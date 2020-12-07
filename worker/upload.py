import pandas as pd
from pymongo import MongoClient
from datetime import datetime
import os

class UploadException(Exception):
    pass

class uploadWorker:
    def __init__(self, task_id):
        self.task_id = task_id
        self.filename = str(task_id)+"file.csv"
        self.lines_read = 0
        self.paused = False
        self.terminated = False
        self.df = pd.read_csv(self.filename)
        self.lines = len(self.df.index)
        self.success = False
        super().__init__()
    def start(self):
        self.paused = False
        client = MongoClient(os.environ.get("MONGODBURI"))
        db = client['atlanC']
        coll = db['teams']
        for index, row in self.df.iloc[self.lines_read:].iterrows():
            try:
                post = {
                    "t_id": self.task_id,
                    "name": str(row["Name"]),
                    "description": str(row["Description"]),
                    "added_on": datetime.now().isoformat()
                }
                coll.insert_one(post).inserted_id
                self.lines_read += 1
                if self.paused or self.terminated:
                    raise UploadException
            except UploadException:
                break
        if not self.paused and not self.terminated:
            self.success = True
    def pause(self):
        self.paused = True
    def terminate(self):
        client = MongoClient(os.environ.get("MONGODBURI"))
        db = client['atlanC']
        coll = db['teams']
        self.terminated = True
        coll.delete_many({"t_id": self.task_id})
    def resume(self):
        if self.paused:
            self.start()
    def status(self):
        if self.success:
            return "Complete"
        else:
            return str(round((self.lines_read/self.lines)*100,2))+"%"
                

    