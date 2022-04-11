import asyncio
import websockets
import json
from req_types import Request, ProgressListener, form_request


async def handler(websocket, path):
    print("Connection made")
    async for message in websocket:
        response = await handle_message(websocket, message)
        print("Sending ...", response)
        await websocket.send(response)


async def handle_message(websocket: websockets.WebSocketServerProtocol, message: str) -> str:
    print("Received message ", message)
    req_data = json.loads(message)
    request = form_request(req_data)

    async def on_start(): await websocket.send(json.dumps({'id': request.id, 'percent': 0}))
    async def on_progress(value): await websocket.send(json.dumps({'id': request.id, 'percent': value}))
    async def on_complete(): await websocket.send(json.dumps({'id': request.id, 'percent': 100}))
    async def on_error(reason): await websocket.send(json.dumps({'id': request.id, 'error': reason}))
    progress_listener = ProgressListener(on_progress, on_complete, on_error, on_start)
    request.set_progress_listener(progress_listener)

    return json.dumps({
        'id': request.id,
        'data': await request.execute()
    })


start_server = websockets.serve(handler, "127.0.0.1", 8888)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
