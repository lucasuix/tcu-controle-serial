import eel
from modules.serial_communication import SerialCommunication

serial_conn = SerialCommunication("COM1")

@eel.expose
def try_comm(comport):
    serial_conn.comport = comport
    return serial_conn._check_startup(comport)

@eel.expose
def run(comport, command):
    serial_conn.comport = comport
    return serial_conn.read_variable(command)

@eel.expose
def MoverProcBurnIn(comport):
    serial_conn.comport = comport
    serial_conn.tcu_movements(None)

@eel.expose
def testarLeds(comport):
    serial_conn.comport = comport
    serial_conn.testar_leds()

if __name__ == '__main__':

    eel.init('www')
    eel.start('index.html')