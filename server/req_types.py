from typing import List, Union, Callable, Dict
import file_manager
import info_aggregator
import time
import asyncio

GLOBAL_LOG_LEVEL = 1


class ProgressListener:
    progress: float = 0
    on_complete: Callable[[], None]
    on_progress: Callable[[float], None]
    on_error: Callable[[str], None]
    on_start: Callable[[], None]
    log_level: int = GLOBAL_LOG_LEVEL

    def __init__(self, on_progress, on_complete=None, on_error=None, on_start=None):
        self.on_complete = on_complete
        self.on_progress = on_progress
        self.on_error = on_error
        self.on_start = on_start

    def start(self):
        if self.log_level > 0:
            print("ProgListener start.")
        if self.on_start is not None:
            self.on_start()

    def set_progress(self, value):
        if self.log_level > 0:
            print("ProgListener set_progress ", value)
        self.on_progress(value)
        self.progress = value

    def end(self):
        if self.log_level > 0:
            print("ProgListener end.")
        if self.on_complete is not None:
            self.on_complete()

    def fail(self, reason):
        if self.log_level > 0:
            print("ProgListener fail.")
        if self.on_error is not None:
            self.on_error(reason)

class Request:
    id: str
    pl: ProgressListener

    def __init__(self, rid):
        self.id = rid

    def set_progress_listener(self, pl: ProgressListener):
        self.pl = pl

    def execute(self) -> Dict:
        raise NotImplementedError("Base class execute called")


class BatchLoadRequest(Request):
    def execute(self) -> Dict:
        self.pl.start()
        results = file_manager.getall().to_dict()
        self.pl.end()
        return results


class SingleLoadRequest(Request):
    uri: str

    def __init__(self, rid, uri):
        super().__init__(rid)
        self.uri = uri

    def execute(self, progress_listener: ProgressListener = None) -> Dict:
        return info_aggregator.save_playlist(self.uri, self.pl).to_dict()


class ProgressTestRequest(Request):
    def execute(self) -> Dict:
        self.pl.start()
        for i in range(10):
            await asyncio.sleep(0.1)
            self.pl.set_progress(i / 10)
        self.pl.end()
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
