from typing import List, Union, Callable, Dict, Coroutine
import file_manager
import info_aggregator
import time
import asyncio

GLOBAL_LOG_LEVEL = 1


class ProgressListener:
    progress: float = 0
    on_complete: Callable[[], Coroutine]
    on_progress: Callable[[float], Coroutine]
    on_error: Callable[[str], Coroutine]
    on_start: Callable[[], Coroutine]
    log_level: int = GLOBAL_LOG_LEVEL

    def __init__(self, on_progress, on_complete=None, on_error=None, on_start=None):
        self.on_complete = on_complete
        self.on_progress = on_progress
        self.on_error = on_error
        self.on_start = on_start

    async def start(self):
        if self.log_level > 0:
            print("ProgListener start.")
        if self.on_start is not None:
            await self.on_start()

    async def set_progress(self, value):
        if self.log_level > 0:
            print("ProgListener set_progress ", value)
        await self.on_progress(value)
        self.progress = value

    async def end(self):
        if self.log_level > 0:
            print("ProgListener end.")
        if self.on_complete is not None:
            await self.on_complete()

    async def fail(self, reason):
        if self.log_level > 0:
            print("ProgListener fail.")
        if self.on_error is not None:
            await self.on_error(reason)

class Request:
    id: str
    pl: ProgressListener

    def __init__(self, rid):
        self.id = rid

    def set_progress_listener(self, pl: ProgressListener):
        self.pl = pl

    async def execute(self) -> Dict:
        raise NotImplementedError("Base class execute called")


class BatchLoadRequest(Request):
    async def execute(self) -> Dict:
        await self.pl.start()
        results = file_manager.getall().to_dict()
        await self.pl.end()
        return results


class SingleLoadRequest(Request):
    uri: str

    def __init__(self, rid, uri):
        super().__init__(rid)
        self.uri = uri

    async def execute(self, progress_listener: ProgressListener = None) -> Dict:
        return info_aggregator.save_playlist(self.uri, self.pl).to_dict()


class ProgressTestRequest(Request):
    async def execute(self) -> Dict:
        await self.pl.start()
        for i in range(10):
            await asyncio.sleep(0.5)
            await self.pl.set_progress(i * 10)
        await self.pl.end()
        return {'time': 1}


def form_request(obj: Dict) -> Request:
    if 'id' not in obj:
        raise ValueError("Request id not found")
    req_id = obj['id']

    if 'cmd' not in obj:
        raise ValueError("Request cmd not found")
    req_cmd = obj['cmd']

    if req_cmd == 'getall':
        return BatchLoadRequest(req_id)

    if req_cmd == 'get':
        if 'uri' not in obj:
            raise ValueError("SingleLoadRequest uri not found")
        req_uri = obj['uri']
        return SingleLoadRequest(req_id, req_uri)

    if req_cmd == 'test':
        cmd_type = obj['type']
        if cmd_type == 'progress':
            return ProgressTestRequest(req_id)
