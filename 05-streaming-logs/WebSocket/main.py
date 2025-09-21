import os
import time
import datetime
import json
from threading import Thread
from uuid import uuid4

from faker import Faker
from flask import Flask, render_template, redirect, request
from flask_socketio import SocketIO, emit, join_room, leave_room

DATASETS_LOGS = "./data"

fake = Faker()
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Initialize SocketIO with CORS support
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Store active deployments and their background threads
active_deployments = {}


def mock_deployment(deployment_id: str):
    """Simulate a deployment by writing logs to a file"""
    filepath = os.path.join(DATASETS_LOGS, f"{deployment_id}.log")
    
    with open(filepath, "w", encoding="utf-8") as fp:
        for i in range(100000):
            timestamp = datetime.datetime.now().isoformat()
            log_entry = fake.text(max_nb_chars=64)
            log_line = f"{timestamp}: {log_entry}"
            
            # Write to file
            fp.write(f"{log_line}\n")
            fp.flush()
            
            time.sleep(0.5)
    
    # Clean up when done
    if deployment_id in active_deployments:
        del active_deployments[deployment_id]


def log_tailer(deployment_id: str):
    """Generator function that tails a log file and yields new lines via WebSocket"""
    filepath = os.path.join(DATASETS_LOGS, f"{deployment_id}.log")
    
    # Wait for file to exist
    while not os.path.exists(filepath):
        time.sleep(0.1)
    
    with open(filepath, "r", encoding="utf-8") as fp:
        # Go to end of file
        fp.seek(0, 2)
        
        while True:
            line = fp.readline()
            if not line:
                time.sleep(0.1)
                continue
            
            # Parse the log line
            parts = line.strip().split(': ', 1)
            if len(parts) >= 2:
                timestamp = parts[0]
                message = parts[1]
                
                # Emit to WebSocket clients in this deployment's room
                socketio.emit('new_log', {
                    'timestamp': timestamp,
                    'message': message,
                    'full_line': line.strip()
                }, room=deployment_id)


# Store active tailers
active_tailers = {}


@app.route("/", methods=["GET"])
def index_handler():
    """Show all previous deployments"""
    deployments = [
        x.split(".")[0] for x in os.listdir(DATASETS_LOGS) 
        if x.endswith(".log")
    ]
    return render_template("index.html", deployments=deployments)


@app.route("/deployments/<deployment_id>", methods=["GET"])
def deployment_handler(deployment_id):
    """Show deployment page with real-time WebSocket log streaming"""
    return render_template("deployment.html", deployment_id=deployment_id)


@app.route("/deployments", methods=["POST"])
def create_deployment_handler():
    """Create a new deployment and start background log generation"""
    deployment_id = uuid4().hex
    
    # Start background thread for log generation
    thread = Thread(target=mock_deployment, args=(deployment_id,))
    thread.daemon = True
    thread.start()
    
    # Store the thread reference
    active_deployments[deployment_id] = thread
    
    return redirect(f"/deployments/{deployment_id}", 301)


# WebSocket event handlers
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f"Client connected: {request.sid}")
    emit('status', {
        'type': 'connected',
        'message': 'Connected to WebSocket server',
        'client_id': request.sid
    })


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(f"Client disconnected: {request.sid}")


@socketio.on('start_streaming')
def handle_start_streaming(data):
    """Start streaming logs for a specific deployment"""
    deployment_id = data['deployment_id']
    join_room(deployment_id)
    
    print(f"Client {request.sid} started streaming deployment: {deployment_id}")
    
    # Send existing logs from file if available (last 50 lines)
    filepath = os.path.join(DATASETS_LOGS, f"{deployment_id}.log")
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as fp:
                lines = fp.readlines()
                recent_lines = lines[-50:] if len(lines) > 50 else lines
                
                for line in recent_lines:
                    if line.strip():
                        parts = line.strip().split(': ', 1)
                        if len(parts) >= 2:
                            timestamp = parts[0]
                            message = parts[1]
                            emit('new_log', {
                                'timestamp': timestamp,
                                'message': message,
                                'full_line': line.strip(),
                                'is_historical': True
                            })
        except Exception as e:
            print(f"Error reading existing logs: {e}")
    
    # Start tailing logs for this deployment if not already started
    if deployment_id not in active_tailers:
        tailer_thread = Thread(target=log_tailer, args=(deployment_id,))
        tailer_thread.daemon = True
        tailer_thread.start()
        active_tailers[deployment_id] = tailer_thread
        print(f"Started log tailer for deployment: {deployment_id}")
    
    emit('status', {
        'type': 'streaming_started',
        'message': f'Started streaming logs for {deployment_id}',
        'deployment_id': deployment_id
    })


@socketio.on('stop_streaming')
def handle_stop_streaming(data):
    """Stop streaming logs for a deployment"""
    deployment_id = data['deployment_id']
    leave_room(deployment_id)
    
    print(f"Client {request.sid} stopped streaming deployment: {deployment_id}")
    
    emit('status', {
        'type': 'streaming_stopped',
        'message': f'Stopped streaming logs for {deployment_id}',
        'deployment_id': deployment_id
    })


@socketio.on('ping')
def handle_ping():
    """Handle ping from client for connection testing"""
    emit('pong', {'timestamp': datetime.datetime.now().isoformat()})


if __name__ == "__main__":
    # Ensure data directory exists
    os.makedirs(DATASETS_LOGS, exist_ok=True)
    
    print("Starting WebSocket server...")
    print("Visit http://localhost:6758 to see the application")
    
    # Run with SocketIO
    socketio.run(app, debug=True, host='0.0.0.0', port=6758)
