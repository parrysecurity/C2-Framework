import logging
import json
from datetime import datetime
import os

class C2Logger:
    def __init__(self, log_dir="/var/log/c2"):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        
        # Setup file handlers
        self.agent_log = self.setup_logger('agent', f"{log_dir}/agents.log")
        self.command_log = self.setup_logger('command', f"{log_dir}/commands.log")
        self.event_log = self.setup_logger('event', f"{log_dir}/events.log")
    
    def setup_logger(self, name, log_file):
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def log_agent_activity(self, agent_id, action, details):
        self.agent_log.info(json.dumps({
            'timestamp': datetime.now().isoformat(),
            'agent_id': agent_id,
            'action': action,
            'details': details
        }))
    
    def log_command(self, agent_id, command, output):
        self.command_log.info(json.dumps({
            'timestamp': datetime.now().isoformat(),
            'agent_id': agent_id,
            'command': command,
            'output': output[:500]  # Truncate long output
        }))
    
    def log_event(self, event_type, severity, message):
        self.event_log.info(json.dumps({
            'timestamp': datetime.now().isoformat(),
            'type': event_type,
            'severity': severity,
            'message': message
        }))
