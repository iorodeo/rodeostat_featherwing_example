import time
import potentiostat
import matplotlib.pyplot as plt

p = potentiostat.Potentiostat('/dev/ttyACM0')

rsp = p.range('100uA')
print(rsp)

rsp = p.averaging(10)
print(rsp)

rsp = p.voltage(1.0)
print(rsp)

rsp = p.voltage(0.0)
print(rsp)

for i in range(10):
    rsp = p.get_values()
    print(rsp)
    time.sleep(0.001)
print()


rsp = p.connected(True)
print(rsp)

param = {
        'max_voltage'   :  1.65,
        'min_voltage'   : -1.65,
        'scan_rate'     :  1.00,
        'start_voltage' : 'min_voltage',
        'sample_rate'   : 15.0,
        'cycles'        : 2,
        }

t, v, i = p.run_test('cyclic', param)

i_uA = 1.0e6*i

rsp = p.connected(False)
print(rsp)

plt.subplot(2,1,1)
plt.plot(t,v)
plt.ylabel('(V)')
plt.grid(True)

plt.subplot(2,1,2)
plt.plot(t,i_uA)
plt.xlabel('t (sec)')
plt.ylabel('(uA)')
plt.grid(True)
plt.show()



