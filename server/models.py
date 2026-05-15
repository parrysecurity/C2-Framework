from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()

class Agent(db.Model):
    __tablename__ = 'agents'
    
    id = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.String(64), unique=True, nullable=False)
    hostname = db.Column(db.String(255))
    username = db.Column(db.String(255))
    os_type = db.Column(db.String(100))
    os_version = db.Column(db.String(255))
    architecture = db.Column(db.String(50))
    ip_address = db.Column(db.String(45))
    first_seen = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='active')
    sleep_time = db.Column(db.Integer, default=5)
    jitter = db.Column(db.Integer, default=20)
    encryption_key = db.Column(db.Text)
    working_directory = db.Column(db.Text)
    privilege_level = db.Column(db.String(20), default='user')
    
    def to_dict(self):
        return {
            'agent_id': self.agent_id,
            'hostname': self.hostname,
            'username': self.username,
            'os': f"{self.os_type} {self.os_version}",
            'ip': self.ip_address,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
            'status': self.status
        }

class Task(db.Model):
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.String(64), unique=True, nullable=False)
    agent_id = db.Column(db.String(64), nullable=False)
    command = db.Column(db.Text)
    command_type = db.Column(db.String(50))  # shell, upload, download, etc.
    status = db.Column(db.String(20), default='pending')
    output = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    executed_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)

class Listener(db.Model):
    __tablename__ = 'listeners'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    type = db.Column(db.String(20))  # https, dns, smb
    host = db.Column(db.String(255))
    port = db.Column(db.Integer)
    status = db.Column(db.String(20), default='inactive')
    config = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
