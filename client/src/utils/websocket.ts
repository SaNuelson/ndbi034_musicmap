type progressCallback = (percent: number) => void;
type dataCallback = (data: object) => void;
type errorCallback = (error: string) => void;

interface dataResObj {
    id: string,
    data: object
};
interface infoResObj {
    id: string,
    percent: number
};
interface errResObj {
    id: string,
    error: string
}
type responseObj = dataResObj | infoResObj | errResObj;

function isResObj(res: object): res is responseObj {
    return "id" in res && ("percent" in res || "data" in res || "error" in res);
}

function isInfoObj(res: responseObj): res is infoResObj {
    return "percent" in res;
}

function isDataObj(res: responseObj): res is dataResObj {
    return "body" in res;
}

function isErrObj(res: responseObj): res is errResObj {
    return "error" in res;
}

enum MMRequestState {
    Idle,
    Sent,
    Processing, // for prolonged requests e.g., with loading bar
    Completed
};

class MMSocket {

    ws: WebSocket;
    isOpen: boolean = false;
    requests: MMRequest[] = [];

    constructor(url) {
        window.socket = this;
        this.setup(url);
    }

    setup(url) {
        this.ws = new WebSocket(url);
        this.ws.onopen = () => {
            console.log("Websocket to ", url, " opened.");
            this.isOpen = true;

            for (let req of this.requests) {
                if (req.state === MMRequestState.Idle) {
                    req.send(this.ws);
                }
            }
        }
        this.ws.onclose = () => {
            console.log("Websocket to ", url, " closed.");
        }
        this.ws.onmessage = this.handleMessage.bind(this);
    }

    get(uri: string, onmessage: dataCallback, onprogress: progressCallback, onerror: errorCallback) {
        let opId = uid();
        let reqBody;
        if (!uri) {
            reqBody = {id: opId, cmd: 'getall'};
        }
        else {
            reqBody = {id: opId, cmd: 'get', uri: uri};
        }
        
        let request = new MMRequest(opId, reqBody, onmessage, onprogress, onerror);
        this.requests.push(request);
        if (this.isOpen) {
            request.send(this.ws);
        }
    }

    getAll(onmessage: dataCallback, onprogress: progressCallback, onerror: errorCallback) {
        this.get(undefined, onmessage, onprogress, onerror);
    }

    progressTest(onmessage: dataCallback, onprogress:progressCallback, onerror: errorCallback) {
        let opId = uid();
        let reqBody = {id: opId, cmd: 'test', type: 'progress'}
        let request = new MMRequest(opId, reqBody, onmessage, onprogress, onerror);
        this.requests.push(request);
        if (this.isOpen) {
            request.send(this.ws);
        }
    }

    handleMessage(event: MessageEvent) {
        let message = JSON.parse(event.data);
        console.log("MMSocket received a message", message);
        if (isResObj(message)) {
            for (let i = 0; i < this.requests.length; i++) {
                let req = this.requests[i];
                if (req.owns(message)) {
                    req.proc(message);
                    if (req.state === MMRequestState.Completed) {
                        this.requests.splice(i);
                    }
                }
            }
        }
        else {
            console.error("Received incompatible message ", message);
        }
    }
}

const uid = function(){
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
}

class MMRequest {

    id: string;
    reqData: object;
    resData: object;
    onmessage: dataCallback;
    onprogress: progressCallback;
    onerror: errorCallback;
    state: MMRequestState = MMRequestState.Idle;
    percent: number = 0;

    constructor(id: string, data: object, onmessage: dataCallback, onprogress: progressCallback, onerror: errorCallback) {
        this.id = id;
        this.reqData = data;
        this.onmessage = onmessage;
        this.onprogress = onprogress;
        this.onerror = onerror;
    }

    send(ws: WebSocket): boolean {
        if (this.state != MMRequestState.Idle)
            return false;
        
        ws.send(JSON.stringify(this.reqData));
        this.state = MMRequestState.Sent;
        return true;
    }

    owns(res: responseObj): boolean {
        if (this.state != MMRequestState.Sent && this.state != MMRequestState.Processing)
            return false;
        
        if (this.id === res.id)
            return true;

        return false;
    }

    proc(res: responseObj): void {
        if (isInfoObj(res)) {
            this.state = MMRequestState.Processing;
            if (this.percent > res.percent) {
                console.warn("Received response updates in wrong order... (", this.percent, " > ", res.percent, ")");
            }
            this.percent = res.percent;
            console.log("Progressing request (", res.percent, ")")
            if (this.onprogress)
                this.onprogress(res.percent);
        }
        else if (isErrObj(res)) {
            this.state = MMRequestState.Completed;
            console.error("Unsuccessful request ", this.id);
            if (this.onerror)
                this.onerror(res.error);
        }
        else {
            this.state = MMRequestState.Completed;
            console.log("Successful request", this.id);
            if (this.onmessage)
                this.onmessage(res.data);
        }
    }
}

export default MMSocket;