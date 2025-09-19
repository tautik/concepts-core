# Short Poll vs Long Poll

## Concept
- **Short Poll**: Client pings server every second
- **Long Poll**: Client sends one request, server waits internally

## Both are polling, but:
- Short polling = Client controls timing (dumb)
- Long polling = Server controls timing (smart)

## Files
- `polling_simple.py` - Server with both endpoints
- `demo_client.py` - Test both methods

## Usage
```bash
pip install fastapi uvicorn aiohttp
python polling_simple.py
python demo_client.py
```

## Key Difference
- Short Poll: Many network requests
- Long Poll: Fewer requests, server holds connection
