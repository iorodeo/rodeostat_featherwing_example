import matplotlib.pyplot as plt
from potentiostat import  Potentiostat

output_file = 'data.txt'

param = {
        'max_voltage'   :  1.5,
        'min_voltage'   : -1.5,
        'scan_rate'     :  0.50,
        'start_voltage' : 'min_voltage',
        'sample_rate'   : 15.0,
        'cycles'        : 2,
        }

pstat = Potentiostat('/dev/ttyACM0')
pstat.range('100uA')
pstat.averaging(50)
pstat.offset(0.0)

pstat.connected(True)
t, v, i = pstat.run_test('cyclic', param)
pstat.connected(False)

i = 1.0e6*i # convert to uA

fig, ax = plt.subplots(2,1,sharex=True)
ax[0].plot(t,v)
ax[0].set_ylabel('(V)')
ax[0].grid(True)

ax[1].plot(t,i)
ax[1].set_ylabel('(uA)')
ax[1].set_xlabel('time (s)')
ax[1].grid(True)

fig, ax = plt.subplots(1,1)
ax.plot(v,i)
ax.set_xlabel('(V)')
ax.set_ylabel('(uA)')
ax.grid(True)
plt.show()

with open(output_file,'w') as f:
    for (tt,vv,ii) in zip(t,v,i):
        f.write('{}, {}, {}\n'.format(tt,vv,ii))

















