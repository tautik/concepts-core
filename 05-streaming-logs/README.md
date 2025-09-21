# 05 - Streaming Logs with Server-Sent Events (SSE)

A real-time log streaming application that demonstrates Server-Sent Events (SSE) for live data updates without the complexity of WebSockets.

## What are Server-Sent Events (SSE)?

**Server-Sent Events (SSE)** is a web standard that allows a web server to push data to a web page in real-time over a single HTTP connection. It's simpler than WebSockets but perfect for one-way communication from server to client.

### Key Characteristics:
- **One-way communication**: Server → Client only
- **Built on HTTP**: Uses standard HTTP connections
- **Automatic reconnection**: Browser automatically reconnects if connection drops
- **Simple protocol**: Just set `Content-Type: text/event-stream`
- **Event-driven**: JavaScript EventSource API handles the connection

### When to Use SSE vs WebSockets:
- **Use SSE for**: Live logs, notifications, real-time dashboards, stock prices
- **Use WebSockets for**: Chat applications, collaborative editing, gaming

## How This Application Works

### 1. Initial Load
- Index page shows all previous deployments (log files in `/data`)
- Each deployment is a clickable hyperlink to `/deployments/{deployment_id}`
- No database required - uses filesystem

### 2. Real-time Streaming
- When viewing a deployment, JavaScript creates an `EventSource` connection
- Server streams new log lines as they're written to the file
- Browser automatically displays new logs and scrolls to bottom

### 3. SSE Implementation

#### Server Side (Python/Flask):
```python
@app.route("/logs/<deployment_id>")
def stream_logs_handler(deployment_id):
    def log_generator():
        # Tail the log file and yield new lines
        while True:
            line = get_new_log_line()
            yield f"data: {line}\\n\\n"  # SSE format
    
    return Response(
        log_generator(), 
        mimetype="text/event-stream"  # Key: tells browser this is SSE
    )
```

#### Client Side (JavaScript):
```javascript
const eventSource = new EventSource('/logs/deployment_id');

eventSource.onmessage = function(event) {
    // event.data contains the log line
    displayLogLine(event.data);
};
```

## Running the Application

### Prerequisites
```bash
# Install dependencies
cd 05-streaming-logs
pip install -r requirements.txt
```

### Start the Server
```bash
python main.py
```

### Usage
1. Visit `http://localhost:5000`
2. Click "New Deployment" to create a mock deployment
3. Click on any deployment ID to view real-time logs
4. Watch logs stream in real-time as they're generated

### Testing the Application

#### Test 1: Basic Functionality
```bash
# Terminal 1: Start the server
cd 05-streaming-logs
python main.py

# Terminal 2: Test with curl (optional)
curl http://localhost:5000
```

#### Test 2: Real-time Streaming
1. Open browser to `http://localhost:5000`
2. Click "New Deployment" 
3. You should see logs appearing every 0.5 seconds
4. Open the same deployment in multiple browser tabs - all should show the same logs in real-time

#### Test 3: SSE Connection
```bash
# Test the SSE endpoint directly
curl -N -H "Accept: text/event-stream" http://localhost:5000/logs/DEPLOYMENT_ID

# You should see output like:
# data: 2025-09-21T10:30:15.123456: Some fake log text
# 
# data: 2025-09-21T10:30:15.623456: Another fake log entry
```

#### Test 4: Connection Resilience
1. Start a deployment and watch logs streaming
2. Stop the server (`Ctrl+C`)
3. Restart the server (`python main.py`)
4. Browser should automatically reconnect and continue showing logs

#### Troubleshooting
- **Port 5000 in use**: Change port in `main.py`: `app.run(debug=True, port=5001)`
- **No logs appearing**: Check if `data/` folder exists and has `.log` files
- **Connection issues**: Check browser console for JavaScript errors

## File Structure

```
05-streaming-logs/
├── main.py              # Flask app with SSE endpoints
├── templates/
│   ├── index.html       # Deployment list page
│   └── deployment.html  # Real-time log viewer
├── data/               # Log files storage
│   └── *.log          # Individual deployment logs
└── README.md          # This file
```

## Key Features

### 🔄 Real-time Updates
- Logs appear instantly as they're written
- No page refresh required
- Automatic scrolling to latest logs

### 🔗 Simple Navigation
- Clean index page with deployment links
- Easy deployment creation
- Back navigation support

### 🛡️ Connection Handling
- Automatic reconnection on network issues
- Connection status indicators
- Graceful error handling

### 📱 Responsive Design
- Terminal-like log display
- Clean, modern UI
- Mobile-friendly layout

## SSE Protocol Details

SSE uses a simple text-based protocol over HTTP:

```
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive

data: First log line

data: Second log line

data: Third log line

```

Each message must:
- Start with `data: `
- End with two newlines (`\n\n`)
- Can include optional `event:` and `id:` fields

## Comparison with Other Real-time Technologies

| Technology | Complexity | Use Case | Browser Support |
|------------|------------|----------|-----------------|
| **SSE** | Low | Server → Client streaming | Excellent |
| **WebSockets** | Medium | Bidirectional real-time | Excellent |
| **Polling** | Low | Simple updates | Universal |
| **Long Polling** | Medium | Real-time with HTTP | Universal |

## Production Considerations

- **Scalability**: SSE connections are persistent HTTP connections
- **Load Balancing**: Requires sticky sessions or shared state
- **Memory**: Each connection consumes server memory
- **Timeouts**: Configure appropriate connection timeouts
- **Security**: Same CORS and authentication considerations as regular HTTP

SSE is perfect for this log streaming use case because it's simple, reliable, and exactly what we need for one-way real-time data flow!
