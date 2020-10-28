import time
from potentiostat import  Potentiostat

def get_current(pstat, voltage, sleep_dt):
    rsp_dict = pstat.send_and_receive({'voltage': voltage})
    time.sleep(sleep_dt)
    rsp_dict = pstat.send_and_receive({'voltage': voltage})
    current = rsp_dict['current']
    return current

step = 0.02
scale = 0.8
voltage = 0.0
current_tol = 1.0e-8
sleep_dt = 1.0
direction = None

pstat = Potentiostat('/dev/ttyACM0')
rsp_dict = pstat.send_and_receive({'averaging': 100})
rsp_dict = pstat.send_and_receive({'connected': True})

current = get_current(pstat, voltage, sleep_dt)
print('current: {}'.format(current))

done = False

if current > current_tol:
    direction = 'down'
elif current < -current_tol:
    direction = 'up'
else:
    done = True


while not done:

    if direction == 'up':
        voltage += step
        current = get_current(pstat, voltage, sleep_dt)
        if current > current_tol:
            direction = 'down'
            step *= scale

    else:
        voltage -= step
        current = get_current(pstat, voltage, sleep_dt)
        if current < current_tol:
            direction = 'up'
            step *= scale

    print('v: {:1.5e}, i: {:1.5e}, s: {:1.5e}'.format(voltage, current, step))
    if abs(current) <= current_tol:
        done = True


print(' v_offset {}'.format(voltage))













