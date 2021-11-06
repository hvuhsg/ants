from .job import JobStatus, Job


class State:
    def __init__(self, jobs: dict = None):
        if jobs is None:
            jobs = {}
        self._jobs = jobs  # {job_id: job_object}

    def add_job(self, job: Job):
        existing_job = self._jobs.get(job.id, None)
        if existing_job and existing_job > job:
            return
        self._jobs[job.id] = job

    def remove_job(self, job_id: str):
        del self._jobs[job_id]

    def _filter_jobs_by_status(self, status: JobStatus):
        return list(filter(lambda job: job.status == status, self._jobs.values()))

    @property
    def pending_jobs(self) -> list:
        return self._filter_jobs_by_status(JobStatus.PENDING)

    @property
    def assigned_jobs(self) -> list:
        return self._filter_jobs_by_status(JobStatus.ASSIGNED)

    @property
    def done_jobs(self) -> list:
        return self._filter_jobs_by_status(JobStatus.DONE)

    def merge(self, other_state):
        for job in other_state._jobs.values():
            my_job = self._jobs.get(job.id, None)
            if my_job:
                job = max(job, my_job)
            self._jobs[job.id] = job

    def __str__(self):
        state_str = 'State(\n'
        for job in self._jobs.values():
            state_str += f'{job}\n'
        state_str += ')'
        return state_str
