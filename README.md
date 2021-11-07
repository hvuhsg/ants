# ants
Allow you to create you own custom decentralize job management system.


### install
```shell script
pip install pyants
```

### How it works?
The library provides you with interface to add assign and do jobs in an decentralized environment.
For example to create your own node just override some methods:
##### node
```python
from typing import List

from ants import BaseNode, Job


class MyNode(BaseNode):

    def add_jobs(self) -> List[Job]:
        return []  # List of jobs to run (the nodes can create duplicate jobs and the lib will manage that)

    def assign_to_jobs(self, pending_jobs: List[Job]) -> List[Job]:
        # You can choose which jobs to assign your self to
        return [] # List of jobs to assign your self to

    def do_jobs(self, my_assigned_jobs: List[Job]):
        # this list do not have to match the list you returned from the assign_to_jobs method,
        # the library will manage the job distribution to the nodes.
        # loop over your assigned jobs and complete them
        for assigned_job in my_assigned_jobs:
            # do your job
            # after you complete a job, report it with job.set_result({'status': 'OK'})
            pass
    
    def completed_jobs(self, done_jobs: List[Job]):
        # Here you can be updated about the jobs that has done by all the nodes
        # you can store it and use it in your business logic
        # For example do not create a operational check for some server if it bin checked recently
        pass
```
##### communication
The communication class expose tow methods:
- pull
- broadcast

The 'pull' method should return list of state objects from other nodes  
The 'broadcast' method should transfer your state to other nodes  

The library implemented for you a simple p2p socket server communication for decentralized networking
```python
from ants.communications.socketserver import SocketCommunication

communication = SocketCommunication(host=..., port=..., pull_interval=..., bootstrap_nodes=...)
```



### Example
Decentralized monitor example.
```shell script
$> git clone https://github.com/hvuhsg/ants.git
$> cd ants/examples/monitor
$> python3 -m venv venv
$> . venv/bin/activate
$> pip install -r requirements.txt
$> pip install ../../.
$> python run.py
```
