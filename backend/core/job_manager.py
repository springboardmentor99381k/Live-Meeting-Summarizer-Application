jobs = {}

def create_job(job_id):
    jobs[job_id] = {
        "status":"uploaded",
        "result": None
    }

def update_job(job_id, status, data=None):
    jobs[job_id]["status"] = status
    if data:
        jobs[job_id]["result"] = data

def get_job(job_id):
    return jobs.get(job_id)