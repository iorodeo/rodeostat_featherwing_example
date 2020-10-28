
class Scheduler:

    def __init__(self):
        self.table = {}

    def update(self):
        for name, job in self.table.items():
            job.update()
            if job.done:
                job.cleanup()
                del self.table[name]

    def add(self,name,job):
        self.table[name] = job





