import time
import command
import scheduler
import potentiostat

pstat = potentiostat.Potentiostat(current_range='1000uA')
job_scheduler = scheduler.Scheduler()
job_scheduler.add('command', command.Handler(job_scheduler, pstat))

while True:
    job_scheduler.update()


