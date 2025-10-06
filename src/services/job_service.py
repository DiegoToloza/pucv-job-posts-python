from pymongo import MongoClient
from classes.job import Job
from typing import List
from utils.config import MONGO_URI

client = MongoClient(MONGO_URI)
db = client.get_database("jobs_db")
collection = db.jobs

def save_many_jobs(jobs: List[Job]):
    if not jobs:
        return
    data = [job.to_dict() for job in jobs]
    collection.insert_many(data)
