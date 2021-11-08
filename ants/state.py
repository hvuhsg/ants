from .job import Job
from .message import Message


class State:
    def __init__(self, jobs: dict = None, messages: dict = None):
        if jobs is None:
            jobs = {}
        if messages is None:
            messages = {}
        self.jobs = jobs  # {job_id: job_object}
        self.messages = messages  # {message_id: message_object}

    def merge(self, other_state):
        for job in other_state.jobs.values():
            my_job = self.jobs.get(job.id, None)
            if my_job:
                job = max(job, my_job)
            self.jobs[job.id] = job
        for message in other_state.messages.values():
            my_message = self.messages.get(message.id, None)
            if my_message:
                message = max(message, my_message)
            self.messages[message.id] = message

    def to_dict(self) -> dict:
        jobs = {job_id: job.to_dict() for job_id, job in self.jobs.items()}
        messages = {message_id: message.to_dict() for message_id, message in self.messages.items()}
        return {'jobs': jobs, 'messages': messages}

    @classmethod
    def from_dict(cls, dict_: dict):
        jobs = {job_id: Job.from_dict(job_dict) for job_id, job_dict in dict_['jobs'].items()}
        messages = {
            message_id: Message.from_dict(message_dict)
            for message_id, message_dict in dict_['messages'].items()
        }
        return cls(jobs=jobs, messages=messages)

    def __str__(self):
        max_jobs_printed = 3
        state_str = 'State(\n'
        for job in list(self.jobs.values())[:min(max_jobs_printed, len(self.jobs))]:
            state_str += str(job) + '\n'
        if len(self.jobs) > max_jobs_printed:
            state_str += '...\n'
        state_str += ')'
        return state_str
