try:
    from time import monotonic as time_in_secs
except ImportError:
    from time import time as time_in_secs

try:
    from potentiostat import Potentiostat
except ImportError:
    class Potentiostat:
        def __init__(self):
            self.connected = False
            self.voltage = 0.0
            self.current = 0.0
            self.vpow = 3.3

try:
    from json_messaging import send 
except ImportError:
    import json
    def send(msg):
        print('send: {}'.format(json.dumps(msg)))



class CyclicTest:


    DIRECTION_UP = 0 
    DIRECTION_DOWN = 1
    MAX_SAMPLE_RATE = 200.0


    def __init__(self,pstat,param):
        self.param = {}
        self.done = False
        self.pstat = pstat
        self.t_start = 0.0
        self.t_now = 0.0
        self.t_half_cycle = 0.0
        self.t_next_sample = 0.0
        self.v_half_cycle = 0.0
        self.half_cycle_count = 0
        self.direction = self.DIRECTION_UP
        self.voltage_range_max =  0.5*self.pstat.vpow
        self.voltage_range_min = -0.5*self.pstat.vpow
        self.sample_period = 1.0
        ok, msg = self.extract_param(param)
        if ok:
            self.setup()
        else:
            msg_dict = {'error': msg}
            send(msg_dict)
            self.done = True
            self.cleanup()
        self.sample_period = 1.0/self.param['sample_rate']


    def __del__(self):
        self.cleanup()


    @property
    def voltage(self):
        return self.pstat.voltage


    @voltage.setter
    def voltage(self,v):
        self.pstat.voltage = v


    @property
    def current(self):
        return self.pstat.current


    @property
    def elapsed_time(self):
        return self.t_now - self.t_start


    @property
    def sign(self):
        if self.direction == self.DIRECTION_UP:
            return  1.0
        else:
            return -1.0


    def update(self):
        self.t_now = time_in_secs()
        dt = self.t_now - self.t_half_cycle
        voltage = self.v_half_cycle + self.sign*dt*self.param['scan_rate']
        new_cycle = False
        if voltage >= self.param['max_voltage'] and self.direction == self.DIRECTION_UP: 
            self.v_half_cycle = self.param['max_voltage']
            new_cycle = True
        if voltage <= self.param['min_voltage'] and self.direction == self.DIRECTION_DOWN:
            self.v_half_cycle = self.param['min_voltage']
            new_cycle = True
        if new_cycle:
            self.t_half_cycle = self.t_now
            voltage = self.v_half_cycle
            self.half_cycle_count += 1 
            self.change_direction()
            if self.half_cycle_count >= 2*self.param['cycles']:
                self.done = True
        self.voltage = voltage
        if self.t_now >= self.t_next_sample or self.done:
            data_dict = {'data': {'t': self.elapsed_time, 'v': self.voltage, 'i': self.current}}
            if self.done:
                data_dict['done'] = True
            send(data_dict)
            self.t_next_sample = self.t_now + self.sample_period


    def change_direction(self):
        if self.direction == self.DIRECTION_UP:
            self.direction = self.DIRECTION_DOWN
        else:
            self.direction = self.DIRECTION_UP


    def setup(self):
        if self.param['start_voltage'] == 'max_voltage':
            self.v_half_cycle = self.param['max_voltage']
            self.direction = self.DIRECTION_DOWN
        else:
            self.v_half_cycle = self.param['min_voltage']
            self.direction = self.DIRECTION_UP
        self.t_now = time_in_secs()
        self.t_start = self.t_now
        self.t_half_cycle = self.t_now 
        self.t_next_sample = self.t_now 
        self.half_cycle_count = 0
        self.voltage = self.v_half_cycle
        self.done = False
        self.pstat.connected = True


    def cleanup(self):
        self.pstat.connected = False
        self.voltage = 0.0


    def extract_param(self,param):

        # Check that we have all required items in param 
        expected_keys = [ 
                'max_voltage',   
                'min_voltage',   
                'scan_rate',     
                'start_voltage', 
                'sample_rate',   
                'cycles',        
                ]

        param_tmp = {}
        for key in expected_keys:
            try:
                param_tmp[key] = param[key]
            except KeyError:
                return False, 'missing param {}'.format(key)

        # Check that float values are of correct type
        float_keys  = [
                'max_voltage', 
                'min_voltage', 
                'sample_rate',
                'scan_rate', 
                ] 
        for key in float_keys:
            try:
                param_tmp[key] = float(param_tmp[key])
            except(ValueError, TypeError):
                return False, '{} must be float'.format(key)

        # Check that integer items are of correct type
        integer_keys = ['cycles']
        for key in integer_keys:
            try:
                param_tmp[key] = int(param_tmp[key])
            except(ValueError, TypeError):
                return False, '{} must be int'.format(key)

        # Check that certain values are > 0
        positive_keys = [
                'scan_rate', 
                'sample_rate', 
                'cycles',
                ]
        for key in positive_keys:
            if param_tmp[key] <= 0:
                return False, '{} must be > 0'.format(key)

        # Check that voltages are within range and that min < max voltage
        for key in ['max_voltage', 'min_voltage']:
            if param_tmp[key] > self.voltage_range_max:
                return False, '{} > voltage_range_max'.format(key)
            if param_tmp[key] < self.voltage_range_min:
                return False, '{} < voltage_range_min'.format(key)
        if param_tmp['min_voltage'] >= param_tmp['max_voltage']:
            return False, 'min_voltage must be < max_voltage'

        # Check that start_voltage is either max_voltage or min_voltage
        if not param_tmp['start_voltage'] in ['max_voltage', 'min_voltage']:
            return False, 'start_voltage must be either max_voltage or min_voltage'

        # Check that sample rate is less or equal than maximum allowed sample rate
        if param_tmp['sample_rate'] > self.MAX_SAMPLE_RATE:
            return False, 'sample_rate must be <= {}'.format(self.MAX_SAMPLE_RATE)

        self.param = param_tmp
        return True, ''






