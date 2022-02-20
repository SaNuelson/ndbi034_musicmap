import asyncio
import websockets
import json
from req_types import Request, ProgressListener, form_request


async def handler(websocket, path):
    print("Connection made")
    async for message in websocket:
        response = handle_message(websocket, message)
        print("Sending ...", response)
        await websocket.send(response)


def handle_message(websocket: websockets.WebSocketServerProtocol, message: str) -> str:
    print("Received message ", message)
    req_data = json.loads(message)
    request = form_request(req_data)

    def on_start(): websocket.send(json.dumps({'id': request.id, 'percent': 0}))
    def on_progress(value): websocket.send(json.dumps({'id': request.id, 'percent': value}))
    def on_complete(): websocket.send(json.dumps({'id': request.id, 'percent': 100}))
    def on_error(reason): websocket.send(json.dumps({'id': request.id, 'error': reason}))
    progress_listener = ProgressListener(on_progress, on_complete, on_error, on_start)
    request.set_progress_listener(progress_listener)

    return json.dumps({
        'id': request.id,
        'data': request.execute()
    })


start_server = websockets.serve(handler, "127.0.0.1", 8888)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
