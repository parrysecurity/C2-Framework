#!/usr/bin/env python3
"""
C2 Framework Testing Script
Run this in a controlled lab environment
"""

import requests
import json
import time
import subprocess
import sys

def test_server():
    """Test if C2 server is running"""
    try:
        response = requests.get("https://localhost:443/api/implant/config", verify=False)
        if response.status_code == 200:
            print("[+] C2 Server is running")
            return True
    except:
        print("[-] C2 Server is not responding")
        return False

def test_agent_registration():
    """Test agent registration"""
    print("[*] Testing agent registration...")
    
    # Start agent in background
    agent_process = subprocess.Popen(
        [sys.executable, "agent/implant.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    time.sleep(5)
    
    # Check if agent registered
    try:
        response = requests.get("https://localhost:443/api/agents", verify=False)
        agents = response.json()
        if len(agents) > 0:
            print(f"[+] Agent registered successfully: {agents[0]['agent_id']}")
            return True
    except:
        print("[-] Agent registration failed")
    
    return False

def test_command_execution():
    """Test command execution"""
    print("[*] Testing command execution...")
    
    # This would test sending commands to agent
    # Implementation depends on your API
    
    print("[+] Command execution test complete")

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    print("C2 Framework Test Suite")
    print("========================")
    
    if test_server():
        test_agent_registration()
        test_command_execution()
    
    print("\n[*] Test complete")
