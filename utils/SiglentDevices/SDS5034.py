"""
    Communication with the SDS5034X Digital Oscilloscope from Siglent over ethernet
    Derek Fujimoto
    March 2023

    See manual for SCPI command list and other examples:
        https://siglentna.com/wp-content/uploads/dlm_uploads/2022/07/SDS_ProgrammingGuide_EN11C-2.pdf
"""

from . import SiglentBase
import numpy as np
import pandas as pd
# import matplotlib.pyplot as plt
import struct, math


class SDS5034(SiglentBase):
    """Control siglent digital oscilloscope and read waveforms

        Attributes:

            HORI_NUM (int): Number of horizontal divisions
            preambles (dict): preamble values, saved when measured
            sds (pyvisa resource): allows write/read/query to the device
            TDIV_ENUM (list): time division values from table 2 of https://siglentna.com/wp-content/uploads/dlm_uploads/2022/07/SDS_ProgrammingGuide_EN11C-2.pdf (page 559)
            waveforms (pd.DataFrame): waveform data in volts (includes all channels)
    """

    # global variables

    HORI_NUM = 10

    # see table 2 from https://siglentna.com/wp-content/uploads/dlm_uploads/2022/07/SDS_ProgrammingGuide_EN11C-2.pdf
    # page 559

    TDIV_ENUM = (
        200e-12,
        500e-12,
        1e-9,
        2e-9,
        5e-9,
        10e-9,
        20e-9,
        50e-9,
        100e-9,
        200e-9,
        500e-9,
        1e-6,
        2e-6,
        5e-6,
        10e-6,
        20e-6,
        50e-6,
        100e-6,
        200e-6,
        500e-6,
        1e-3,
        2e-3,
        5e-3,
        10e-3,
        20e-3,
        50e-3,
        100e-3,
        200e-3,
        500e-3,
        1,
        2,
        5,
        10,
        20,
        50,
        100,
        200,
        500,
        1000,
    )

    def __init__(self, hostname='169.254.239.195'):
        """ Init.

        Args:
            hostname (str): ip address or DNC lookup of device
        """

        # setup
        super().__init__(hostname=hostname)

        # set chunk size for communication
        self.sds.chunk_size = 20 * 1024 * 1024

        # set data storage
        self.preambles = {}
        self.waveforms = pd.DataFrame()

    # simple basic commands
    def default(self):
        """Resets the oscilloscope to the default configuration, equivalent to the Default button on the front panel.
        """
        self.write('*RST')

    def reboot(self):
        """Restart the scope."""
        self.write('SYSTem:REBoot')

    def run(self):
        """Start taking data, equivalent to pressing the Run button on the front panel."""
        self.write('ACQuire:STATE RUN')

    def stop(self):
        """Stop taking data, equivalent to pressing the Stop button on the front panel."""
        self.write('ACQuire:STATE STOP')

    # simple queries
    """
    示波器的ADC分辨率指的是模数转换器（Analog-to-Digital Converter，简称ADC）对输入信号进行数字化转换时所能表示的精度。它表示ADC将连续模拟信号转换成离散数字信号时所能区分的最小电压或电平变化。
    ADC分辨率通常以位（bit）为单位进行表示。较高的分辨率意味着ADC能够更准确地将模拟信号离散化为数字信号，从而提供更精确的测量结果。
    例如，一个8位的ADC具有256个离散化的电平值，而一个12位的ADC则具有4096个电平值。因此，12位的ADC比8位的ADC具有更高的分辨率。
    示波器的ADC分辨率在很大程度上决定了其测量精度和信号分辨能力。较高的分辨率使得示波器能够显示细微的信号细节，尤其在观察小信号或
    """

    def get_adc_resolution(self):
        """Returns:
            int: number of bits 8|10
        """
        return int(self.query('ACQuire:RESolution?').replace('Bits', ''))

    """
    在示波器中，"ch_coupling"（通道耦合）是指示波器输入通道的耦合模式或耦合选项。通道耦合用于选择输入信号的耦合方式，以便适应不同类型的信号和测量需求。
    主要的通道耦合模式通常包括以下两种：
    AC耦合（AC Coupling）：
    在AC耦合模式下，示波器会过滤掉信号中的直流成分，只显示交流信号的波形。这样做可以将信号的基准线移动到屏幕中央，从而更好地观察信号的变化情况。AC耦合适用于观察交流信号，例如信号频率高于几十赫兹的波形。
    DC耦合（DC Coupling）：
    在DC耦合模式下，示波器会显示信号的全部频率分量，包括直流成分。这种模式适用于观察包含直流偏置或低频成分的信号。在DC耦合模式下，示波器不会过滤掉信号的直流分量，因此直流偏置也会显示在波形上。
    根据被测信号的特性和测量需求，你可以在示波器上选择AC耦合或DC耦合模式。对于测量交流信号或需要移除直流偏置的情况，使用AC耦合模式是合适的。而对于需要观察直流偏置或低频信号的情况，使用DC耦合模式更为适用。示波器通常会提供在通道菜单中切换这两种耦合模式的选项。
    """

    def get_ch_coupling(self, ch):
        """Args:
            ch (int): channel number

        Returns:
            str: DC|AC|GND
            直流|交流|地
        """
        return self.query(f'CHANnel{int(ch)}:COUPling?')

    """
    在示波器中，"ch_impedance"（通道阻抗）指的是示波器输入通道的输入阻抗。通道阻抗是指示波器在测量电压信号时对电路的负载影响程度。通常用欧姆（Ω）表示。
    示波器的通道阻抗通常有两种标准值：1兆欧姆（1MΩ）和50欧姆（50Ω）。这两种阻抗选项在不同的测量场景中有不同的用途。
    1兆欧姆通道阻抗：
    大多数示波器的高阻抗输入通道都是1兆欧姆，通常用于测量高阻抗电路，例如常见的逻辑电路、模拟电路、传感器输出等。高阻抗输入通道对被测电路的负载影响较小，不会明显地改变电路的特性。
    50欧姆通道阻抗：
    50欧姆通道主要用于高频信号的测量，例如射频（RF）信号。在高频情况下，示波器的高阻抗输入可能会引入较大的反射和信号失真。因此，使用50欧姆输入阻抗可以有效地匹配被测电路的输出阻抗，减少反射，提高测量的准确性。
    选择适当的通道阻抗对于测量结果的准确性非常重要。通常在示波器上，你可以根据实际测量需求，在通道菜单或设置中选择相应的通道阻抗，以确保测量结果准确且不影响被测电路的性能。
    """

    def get_ch_impedance(self, ch):
        """Args:
            ch (int): channel number

        Returns:
            str: 1M|50 (1 MOhm or 50 Ohms)
            电阻 1M欧姆|50欧姆
        """

        response = self.query(f'CHANnel{int(ch)}:IMP?').strip()

        if response == 'ONEMeg':
            return '1M'
        elif response == 'FIFTy':
            return '50'
        else:
            raise RuntimeError(f'Unexpected device response "{response}"')

    """
    在示波器中，"offset"（偏置）是指调整示波器显示波形位置的参数。它允许你在屏幕上上下移动波形，以便更好地查看信号的特定部分或使波形位于合适的位置。
    示波器通常会显示一个水平基准线，表示为零电平或地线。在没有偏置的情况下，信号波形将在基准线上显示。但是，有时信号可能不在基准线上，这可能是由于信号存在直流偏置或其他原因。为了将信号合适地显示在屏幕上，可以使用示波器的偏置功能。
    偏置功能允许你通过增加或减少基准线的电压来垂直移动波形。通过向上或向下调整波形的位置，你可以将感兴趣的信号部分置于屏幕的中心或其他合适的位置，从而更清晰地观察信号的波形特征。
    注意，示波器的偏置功能通常是针对直流信号或直流偏置的调整，并不影响信号的交流部分。偏置通常用于直流耦合模式（DC耦合）下的信号观察，而在交流耦合模式（AC耦合）下，示波器会自动将信号偏置移到基准线附近。
    """

    def get_ch_offset(self, ch):
        """Args:
                ch (int): channel number

            Returns:
                float: Offset in volts
        """
        return float(self.query(f'CHANnel{int(ch)}:OFFS?').strip())

    """
    在示波器中，"ch_probe"（通道探头）是一种连接到示波器输入通道上的测量探头。通道探头用于将被测电路的信号连接到示波器，使示波器能够显示和测量电压信号的波形。
    通常情况下，示波器的输入通道是通过BNC接头来连接通道探头的。通道探头的另一端则连接到被测电路上。探头通过插入到被测电路中，可以非侵入性地获取电压信号，使得示波器能够观察和分析电路的波形特征。
    通道探头的设计通常考虑以下几个方面：
    阻抗匹配：通道探头应该与示波器的输入通道阻抗匹配，以确保测量的准确性和避免信号反射。
    带宽：通道探头的带宽决定了它可以传递多高频率的信号。带宽越高，探头可以测量的高频信号越多。
    补偿：一些高级的通道探头具有可调的补偿功能，可以用来校正探头的响应，以保证测量的精度。
    放大倍数：某些通道探头可能具有可调的放大倍数，用于调整测量范围。
    示波器通常会配备至少两个输入通道，因此你可以使用多个通道探头同时测量不同的信号或观察不同的波形。在选择通道探头时，应该考虑被测信号的特性和测量需求，选择适合的探头类型以获得准确和可靠的测量结果。
    """

    def get_ch_probe(self, ch):
        """Args:
                ch (int): channel number

            Returns:
                float: probe attenuation factor
        """
        return float(self.query(f'CHANnel{int(ch)}:PROBe?').strip())

    """
    在示波器中，"ch_scale"（通道刻度）指的是示波器输入通道的垂直缩放设置。通道刻度用于调整示波器屏幕上波形的垂直尺度，以便更好地观察和测量输入信号的振幅。
    通道刻度通常以电压为单位进行表示，例如每格代表1伏特（1V）、0.1伏特（0.1V）等等。示波器屏幕通常会有一个垂直标尺，显示每个小格表示的电压值。
    通过调整通道刻度，你可以将信号的振幅放大或缩小，使波形在示波器屏幕上适合观察。较小的刻度值可以放大波形，使细微的信号变化更明显可见。较大的刻度值可以缩小波形，使整个信号波形在屏幕上完整可见。
    示波器通常还具有自动刻度功能，可以根据输入信号的振幅自动调整通道刻度，以确保波形能够适合屏幕显示，且不会超出范围而导致波形截断。
    在进行测量时，根据被测信号的振幅范围和观察要求，你可以通过示波器控制面板或菜单调整通道刻度，以获得最佳的波形显示效果。
    """

    def get_ch_scale(self, ch):
        """
            Returns the current vertical sensitivity of the specified channel (volts/div).

            Args:
                ch (int): channel number

            Returns:
                float: vertical sensitivity in volts/div
        """
        return float(self.query(f'CHANnel{int(ch)}:SCALe?').strip())

    """
    通到状态
    """

    def get_ch_state(self, ch):
        """Args:
                ch (int): channel number

            Returns:
                bool: True if channel is on. False if channel is off
        """
        state = self.query(f'CHANnel{int(ch)}:SWITch?')

        return state.strip().upper() == 'ON'

    """
    测试电流，可能需要电流钳，电流探头
    """

    def get_ch_unit(self, ch):
        """Args:
                ch (int): channel number

            Returns:
                str: the unit of the channel V|A
        """
        return self.query(f'CHANnel{int(ch)}:UNIT?')

    def get_id(self):
        """Returns:
                str: id of device
        """
        return self.query('*IDN?')

    def get_run_state(self):
        """Returns:
                bool: True if run. False if Stop
        """
        return bool(int(self.query('ACQ:STATE?')))

    def get_sequence(self):
        """Returns:
                bool: True if ON, False if OFF
        """
        return self.query('ACQuire:SEQuence?') == 'ON'

    def get_sequence_count(self):
        """
            Returns the current count setting: number of memory segments to acquire.

            The maximum number of segments may be limited by the memory depth of your oscilloscope.

            Returns:
                int: number of counts, is a power of 2
        """
        return int(self.query('ACQuire:SEQuence:COUNt?').strip())

    """
    "smpl_rate"（采样率）是示波器进行模拟信号数字化转换（ADC）的速率，表示示波器每秒对输入信号进行多少次采样。
    采样率通常以赫兹（Hz）为单位进行表示，即每秒进行的采样次数。较高的采样率意味着示波器能够更频繁地对输入信号进行采样，从而获得更多的样本点，使波形更准确地表示原始信号。
    对于示波器，采样率的选择至关重要，它直接影响到示波器对信号的捕获和显示能力。较高的采样率可以更好地表示高频信号和快速变化的信号，而较低的采样率可能会导致信号失真，尤其是在观察高频信号时。
    当选择示波器时，你应该考虑被测信号的最高频率成分，以及希望获得的波形细节。通常，采样率应该至少是信号最高频率成分的2倍以上，以确保信号能够被适当地还原。
    示波器通常会在产品规格中明确列出其采样率。较高端的示波器通常具有更高的采样率，适用于更广泛的应用和更复杂的信号观察。
    """

    def get_smpl_rate(self):
        """Returns:
                float: sampling rate for fixed sampling rate mode
                float: sampling rate for fixed sampling rate moded
        """
        return float(self.query('ACQuire:SRATe?').strip())

    """
    "time_delay"（时间延迟）在示波器中通常指的是设置示波器触发器以延迟波形显示的功能。时间延迟允许你在时间轴上向左或向右延迟波形的显示，以便更好地观察信号的起始点或特定事件。
    当示波器触发器设置为延迟模式时，示波器会等待触发条件满足后再显示波形。触发条件可以是特定的电压电平、边沿触发、脉冲宽度等。一旦触发条件满足，示波器会将波形的起始点对齐于屏幕的特定位置，并根据设置的时间延迟值显示后续波形。
    时间延迟功能对于观察波形中复杂事件或信号的起始瞬态非常有用。通过设置适当的时间延迟值，你可以将感兴趣的信号部分置于屏幕的中心或其他合适的位置，以便更清晰地观察信号的特征。
    示波器通常提供时间延迟控制选项，你可以通过示波器的控制面板或菜单来设置时间延迟值。根据观察需求和信号特性，你可以灵活地调整时间延迟来获得最佳的波形显示效果和测量准确性。
    """

    def get_time_delay(self):
        """Returns:
                float: delay between the trigger event and the delay reference point on the screen in seconds
        """
        return float(self.query('TIMebase:DELay?').strip())

    """
    "time_scale"（时间刻度）指的是示波器水平轴上时间的缩放设置。时间刻度用于调整示波器屏幕上波形的水平尺度，以便更好地观察信号随时间的变化
    时间刻度通常以时间单位（如秒、毫秒、微秒等）进行表示，例如每格代表1秒（1s）、1毫秒（1ms）等等。示波器屏幕通常会有一个水平标尺，显示每个小格表示的时间值。
    通过调整时间刻度，你可以改变波形在示波器屏幕上的时间跨度。较小的时间刻度值可以放大波形，使信号变化的细节更明显可见。较大的时间刻度值可以缩小波形，使更长的时间段的信号波形在屏幕上完整可见。
    示波器通常还具有自动时间刻度功能，可以根据输入信号的频率自动调整时间刻度，以确保波形能够适合屏幕显示，且不会超出范围而导致波形截断。
    在进行波形观察和测量时，根据信号的变化速率和观察需求，你可以通过示波器控制面板或菜单调整时间刻度，以获得最佳的波形显示效果和测量精度。
    """

    def get_time_scale(self):
        """Returns:
                float: horizontal scale in seconds/div
        """
        return float(self.query('TIMebase:SCALe?').strip())

    """
    auto|normal|single
    """

    def get_trig_mode(self):
        """Returns:
            str: trigger mode (auto|normal|single)
        """
        return self.query('TRIGger:MODE?').lower()

    """
    "trig_state"（触发状态）是指示波器触发器是否处于启用或禁用状态的设置。触发器是示波器中非常重要的功能，用于帮助捕获稳定的波形并在屏幕上显示。
    Arm|Ready|Auto|Trig'd|Stop|Roll
    """

    def get_trig_state(self):
        """Returns:
            str: trigger state (Arm|Ready|Auto|Trig'd|Stop|Roll).
        """
        return self.query('TRIGger:STATus?')

    """
    Int:要从示波器传输的波形对应的通道号
    """

    def get_wave_ch(self):
        """Returns:
            int: channel number corresponding to waveform to be transferred from the oscilloscope
        """
        return int(self.query('WAVeform:SOURce?')[1])

    """
    "wave_startpt"（波形起始点）是指示波器屏幕上波形显示的起始位置的设置。在示波器屏幕上显示的波形通常是一个有限的波形窗口，而波形起始点指示了波形窗口中的起始位置
    通过调整波形起始点，你可以改变示波器屏幕上波形显示的水平位置。将波形起始点向右移动可以将更早的信号部分显示在屏幕中，而将波形起始点向左移动可以将更晚的信号部分显示在屏幕中。
    波形起始点的设置对于观察信号的特定部分非常有用。当你对信号的特定时刻或事件感兴趣时，通过调整波形起始点，你可以将感兴趣的信号部分置于屏幕的中心或其他合适的位置，从而更清晰地观察信号的特征。
    示波器通常提供波形起始点的控制选项，你可以通过示波器的控制面板或菜单来设置波形起始点。根据观察需求和信号特性，你可以灵活地调整波形起始点来获得最佳的波形显示效果和测量准确性。
    """

    def get_wave_startpt(self):
        """Returns:
            int: the starting index of the data for waveform transfer.
        """
        return int(self.query('WAVeform:STARt?').strip())

    """
    "wave_interval"（波形间隔）是指示波器屏幕上显示的两个波形之间的时间间隔的设置。在示波器屏幕上同时显示多个波形时，波形间隔指示了相邻波形之间的时间间隔。
    通过调整波形间隔，你可以改变示波器屏幕上多个波形的水平位置和密度。较小的波形间隔值意味着波形之间更紧密，可以同时显示更多的波形，而较大的波形间隔值意味着波形之间更宽松，每个波形占用更大的空间。
    波形间隔的设置对于同时比较多个信号或监测不同波形特征非常有用。通过适当调整波形间隔，你可以在示波器屏幕上同时显示多个波形，并对它们进行比较和分析。
    示波器通常提供波形间隔的控制选项，你可以通过示波器的控制面板或菜单来设置波形间隔。根据观察需求和信号特性，你可以灵活地调整波形间隔来获得最佳的波形显示效果和测量准确性。
    """

    def get_wave_interval(self):
        """Returns:
            int: the interval between data points for waveform transfer.
        """
        return int(self.query('WAVeform:INTerval?'))

    """
    "wave_npts"（波形数据点数）是指示示波器在屏幕上显示的波形中包含的数据点数量。波形数据点数表示示波器在水平方向上采集和显示的数据点数量。
    示波器通过采样输入信号并将其转换为数字数据来生成波形。每个波形数据点代表一个离散的采样值，示波器根据这些数据点在屏幕上绘制波形。
    波形数据点数影响示波器屏幕上波形的水平分辨率。较多的数据点数意味着示波器在水平方向上有更多的细节，波形显示更加精细。较少的数据点数则可能导致波形显示不够平滑，特别是当观察高频信号时可能会产生
    通常，示波器具有可调的数据点数设置，你可以根据需要选择合适的数据点数来获得最佳的波形显示效果。对于较复杂的信号或需要更精细的观察和分析的情况，使用较多的数据点数可能更为合适。但是，较多的数据点数也会增加示波器处理和显示的负担，因此需要平衡显示效果和性能要求。
    """

    def get_wave_npts(self):
        """Returns:
            float: the number of waveform points to be transferred
        """
        return float(self.query('WAVeform:POINt?').strip())

    """
    "wave_maxpt"（波形最大数据点数）是指示示波器能够采集和显示的波形数据点数的最大限制。波形最大数据点数表示示波器在水平方向上能够捕获和显示的最大样本数量。
    示波器在捕获波形时，会以一定的采样率对输入信号进行模拟信号数字化转换（ADC），将连续的模拟信号转换为离散的数字信号。每个数据点代表一个离散的采样值。
    波形最大数据点数是示波器硬件和性能的一个限制。较高端的示波器通常具有更大的波形最大数据点数，因为它们具备更强大的处理能力和存储容量，能够处理更多的样本数据。
    选择适当的波形最大数据点数取决于你的测量需求和所观察的信号特性。如果你需要观察长时间的信号波形或捕获高频信号的细节，较大的波形最大数据点数可能更为合适。但要注意，较大的数据点数会占用更多的存储空间和增加示波器的处理负担。
    当波形数据点数达到波形最大数据点数时，示波器可能会自动进行数据压缩或丢弃数据，以适应其最大限制。因此，为了确保测量的准确性，最好选择符合测量需求的适当波形最大数据点数。
    """

    def get_wave_maxpt(self):
        """Returns:
            float: the maximum points of one piece, when it needs to read the waveform data in pieces.
        """
        return float(self.query('WAVeform:MAXPoint?').strip())

    """
    "wave_width"（波形宽度）通常指示示波器屏幕上显示的波形的宽度。波形宽度表示波形在水平方向上占据的屏幕像素数量或单位。
    波形宽度决定了示波器屏幕上显示的波形水平尺寸。较宽的波形意味着波形显示在屏幕上占据更多的水平空间，使得波形更宽大，可以更清晰地观察波形特征和细节。较窄的波形则意味着波形在屏幕上占据较少的水平空间，使得波形显示较小，可以同时在屏幕上显示更多的波形。
    示波器通常提供波形宽度的调整选项，你可以通过示波器的控制面板或菜单来设置波形宽度。调整波形宽度可以根据观察需求和波形特性，以获得最佳的波形显示效果和测量准确性。
    在进行波形观察和测量时，选择适当的波形宽度可以帮助你更好地观察和分析信号的特征，并确保波形显示在屏幕上不过度挤压或过于扩展。
    """

    def get_wave_width(self):
        """Returns:
            str: output format for the transfer of waveform data (byte|word).
        """
        return self.query('WAVeform:WIDTh?').lower()

    # simple commands
    def set_adc_resolution(self, bits):
        """Set the number of bits used in data acquisition

        Args:
            bits (int): 8|10
        """
        if bits not in (8, 10):
            raise RuntimeError(f'Input bits must be 8 or 10, not "{bits}"')

        state = self.get_run_state()
        self.run()
        self.write(f'ACQuire:RESolution {bits}B')
        if not state:
            self.stop()

    # 直流交流
    def set_ch_coupling(self, ch, mode):
        """Selects the coupling mode of the specified input channel.

        Args:
            ch (int): channel number
            mode (str): DC|AC|GND
        """
        mode = mode.upper()
        assert mode in ('DC', 'AC',
                        'GND'), 'mode must be one of DC, AC, or GND'
        self.write(f'CHANnel{int(ch)}:COUPling {mode}')

    # 电阻
    def set_ch_impedance(self, ch, z):
        """Sets the input impedance of the selected channel.
            There are two impedance values available. They are 1M and 50.

        Args:
            ch (int): channel number
            z (str):  1M|50
        """
        z = str(z).upper()

        if z == '1M':
            self.write(f'CHANnel{int(ch)}:IMP ONEMeg')
        elif z == '50':
            self.write(f'CHANnel{int(ch)}:IMP FIFTy')
        else:
            raise RuntimeError('z must be one of "1M" or "50"')

    # 按电压偏移
    def set_ch_offset(self, ch, offset):
        """Set vertical offset of the channel.

            The maximum ranges depend on the fixed sensitivity setting.
            The range of legal values varies with the value set by self.set_ch_vscale

        Args:
            ch (int): channel number
            offset (float): offset value in volts
        """
        return self.write(f'CHANnel{int(ch)}:OFFSet {offset:g}')

    def set_ch_probe(self, ch, attenuation=None):
        """Specifies the probe attenuation factor for the selected channel.

            This command does not change the actual input sensitivity of the oscilloscope.
            It changes the reference constants for scaling the  display factors, for making
            automatic measurements, and for setting trigger levels.

        Args:
            ch (int): channel number
            attenuation (float|None): if none, set to default (1X); else should be a float
        """
        if attenuation is None:
            self.write(f'CHANnel{int(ch)}:PROBe DEFault')
        else:
            assert 1e-6 < attenuation < 1e6, 'Attenuation out of bounds: (1e-6, 1e6)'
            self.write(f'CHANnel{int(ch)}:PROBe VALue {attenuation:g}')

    def set_ch_scale(self, ch, scale):
        """Sets the vertical sensitivity in Volts/div.

            If the probe attenuation is changed, the scale value is multiplied by the probe's
            attenuation factor.

        Args:
            ch (int): channel number
            scale (float): vertical scaling
        """
        return self.write(f'CHANnel{int(ch)}:SCALe {scale:g}')

    def set_ch_state(self, ch, on):
        """Turns the display of the specified channel on or off.

        Args:
            ch (int): channel number
            on (bool): if True, turn channel on. If False turn channel off.
        """
        state = 'ON' if on else 'OFF'
        self.write(f'CHANnel{int(ch)}:SWITch {state}')

    def set_ch_unit(self, ch, unit):
        """Changes the unit of input signal of specified channel: voltage (V) or current (A)

        Args:
            ch (int): channel number
            unit (str): V|A for volts or amps
        """
        unit = unit.upper()
        assert unit in ('V', 'A'), 'unit must be one of "V" or "A"'
        self.write(f'CHANnel{int(ch)}:UNIT {unit}')

    """
    启动/停止采集数据，相当于按下前面板上的运行/停止按钮
    """

    def set_run_state(self, run):
        """Start/Stop taking data, equivalent to pressing the Run/Stop button on the front panel.

        Args:
            run (bool): if True, RUN. If False, STOP
        """
        if run:
            self.run()
        else:
            self.stop()

    def set_sequence(self, state):
        """Enables or disables sequence acquisition mode.

        Args:
            state (bool): If True, sequence on. If False, sequence off.
        """
        if state:
            self.write('ACQuire:SEQuence ON')
        else:
            self.write('ACQuire:SEQuence OFF')

    def set_sequence_count(self, value):
        """Sets the number of memory segments to acquire.

        The maximum number of segments may be limited by the memory depth of your oscilloscope.

        Args:
            value (int): count setting, must be a power of two
        """
        if value % 2 != 0:
            raise RuntimeError(f'Input {value} must be a power of 2')

        self.write(f'ACQuire:SEQuence:COUNt {int(value)}')

    def set_smpl_rate(self, rate):
        """Sets the sampling rate when in the fixed sampling rate mode.

        Args:
            rate (float|str): sample rate in pts/sec or "auto"
        """

        if str(rate) in 'auto':
            self.write('ACQuire:MMANagement AUTO')
        else:
            self.write('ACQuire:MMANagement FSRate')
            self.write(f'ACQuire:SRATe {rate:g}')

    def set_time_delay(self, delay):
        """Specifies the main timebase delay.

            This delay is the time between the trigger event and the delay reference
            point on the screen

        Args:
            delay (float): delay in seconds between the trigger event and the delay reference
            point on the screen
        """
        self.write(f'TIMebase:DELay {float(delay):E}')

    def set_time_scale(self, scale):
        """Sets the horizontal scale per division for the main window.

            Due to the limitation of the expansion strategy, when the time
            base is set from large to small, it will automatically adjust to
            the minimum time base that can be set currently.

        Args:
            scale (float): seconds per division
        """
        self.write(f'TIMebase:SCALe {scale:E}')

    def set_trig_mode(self, mode):
        """Sets the mode of the trigger.

        Args:
            mode (str): single|normal|auto
        """

        mode = mode.lower()

        if mode in 'single':
            self.write('TRIGger:MODE SINGle')
        elif mode in 'normal':
            self.write('TRIGger:MODE NORMal')
        elif mode in 'auto':
            self.write('TRIGger:MODE AUTO')
        else:
            raise RuntimeError(
                "mode must be one of 'single', 'normal', or 'auto'")

    def set_trig_state(self, state):
        """Set trigger state

        Args:
            state (str): RUN|STOP
        """
        if state.upper() in 'RUN':
            self.write('TRIGger:RUN')
        elif state.upper() in 'STOP':
            self.write('TRIGger:STOP')
        else:
            raise RuntimeError('Bad state input, should be one of RUN or STOP')

    def set_wave_ch(self, ch):
        """Specifies the source waveform to be transferred from the oscilloscope

        Args:
            ch (int): channel number
        """
        self.write(f'WAVeform:SOURce C{int(ch)}')

    def set_wave_startpt(self, pt):
        """Args:
            pt (int): index of starting data point for waveform transfer
        """
        self.write(f'WAVeform:STARt {int(pt)}')

    def set_wave_interval(self, interval):
        """Args:
            interval (int): interval between data points for waveform transfer
        """
        self.write(f'WAVeform:INTerval {int(interval)}')

    def set_wave_npts(self, npts):
        """Args:
            npts (int): number of waveform points to be transferred
        """
        self.write(f'WAVeform:POINt {int(npts)}')

    def set_wave_width(self, format):
        """Sets the current output format for the transfer of waveform data.

        Args:
            format (str): byte|word
        """
        format = format.upper()
        if format in 'BYTE':
            self.write('WAVeform:WIDTh BYTE')
        elif format in 'WORD':
            self.write('WAVeform:WIDTh WORD')

    # 获取测量值
    def get_measurement_item_value(self, n):
        return self.query(f'MEAS:ADV:P{n}:VAL?')

    #截图
    def get_screenshot(self, na):
        try:
            s = self.query(f'SAVE:IMAGe "U-disk0/SIGLENT/{na}.png",PNG,ON')
            # return self.query(f'SAVE:IMAGe "U-disk0/SIGLENT/{na}.png",PNG,ON')
        except Exception as e:
            return 0

    # 测量
    def set_measurement_item(self, lst_measurement=None):
        var = {
            '峰峰值': 'PKPK',
            '最大值': 'MAX',
            '最小值': 'MIN',
            '幅值': 'AMPL',
            '顶端值': 'TOP',
            '低端值': 'BASE',
            'L@T': 'LEVELX',
            '周期平局值': 'CMEAN',
            '平均值': 'MEAN',
            '标准差': 'STDEV',
            '周期标准差': 'VSTD',
            '均方根': 'RMS',
            '周期均方根': 'CRMS',
            '中位数': 'MEDIAN',
            '周期中位数': 'CMEDIAN',
            '下降过激': 'OVSN',
            '下降前激': 'FPRE',
            '上升过激': 'OVSP',
            '上升前激': 'RPRE',
            '周期': 'PER',
            '频率': 'FREQ',
            '最大值时间': 'TMAX',
            '最小值时间': 'TMIN',
            '正脉宽': 'PWID',
            '负脉宽': 'NWID',
            '正占空比': 'DUTY',
            '负占空比': 'NDUTY',
            '正脉冲串宽度': 'WID',
            '负脉冲串宽度': 'NBWID',
            '延时': 'DELAY',
            'T@M': 'TIMEL',
            '上升时间': 'RISE',
            '下降时间': 'FALL',
            '10-90%上升时间': 'RISE10T90',
            '90-10%下降时间': 'FALL90T10',
            '相邻周期抖动': 'CCJ',
            '直流正面积': 'PAREA',
            '直流负面积': 'NAREA',
            '直流有效面积': 'AREA',
            '直流绝对面积': 'ABSAREA',
            '周期数': 'CYCLES',
            '上升沿个数': 'REDGES',
            '下降沿个数': 'FEDGES',
            '边沿总数': 'EDGES',
            '正脉冲数': 'PPULSES',
            '负脉冲数': 'NPULSES',
            '相位': 'PHA',
            '时滞': 'SKEW',
            'FRFR': 'FRR',
            'FRFF': 'FRF',
            'FFFR': 'FFR',
            'FFFF': 'FFF',
            'FRLR': 'LRR',
            'FRLF': 'LRF',
            'FFLR': 'LFR',
            'FFLF': 'LFF',
            '交流正面积': 'PACArea',
            '交流负面积': 'NACArea',
            '交流有效面积': 'ACArea',
            '交流绝对面积': 'ABSACArea',
            '上升沿斜率': 'PSLOPE',
            '下降沿斜率': 'NSLOPE',
            'TSU@R': 'TSR',
            'TSU@F': 'TSF',
            'TH@R': 'THR',
            'TH@F': 'THF'
        }

        if not lst_measurement:
            lst_measurement = [
                '周期', '幅值', '频率', '正占空比', '正脉宽', '最大值', '最小值', '顶端值', '低端值',
                '上升沿斜率', '下降沿斜率'
            ]
        # n = 0
        # for measurement_mode in lst_measurement:
        #     if n < 12:
        #         self.write(f':MEASure:ADVanced:P{n + 1}:TYPE {var[measurement_mode]}')
        #     n += 1
        for n in range(len(lst_measurement)):
            self.write(
                f':MEASure:ADVanced:P{n + 1}:TYPE {var[lst_measurement[n]]}')

    # read waveform commands
    def get_wave_preamble(self, ch=None):
        """
        获取指定通道波形数据的序文(字典，键值见下文)

        参数:
        ch (int|None):通道号。如果无，则使用当前设置通道

        返回:
        Dict:通道特定的作用域设置
        Adc_bit: adc的字节数
        Bandwidth:带宽限制。跑，20米，200米
        通道:波源id
        Code_per_div:该值对于不同的垂直增益不同
        模型
        耦合:垂直耦合。直流，交流，地
        Comm_type:由远程命令comm_format选择
        Comm_order:由远程命令comm_format选择
        Data_bytes:第一个简单数据数组的字节长度。在传播的
        波形，表示所传输的字节数
        参数为:波形:点远程命令和
        使用的格式(参见comm_type)。仅适用于模拟信道。
        Data_first_pt:相对于跟踪缓冲区开始的偏移量。
        取值与“波形:远程启动”的参数相同
        命令。
        Data_interval:波形传输数据点之间的间隔。
        取值与“波形:间隔远程”的参数相同
        命令。
        Data_npts:数据数组中数据点的个数。仅适用于模拟信道。
        当序列开启时，该值表示单个点的个数
        序列帧。
        描述符:描述符名称。它是字符串，前8个字符总是
        “WAVEDESC”
        fixed_v_gain:固定垂直增益。这是枚举的垂直刻度。
        这个值并不直观，通常是垂直比例尺
        用地址156~159的值表示
        Frame_index:参数设置的序列的指定帧索引
        & lt; value1&gt;波形:序列。默认值为1
        instrum_name:字符串，始终为“Siglent SDS”。
        probe_attenten:探针衰减因子
        Read_frames:这次传输的序列帧数。用于计算
        序列波形的读取次数
        sample_interval:横向间隔。时域波形的采样间隔。
        水平间隔= 1/采样率
        Sum_frames:获取的序列帧数。用于计算读数
        序列波形次数
        T_delay_s:水平偏移量。的第一次扫描的触发偏移量
        触发，从触发到第一个数据点之间的秒数。
        单位为s。
        t_per_div: time_base。这是枚举的时间/div。
        Template:模板名称。它是字符串，前7个字符总是" WAVEACE "。
        V_offset:探头衰减后的垂直偏移值
        V_offset_raw:不考虑探针衰减的垂直偏移值
        V_per_div:探头衰减后的垂直尺度值。
        V_per_div_raw:不考虑探针衰减的垂直刻度值。
        wave_desc_bytes: wave_desc块的字节长度。(346)

        """
        """Get preamble for waveform data of specified channel (dict, see below for key values)

        Args:
            ch (int|None): channel number. If None, use current set channel

        Returns:
            dict: channel-specific scope settings
                adc_bit:        number of bytes in adc
                bandwidth:      bandwidth limit. OFF, 20M, 200M
                channel:        wave source id
                code_per_div:   the value is different for different vertical gain of different
                                models
                coupling:       vertical coupling. DC, AC, GND
                comm_type:      chosen by remote command comm_format
                comm_order:     chosen by remote command comm_format
                data_bytes:     length in bytes of 1st simple data array. In transmitted
                                waveform, represent the number of transmitted bytes in accordance
                                with the parameter of the :WAVeform:POINt remote command and the
                                used format (see comm_type). Only for analog channels.
                data_first_pt:  indicates the offset relative to the beginning of the trace buffer.
                                Value is the same as the parameter of the :WAVeform:STARt remote
                                command.
                data_interval:  indicates the interval between data points for waveform transfer.
                                Value is the same as the parameter of the :WAVeform:INTerval remote
                                command.
                data_npts:      number of data points in the data array. Only for analog channels.
                                When sequence is on, this value means the points number of single
                                sequence frame.
                descriptor:     descriptor name. It is string, the first 8 chars are always
                                “WAVEDESC”
                fixed_v_gain:   Fixed vertical gain. This is the enumerated vertical scale.
                                This value is not intuitive, and the vertical scale is usually
                                represented by the value of address 156~159
                frame_index:    the specified frame index of sequence set by the parameter
                                <value1> of the command :WAVeform:SEQuence. Default Value is 1
                instrum_name:   string, always “Siglent SDS”.
                probe_atten:    probe attenuation factor
                read_frames:    number of sequence frames transferred this time. Used to calculate
                                the reading times of sequence waveform
                sample_interval:horizontal interval. Sampling interval for time domain waveforms.
                                Horizontal interval = 1/sampling rate
                sum_frames:     number of sequence frames acquired. Used to calculate the reading
                                times of sequence waveform
                t_delay_s:      horizontal offset. Trigger offset for the first sweep of the
                                trigger, seconds between the trigger and the first data point.
                                Unit is s.
                t_per_div:      time_base. This is the enumerated time/div.
                template:       template name. It is string, the first 7 chars are always “WAVEACE”.
                v_offset:       the value of vertical offset with probe attenuation
                v_offset_raw:   the value of vertical offset without probe attenuation
                v_per_div:      the value of vertical scale with probe attenuation.
                v_per_div_raw:  the value of vertical scale without probe attenuation.
                wave_desc_bytes:length in bytes of block WAVEDESC. (346)
        """

        # set channel
        if ch is not None:
            self.set_wave_ch(ch)

        # read preamble
        self.write("WAV:PREamble?")
        recv_all = self.read_bytes(350)
        recv = recv_all[recv_all.find(b'#') + 11:]

        # convert to data
        preamble = {}

        # descriptor name. It is string, the first 8 chars are always “WAVEDESC”
        desc = (struct.unpack('s', recv[i:i + 1])[0] for i in range(16))
        desc = (b''.join(desc)).decode()
        preamble['descriptor'] = desc.replace('\x00', '')

        # Template name. It is string, the first 7 chars are always “WAVEACE”.
        desc = (struct.unpack('s', recv[i:i + 1])[0] for i in range(16, 32))
        desc = (b''.join(desc)).decode()
        preamble['template'] = desc.replace('\x00', '')

        # COMM_TYPE. Chosen by remote command comm_format. 0 -byte, 1- word. Default value is 0.
        options = ['byte', 'word']
        preamble['comm_type'] = options[struct.unpack('h', recv[32:34])[0]]

        # COMM_ORDER. Chosen by remote command comm_format. 0- LSB, 1- MSB. Default value is 0.
        options = ['LSB', 'MSB']
        preamble['comm_order'] = options[struct.unpack('h', recv[34:36])[0]]

        # wave_desc_length. Length in bytes of block WAVEDESC. (346)
        preamble['wave_desc_bytes'] = struct.unpack('i', recv[36:40])[0]

        # WAVE_ARRAY_1. Length in bytes of 1st simple data array. In
        # transmitted waveform, represent the number of transmitted bytes in
        # accordance with the parameter of the :WAVeform:POINt remote
        # command and the used format (see COMM_TYPE). Only for analog
        # channel.
        preamble['data_bytes'] = struct.unpack('i', recv[60:64])[0]

        # Instrument name. It is string, always “Siglent SDS”.
        desc = (struct.unpack('s', recv[i:i + 1])[0] for i in range(76, 92))
        desc = (b''.join(desc)).decode()
        preamble['instrum_name'] = desc.replace('\x00', '')

        # Wave array count. Number of data points in the data array. Only for
        # analog channel. When sequence is on, this value means the points
        # number of single sequence frame.
        preamble['data_npts'] = struct.unpack('i', recv[116:120])[0]

        # First point. Indicates the offset relative to the beginning of the trace
        # buffer. Value is the same as the parameter of
        # the :WAVeform:STARt remote command.
        preamble['data_first_pt'] = struct.unpack('i', recv[132:136])[0]

        # Data interval. Indicates the interval between data points for
        # waveform transfer. Value is the same as the parameter of
        # the :WAVeform:INTerval remote command.
        preamble['data_interval'] = struct.unpack('i', recv[136:140])[0]

        # Read_frames, number of sequence frames transferred this time.
        # Used to calculate the reading times of sequence waveform
        preamble['read_frames'] = struct.unpack('i', recv[144:148])[0]

        # sum_frames, number of sequence frames acquired. Used to
        # calculate the reading times of sequence waveform
        preamble['sum_frames'] = struct.unpack('i', recv[148:152])[0]

        # Vertical gain. The value of vertical scale without probe attenuation.
        preamble['v_per_div_raw'] = struct.unpack('f', recv[156:160])[0]

        # Vertical offset. The value of vertical offset without probe attenuation
        preamble['v_offset_raw'] = struct.unpack('f', recv[160:164])[0]

        # code_per_div. The value is different for different vertical gain of different models
        # see page 562 of manual
        preamble['code_per_div'] = struct.unpack('f', recv[164:168])[0]
        if preamble['code_per_div'] > 2**8:
            preamble['code_per_div'] /= 2**4

        # Adc_bit
        preamble['adc_bit'] = struct.unpack('h', recv[172:174])[0]

        # The specified frame index of sequence set by the parameter
        # <value1> of the command :WAVeform:SEQuence. Default Value is 1
        preamble['frame_index'] = struct.unpack('h', recv[174:176])[0]

        # Horizontal interval. Sampling interval for time domain waveforms.
        # Horizontal interval = 1/sampling rate
        preamble['sample_interval'] = struct.unpack('f', recv[176:180])[0]

        # Horizontal offset. Trigger offset for the first sweep of the trigger,
        # seconds between the trigger and the first data point. Unit is s.
        preamble['t_delay_s'] = struct.unpack('d', recv[180:188])[0]

        # Time_base. This is the enumerated time/div.
        preamble['t_per_div'] = self.TDIV_ENUM[struct.unpack(
            'h', recv[324:326])[0]]

        # Vertical coupling. 0-DC,1-AC,2-GND
        options = ['DC', 'AC', 'GND']
        preamble['coupling'] = options[struct.unpack('h', recv[326:328])[0]]

        # Probe attenuation.
        preamble['probe_atten'] = struct.unpack('f', recv[328:332])[0]

        # Fixed vertical gain. This is the enumerated vertical scale. This value
        # is not intuitive, and the vertical scale is usually represented by the
        # value of address 156~159
        preamble['fixed_v_gain'] = struct.unpack('h', recv[332:334])[0]

        # Bandwidth limit. 0-OFF,1-20M,2-200M
        options = ['OFF', '20M', '200M']
        preamble['bandwidth'] = options[struct.unpack('h', recv[334:336])[0]]

        # Wave source. 0-C1,1-C2,2-C3,3-C4
        # Normal command doesn't work?
        # preamble['channel'] = f"C{struct.unpack('h', recv[344:346])[0]}"
        preamble['channel'] = f"C{self.get_wave_ch()}"

        # adjusted vertical values
        preamble[
            'v_per_div'] = preamble['v_per_div_raw'] * preamble['probe_atten']
        preamble[
            'v_offset'] = preamble['v_offset_raw'] * preamble['probe_atten']

        # save
        self.preambles[preamble['channel']] = preamble

        return preamble

    def read_wave_ch(self, ch, start_pt=0):
        """Fetch the waveform data of a single source channel in volts

        Args:
            ch (int): channel number
            start_pt (int): index of starting point

        Returns:
            pd.DataFrame: voltages of single channel, indexed by timestamp
        """

        # setup input
        self.set_wave_startpt(start_pt)
        self.set_wave_ch(ch)

        # set number of points to read from
        points = self.get_wave_npts()
        one_piece_num = self.get_wave_maxpt()

        if points == 0:
            preamble = self.get_wave_preamble()
            points = preamble['data_npts']
            self.set_wave_npts(points)

        if points > one_piece_num:
            self.set_wave_npts(one_piece_num)

        # number of bits used in data read
        nbits = self.get_adc_resolution()
        if nbits > 8:
            self.set_wave_width('WORD')
        else:
            self.set_wave_width('BYTE')

        # read waveform data?
        read_times = math.ceil(points / one_piece_num)
        recv_all = []
        for i in range(0, read_times):
            start = i * one_piece_num
            self.set_wave_startpt(start)
            self.write("WAV:DATA?")
            recv_rtn = self.read_raw()
            recv = list(recv_rtn[recv_rtn.find(b'#') + 11:-2])
            recv_all += recv

        # convert bits to float
        if nbits > 8:
            convert_data = []
            for i in range(0, int(len(recv_all) / 2)):
                data_16bit = recv_all[2 * i + 1] * 256 + recv_all[2 * i]
                data = data_16bit >> (16 - nbits)
                convert_data.append(data)
        else:
            convert_data = recv_all

        # convert ints to volts
        volt_value = []
        for data in convert_data:

            # 12bit-2047, 8bit-127
            if data > pow(2, nbits - 1) - 1:
                data = data - pow(2, nbits)
            else:
                pass
            volt_value.append(data)

        volt_value = np.array(volt_value)

        if nbits == 10:
            volt_value = volt_value / 4

        # read waveform preamble
        preamble = self.get_wave_preamble()
        code = preamble['code_per_div']
        vdiv = preamble['v_per_div']
        offset = preamble['v_offset']
        tdiv = preamble['t_per_div']
        delay = preamble['t_delay_s']
        interval = preamble['sample_interval']

        # adjust voltage values
        volt_value = volt_value / code * vdiv - offset

        # get times
        idx = np.arange(len(volt_value))
        time_value = -delay - (tdiv * self.HORI_NUM / 2) + idx * interval

        # make data frame for output
        df = pd.DataFrame({f'C{ch}': volt_value, 'time_s': time_value})
        df.set_index('time_s', inplace=True)

        # save
        self.waveforms.drop(columns=[f'C{ch}'], errors='ignore', inplace=True)
        self.waveforms = pd.concat((self.waveforms, df), axis='columns')
        output_file = 'data.csv'
        df.to_csv(output_file, index=False)
        return df

    def read_wave_active(self, start_pt=0):
        """Read the waveforms of all active (displayed) analog input channels

        Args:
            start_pt (int): index of starting point to read

        Returns:
            pd.DataFrame: voltages of all active channels, indexed by timestamp
        """

        # stop run state

        self.stop()

        # iterate over all possible channels
        waves = []
        for i in range(1, 5):

            if self.get_ch_state(i):
                waves.append(self.read_wave_ch(i, start_pt=start_pt))

        # make dataframe
        df = pd.concat(waves, axis='columns')

        # save
        self.waveforms.drop(columns=df.columns, errors='ignore', inplace=True)
        self.waveforms = pd.concat((self.waveforms, df), axis='columns')
        output_file = 'data.csv'
        df.to_csv(output_file, index=True)
        print("DataFrame已成功写入CSV文件。")
        return df

    def getdecode(self):
        return self.query('DEC:BUS1:PROT?')

    # def draw_wave(self, ch, ax=None, adjust_ylim=True, **plotargs):
    #     """Draw waveform for single channel, as shown on scope screen
    #
    #         Must read the waveform first
    #
    #     Args:
    #         ch (int): channel number
    #         ax (plt.Axes|None): object to draw in, if none then make new figure
    #         adjust_ylim (bool): if True, change ylim to match scope
    #         plotargs: passed to ax.plot()
    #     """
    #
    #     # import matplotlib.pyplot as plt
    #
    #     # ... (the code snippet you provided)
    #
    #     # Create a figure and axes
    #     fig, ax = plt.subplots()
    #
    #     # Draw the plot
    #     df = self.read_wave_ch(ch=1)
    #     ax.plot(df.index.values, df.values, label=f'CH{ch}', **plotargs)
    #
    #     # Get preamble
    #     pre = self.preambles[f'C{ch}']
    #
    #     # Set plot elements
    #     ax.set_xlabel('Time (s)')
    #     ax.set_ylabel('Voltage (V)')
    #     if adjust_ylim:
    #         ax.set_ylim(-4 * pre['v_per_div'], 4 * pre['v_per_div'])
    #     ax.legend(fontsize='x-small')
    #
    #     # Save the plot to a file (e.g., 'plot.png')
    #     output_file = 'plot.png'
    #     fig.savefig(output_file)
    #
    #     print("Plot saved successfully as:", output_file)
    #
    # def draw_wave_all(self, ax=None, **plotargs):
    #     """Draw all read waveforms, as shown on scope screen
    #
    #         Must read the waveform first
    #
    #     Args:
    #         ax (plt.Axes|None): object to draw in, if none then make new figure
    #         plotargs: passed to ax.plot()
    #     """
    #
    #     if ax is None:
    #         plt.figure()
    #         ax = plt.gca()
    #
    #     for col in self.waveforms:
    #         self.draw_wave(int(col[1]), ax=ax, adjust_ylim=False, **plotargs)


# s = SDS5034('169.254.239.195')
