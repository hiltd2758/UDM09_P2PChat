import time  
import psutil  
import threading  
from typing import List, Dict, Any  
import subprocess  
import os 
import matplotlib.pyplot as plt  
import pandas as pd   
  
class TestMetrics:  
    def __init__(self):  
        self.start_time = None  
        self.end_time = None  
        self.cpu_usage = []  
        self.memory_usage = []  
        self.message_count = 0  
        self.error_count = 0  
          
    def start_monitoring(self):  
        self.start_time = time.time()  
        self.monitor_thread = threading.Thread(target=self._monitor_resources)  
        self.monitor_thread.daemon = True  
        self.monitor_thread.start()  
          
    def _monitor_resources(self):  
        process = psutil.Process()  
        while True:  
            self.cpu_usage.append(process.cpu_percent())  
            self.memory_usage.append(process.memory_info().rss / 1024 / 1024)  # MB  
            time.sleep(0.1)  
              
    def stop_monitoring(self):  
        self.end_time = time.time()  
        return {  
            'duration': self.end_time - self.start_time,  
            'avg_cpu': sum(self.cpu_usage) / len(self.cpu_usage) if self.cpu_usage else 0,  
            'peak_memory': max(self.memory_usage) if self.memory_usage else 0,  
            'messages_sent': self.message_count,  
            'errors': self.error_count  
        }  
  
def launch_peer_instances(count: int, start_port: int = 12000) -> List[subprocess.Popen]:  
    """Launch multiple peer instances for testing"""  
    processes = []  
    for i in range(count):  
        port = start_port + i  
        cmd = ['python', 'main.py', str(port)]  
        # Redirect output to log files  
        log_file = open(f'tests/results/logs/peer_{port}.log', 'w')  
        proc = subprocess.Popen(cmd, stdout=log_file, stderr=log_file)  
        processes.append(proc)  
        time.sleep(0.5)  # Stagger launches  
    return processes

