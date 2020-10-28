import board
import analogio
import digitalio

UINT16_MAX_VALUE = 2**16 - 1

class Potentiostat:

    CURRENT_RANGE_TO_TIA_RESISTOR = {
            '1uA'    : 1650000.0,
            '10uA'   : 165000.0, 
            '100uA'  : 16500.0,
            '1000uA' : 1650.0,
            }
    TIA_RESISTOR_TO_CURRENT_RANGE = {v:k for (k,v) in CURRENT_RANGE_TO_TIA_RESISTOR.items()}

    def __init__(self, current_range='100uA', num_avg=15):

        self.current_range = current_range
        self.num_avg = num_avg 

        # Hardware connections 
        self.setp_aout = analogio.AnalogOut(board.A0)
        self.setp_aout_saved_value = 0.0
        self.tia_ain = analogio.AnalogIn(board.A2)
        self.ref_ain = analogio.AnalogIn(board.A4)
        self.ctr_elect_switch = digitalio.DigitalInOut(board.D13)
        self.ctr_elect_switch.direction = digitalio.Direction.OUTPUT

        # Transimpedance amplifier resistor value
        self.tia_resistor_ohm = self.CURRENT_RANGE_TO_TIA_RESISTOR[current_range]

        # System voltage (vpow) and virtual ground voltage (vgnd) 
        self.vpow = self.tia_ain.reference_voltage  
        self.vgnd = 0.5*self.vpow                   

        # Set initial state
        self.offset = 0.0
        self.connected = False 
        self.voltage = 0.0

    @property
    def current_range(self):
        return self.TIA_RESISTOR_TO_CURRENT_RANGE[self.tia_resistor_ohm]

    @current_range.setter
    def current_range(self, value):
        self.tia_resistor_ohm = self.CURRENT_RANGE_TO_TIA_RESISTOR[value]

    @property
    def averaging(self):
        return self.num_avg

    @averaging.setter
    def averaging(self, num):
        self.num_avg = num 

    @property
    def connected(self):
        return not self.ctr_elect_switch.value

    @connected.setter
    def connected(self,value):
        if value:
            self.ctr_elect_switch.value = False
        else:
            self.ctr_elect_switch.value = True 

    @property
    def voltage(self):
        return self.setp_aout_saved_value

    @voltage.setter
    def voltage(self,value):
        value_shifted = self.vgnd + value + self.offset
        value_uint16 = volt_to_uint16(value_shifted,self.vpow)
        self.setp_aout.value = value_uint16
        self.setp_aout_saved_value = value

    @property
    def current(self):
        value = self.tia_voltage/self.tia_resistor_ohm
        return value

    @property
    def tia_voltage(self):
        return self.read_ain_avg(self.tia_ain, self.num_avg)

    @property
    def ref_voltage(self):
        return self.read_ain_avg(self.ref_ain, self.num_avg)

    def read_ain(self,ain):
        value_uint16 = ain.value
        value_shifted = uint16_to_volt(value_uint16,self.vpow)
        value = value_shifted - self.vgnd
        return value

    def read_ain_avg(self,ain,num):
        value = 0.0
        for i in range(num):
            value += self.read_ain(ain)
        return value/float(num)




# Utility functions
# ---------------------------------------------------------------------------------------
def volt_to_uint16(v,vref):
    vint = int(UINT16_MAX_VALUE*float(v)/float(vref))
    return clamp(vint, 0, UINT16_MAX_VALUE)

def uint16_to_volt(n,vref):
    return vref*float(n)/float(UINT16_MAX_VALUE)

def clamp(value, min_value, max_value):
    value_clamped = min(max_value, value)
    value_clamped = max(0,value_clamped)
    return value_clamped

