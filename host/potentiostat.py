import serial
import json
import numpy as np


class Potentiostat(serial.Serial):

    MAX_ABS_VOLTAGE = 1.65
    ALLOWED_CURRENT_RANGE = ('1uA', '10uA', '100uA', '1000uA')
    ALLOWED_TEST_NAMES = ['cyclic']
    THROW_AWAY_TIMEOUT = 0.1

    def __init__(self, port):
        port_param = {'port': port, 'baudrate': 115200, 'timeout': 0.5}
        super().__init__(**port_param)
        self.num_throw_away = 10
        self.max_error_count = 10
        self.throw_away_lines()


    def throw_away_lines(self):
        """ 
        Throw away first few lines. Deals with case where user has updated the firmware
        which writes a bunch text to the serial port. 
        """
        timeout = self.timeout
        self.timeout = self.THROW_AWAY_TIMEOUT
        for i in range(self.num_throw_away):
            line = self.readline()
        self.timeout = timeout


    def get_values(self):
        """
        Get current devices values ... connection status, current reading, output voltage,
        reference voltage, current range. 
        """
        msg_dict = {'':''}
        rsp = self.send_and_receive(msg_dict)
        self.error_check_rsp(rsp)
        return rsp


    def averaging(self, num_average):
        """
        Set number of averages used for each measure current value. 
        """
        if num_average <= 0:
            raise ValueError('averaging must be int > 0')
        msg_dict = {'averaging': int(num_average)}
        rsp = self.send_and_receive(msg_dict)
        self.error_check_rsp(rsp)
        return rsp


    def range(self,range_value):
        """
        Set the output current range (uA). Value must be in ALLOW_CURRENT_RANGE list.
        """
        if not range_value in self.ALLOWED_CURRENT_RANGE:
            raise ValueError('range must be in {}'.format(self.ALLOWED_CURRENT_RANGE)) 
        msg_dict = {'range': range_value}
        rsp = self.send_and_receive(msg_dict)
        self.error_check_rsp(rsp)
        return rsp


    def voltage(self,voltage_value):
        """
        Set the output voltage value directly
        """
        if abs(voltage_value) > self.MAX_ABS_VOLTAGE:
            raise ValueError('abs(voltage) must be < {}'.format(self.MAX_ABS_VOLTAGE))
        msg_dict = {'voltage': float(voltage_value)}
        rsp = self.send_and_receive(msg_dict)
        self.error_check_rsp(rsp)
        return rsp


    def connected(self, value):
        """
        Connect/disconnect counter electrode. value=True connects, value=False disconnects.
        """
        msg_dict = {'connected': bool(value)}
        rsp = self.send_and_receive(msg_dict)
        self.error_check_rsp(rsp)
        return rsp


    def offset(self, offset_value):
        """
        Set analog output voltage offset. Used for correcting 
        """
        if abs(offset_value) > self.MAX_ABS_VOLTAGE:
            raise ValueError('abs(offset) must be < {}'.format(self.MAX_ABS_VOLTAGE))
        msg_dict = {'offset': offset_value}
        rsp = self.send_and_receive(msg_dict)
        self.error_check_rsp(rsp)
        return rsp


    def run_test(self, test_name, test_param):
        """
        Run voltametric test. 
        
        test_name  = name of  test
        test_param = dictionary of test parameters. 

        Currently only cyclic voltammetry is implemented.

        run_test('cyclic', test_param)
        
        Example params:
        test_param = {
                'max_voltage'   :  1.5,
                'min_voltage'   : -1.5,
                'scan_rate'     :  0.20,
                'start_voltage' : 'min_voltage',
                'sample_rate'   : 15.0,
                'cycles'        : 2,
                }

        """
        if not test_name in self.ALLOWED_TEST_NAMES:
            raise ValueError('unknown test name {}'.format(test_name))

        msg_dict = {'test': {'name': test_name, 'param': test_param}}
        rsp = self.send_and_receive(msg_dict)
        self.error_check_rsp(rsp)
        tval, volt, curr = self.receive_until_done()
        return tval, volt, curr

    def send_and_receive(self,msg_dict):
        """
        Send and receive message from the device.
        """
        msg_json = f'{json.dumps(msg_dict)}\n'
        self.write(msg_json.encode())
        rsp_json = self.readline()
        rsp_json = rsp_json.strip()
        try:
            rsp_dict = json.loads(rsp_json.decode('utf-8'))
            done = True
        except json.decoder.JSONDecodeError as err:
            rsp_dict = {'error': f'{err}'}
        return rsp_dict


    def receive_until_done(self):
        data_list = []
        while True:
            rsp_json = self.readline()
            rsp_json = rsp_json.strip()
            rsp_dict = json.loads(rsp_json.decode('utf-8'))
            if 'data' in rsp_dict:
                data = rsp_dict['data']
                data_list.append(data)
                data_tuple = float(data['t']), float(data['v']), float(data['i'])
                print('t: {:1.2e}, v: {:1.2e}, i: {:1.2e}'.format(*data_tuple))
            if 'error' in rsp_dict:
                print(rsp_dict['error'])
                break
            if 'done' in rsp_dict:
                break
        tsec = np.array([item['t'] for item in data_list])
        volt = np.array([item['v'] for item in data_list])
        curr = np.array([item['i'] for item in data_list])
        return tsec, volt, curr  # sec, V, A


    def error_check_rsp(self,rsp):
        if 'error' in rsp:
            raise PotentiostatError(rsp['error'])


# Utility
# --------------------------------------------------------------------------------

class PotentiostatError(Exception):
    pass

def convert_A_to_uA(value):
    return 1.0e6*value

