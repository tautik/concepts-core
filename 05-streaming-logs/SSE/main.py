import os
import time
import datetime
from threading import Thread
from uuid import uuid4

from faker import Faker
from flask import Flask, Response, redirect, render_template

DATASETS_LOGS = "./data"

fake = Faker()
app = Flask(__name__)


def mock_deployment(deployment_id: str):
    """Simulate a deployment by writing logs to a file"""
    filepath = os.path.join(DATASETS_LOGS, f"{deployment_id}.log")
    
    with open(filepath, "w", encoding="utf-8") as fp:
        for _ in range(100000):
            timestamp = datetime.datetime.now().isoformat()
            log_entry = fake.text(max_nb_chars=64)
            fp.write(f"{timestamp}: {log_entry}\n")
            fp.flush()
            time.sleep(0.5)


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
    """Show deployment page with real-time log streaming"""
    return render_template("deployment.html", deployment_id=deployment_id)


@app.route("/deployments", methods=["POST"])
def create_deployment_handler():
    """Create a new deployment and start background log generation"""
    deployment_id = uuid4().hex
    thread = Thread(target=mock_deployment, args=(deployment_id,))
    thread.start()
    
    return redirect(f"/deployments/{deployment_id}", 301)


def log_tailer(deployment_id: str):
    """Generator function that tails a log file and yields new lines"""
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
            yield f"data: {line.strip()}\n\n"


@app.route("/logs/<deployment_id>")
def stream_logs_handler(deployment_id):
    """
    Server-Sent Events (SSE) endpoint for streaming logs in real-time.
    
    EventSource is a web standard that allows a web page to receive 
    automatic updates from a server via HTTP connection. It's perfect
    for real-time data streaming like logs, notifications, etc.
    
    The key is setting the mimetype to 'text/event-stream' which tells
    the browser this is an SSE stream.
    """
    logs_stream = log_tailer(deployment_id)
    return Response(
        logs_stream, 
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )


if __name__ == "__main__":
    # Ensure data directory exists
    os.makedirs(DATASETS_LOGS, exist_ok=True)
    app.run(debug=True)

