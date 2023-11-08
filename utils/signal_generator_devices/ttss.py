import time

import tektronix_func_gen as tfg

# with tfg.FuncGen('USB::0x0699::0x0353::2136516::INSTR') as fgen:
#       # fgen.write()
#       # fgen.ch2.set_function("SIN")
#       fgen.ch2.set_frequency(200, unit="KHz")
#       # fgen.ch1.set_offset(50, unit="mV")
#       # fgen.ch2.set_amplitude(0.002)
#       # print(fgen.ch2.get_settings())
#       fgen.ch2.set_duty(0.1)
#       # print(fgen.ch2.get_duty())
#
#       # fgen.ch1.set_output("ON")
#       # fgen.ch2.set_output("OFF")
#       # alternatively fgen.ch1.print_settings() to show from one channel only
#       # fgen.fgen.ch2.set_function("SIN")

with tfg.FuncGen('USB0::0x0699::0x0353::2310317::INSTR') as fgen:
        fgen.ch1.set_frequency(180, unit="KHz")
        fgen.ch1.set_duty(40)
        time.sleep(1)
        fgen.ch1.set_frequency(100, unit="KHz")
        fgen.ch1.set_duty(50)
        time.sleep(1)
        fgen.ch1.set_frequency(190, unit="KHz")
        fgen.ch1.set_duty(70)
        time.sleep(1)