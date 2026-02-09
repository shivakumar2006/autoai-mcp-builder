import docker 
import subprocess
import time 
from pathlib import Path
from typing import Dict, Callable 

class AgentDeployer: 
    
    def __init__(self, on_progress: Callable = None): 
        self.client = docker.from_env()