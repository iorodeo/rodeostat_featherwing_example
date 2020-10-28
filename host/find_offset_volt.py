import time
from potentiostat import  Potentiostat

def get_current_with_sleep(pstat, voltage, sleep_dt):
    pstat.voltage(voltage)
    time.sleep(sleep_dt)
    rsp = pstat.get_values()
    return rsp['current']

# -------------------------------------------------------------------------------
if __name__ == '__main__':

    step = 0.02
    scale = 0.8
    voltage = 0.0
    current_tol = 1.0e-8
    sleep_dt = 1.0
    direction = None
    
    pstat = Potentiostat('/dev/ttyACM0')
    rsp = pstat.averaging(100) 
    rsp = pstat.connected(True)
    
    current = get_current_with_sleep(pstat, voltage, sleep_dt)
    print('starting current i: {}'.format(current))
    print()
    print('finding voltage offset')
    
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
            current = get_current_with_sleep(pstat, voltage, sleep_dt)
            if current > current_tol:
                direction = 'down'
                step *= scale
        else:
            voltage -= step
            current = get_current_with_sleep(pstat, voltage, sleep_dt)
            if current < current_tol:
                direction = 'up'
                step *= scale
    
        print(' v: {:1.5e}, i: {:1.5e}, s: {:1.5e}'.format(voltage, current, step))
        if abs(current) <= current_tol:
            done = True

    print('done')
    print()
    print('offset voltage: {}'.format(voltage))













