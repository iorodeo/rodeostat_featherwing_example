import json_messaging
import cyclic_test

class Handler:

    def __init__(self,scheduler,pstat):
        self.receiver = json_messaging.Receiver()

        self.scheduler = scheduler
        self.pstat = pstat
        self.pstat.connected = True
        self.done = False

    def update(self):
        msg = self.receiver.update()
        if msg: 
            if 'voltage' in msg:
                try:
                    voltage = float(msg['voltage'])
                except(ValueError, TypeError):
                    err_msg = {'error': 'voltage must be float'}
                    json_messaging.send(err_msg)
                    return
                self.pstat.voltage = voltage

            if 'connected' in msg:
                try:
                    connected = bool(msg['connected'])
                except(ValueError, TypeError):
                    err_msg = {'error': 'connected must be bool'}
                    json_messaging.send(err_msg)
                    return
                self.pstat.connected = connected

            if 'averaging' in msg:
                try:
                    averaging = int(msg['averaging'])
                except(ValueError, TypeError):
                    err_msg = {'error': 'averaging must be int'}
                    json_messaging.send(err_msg)
                    return
                self.pstat.averaging = averaging

            if 'offset' in msg:
                try:
                    offset = float(msg['offset'])
                except(ValueError, TypeError):
                    err_msg = {'error': 'offset must be float'}
                    json_messaging.send(err_msg)
                    return
                self.pstat.offset = offset

            if 'range' in msg:
                try:
                    self.pstat.current_range = msg['range']
                except KeyError:
                    err_msg = {'error': 'current range not found'}
                    json_messaging.send(err_msg)
                    return

            if 'test' in msg:
                try:
                    test = dict(msg['test'])
                except(ValueError, TypeError):
                    err_msg = {'error': 'test must be dictionary'}
                    json_messaging.send(err_msg)
                    return

                try:
                    name = test['name']
                except KeyError:
                    err_msg = {'error': 'test missing name'}
                    json_messaging.send(err_msg)
                    return

                try:
                    param = test['param']
                except(ValueError, TypeError):
                    err_msg = {'error': 'test missing param'}
                    json_messaging.send(err_msg)
                    return

                try:
                    param = dict(param)
                except(ValueError, TypeError):
                    err_msg = {'error': 'param must be dict'}
                    json_messaging.send(err_msg)
                    return

                if name == 'cyclic':
                    test = cyclic_test.CyclicTest(self.pstat,param)
                    if not test.done:
                        self.scheduler.add('cyclic_test', test)

                else:
                    err_msg = {'error': 'unknown test name'}
                    json_messaging.send(err_msg)
                    return


            # Send response
            rsp = {
                    'connected'    : self.pstat.connected,
                    'current'      : self.pstat.current,
                    'voltage'      : self.pstat.voltage,
                    'ref_voltage'  : self.pstat.ref_voltage,
                    'averaging'    : self.pstat.averaging,
                    'offset'       : self.pstat.offset,
                    'range'        : self.pstat.current_range,
                    }
            json_messaging.send(rsp)
        elif self.receiver.error:
            rsp = {'error': True, 'message': 'parse error'}
            json_messaging.send(rsp)

