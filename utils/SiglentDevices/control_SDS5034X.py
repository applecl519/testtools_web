from flask import Flask
from utils.SiglentDevices import SDS5034
app = Flask(__name__)
handler = SDS5034('169.254.52.164')


