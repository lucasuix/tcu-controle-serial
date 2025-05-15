
import serial
import time
from time import sleep
# from utils.error_codes import get_error_message
from datetime import datetime, timedelta

class SerialCommunication:
    def __init__(self, comport):
        self.comport = comport
        self.firmware_file = None
        self.serial_connection = None
        self.error_count = 0

    def _is_connected(self):
        return self.serial_connection is not None and self.serial_connection.is_open
    
    def _connect(self, baudrate=9600):
        if self._is_connected():
            return True
        try:
            self.serial_connection = serial.Serial(self.comport, baudrate=baudrate, bytesize=8, timeout=1.5)
            return True
        except serial.SerialException as e:
            return False
    
    def _disconnect(self):
        if self.serial_connection is not None:
            self.serial_connection.close()
            self.serial_connection = None

    def _check_startup(self, comport):
        self.comport = comport
        self._connect()

        if self.serial_connection is not None:
            self.serial_connection.write("$rBoardVersion\r\n".encode())
            try:
                res = self.serial_connection.read_until().decode()
                self._disconnect()
            except:
                self._disconnect()
                return False
        else:
            return False
        
        return "$ok" in res

    ### MÉTODOS PÚBLICOS

    def read_variable(self, variable):
        self._connect()
        self.serial_connection.write(variable.encode())
        time.sleep(0.1)
        response = self.serial_connection.read_until().decode().rstrip().split(",")[-1]
        print(response)
        self._disconnect()
        return response
    
    def tcu_movements(self, stop_event, minutes=3):
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=minutes)
        angle_readings = []
        try:
            print("Passando para o modo manual")
            self.read_variable("$manual")
            self.read_variable("$stop")
            print("Entrando no loop")
            self.read_variable("$mvE")
            while datetime.now() < end_time:
                time.sleep(0.1)
                try:
                    angle = float(self.read_variable("$rAngInc")) 
                    if angle != angle:
                        raise RuntimeError('Error 202')
                    angle_readings.append(angle)
                    if len(angle_readings) > 5:
                        angle_readings.pop(0)
                        max_angle = max(angle_readings)
                        min_angle = min(angle_readings)
                        # if max_angle - min_angle < 0.8:
                        #     self.error_count = 100
                        #     raise RuntimeError(get_error_message(201))
                except Exception as e:
                    self.error_count += 1
                    time.sleep(0.5)
                    print(e)
                    print(self.error_count)
                    if self.error_count > 20:
                        raise RuntimeError(e)
                    else:
                        continue
                print(angle)
                if angle >= 55:
                    self.read_variable("$mvE")
                    time.sleep(1)
                elif angle <= - 55:
                    self.read_variable("$mvW")
                    time.sleep(1)
            self.read_variable("$stop")
            print("Fim do loop")
        except:
            raise
    
    def testar_leds(self):
        self.read_variable("$ledsOff")
        self.read_variable("$red")
        sleep(1)
        self.read_variable("$red")
        self.read_variable("$green")
        sleep(1)
        self.read_variable("$green")
        self.read_variable("$blue")
        sleep(1)
        self.read_variable("$blue")
        self.read_variable("$ledsOn")