from utils.SiglentDevices import SDS5034

handler = SDS5034('192.168.90.105')

# f'SAVE:IMAGe "U-disk0/SIGLENT/{photoname}.png",PNG,ON'


handler.get_screenshot('sdasdas')