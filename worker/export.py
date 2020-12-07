import pandas as pd
from pymongo import MongoClient
from datetime import datetime
import os
class ExportException(Exception):
    pass

class exportWorker:
    def __init__(self, start_date, end_date, task_id):
        self.task_id = task_id
        self.paused = False
        self.terminated = False
        self.paused = False
        self.start_date = start_date
        self.end_date = end_date
        self.client = MongoClient(os.environ.get("MONGODBURI"))
        self.db = self.client['atlanC']
        self.coll = self.db['teams']
        self.results = {}
        self.results_read = 0
        self.success = False
        super().__init__()
    def start(self):
        self.paused = False
        f = open(str(self.task_id)+"file.csv", "a")
        self.results = self.coll.find({"added_on": {'$gte': self.start_date, '$lt':self.end_date }}).skip(self.results_read)
        f.write("Name,Description,Date\n")
        for line in self.results:
            try:
                #line = self.results.pop(0)
                f.write(line["name"]+","+line["description"]+","+line["added_on"]+"\n")
                self.results_read += 1
                if self.paused or self.terminated:
                    f.close()
                    raise ExportException
            except ExportException:
                break
        if not self.paused and not self.terminated:
            self.success = True
            f.close()
    def pause(self):
        self.paused = True
    def terminate(self):
        self.terminated = True
        os.remove(str(self.task_id)+"file.csv")
    def resume(self):
        self.start()
    def status(self):
        if self.success:
            return "Complete"
        return str(round((self.results_read/self.results.count())*100,2))+"%"