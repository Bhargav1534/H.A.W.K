from fastapi import FastAPI, Request, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from contextlib import asynccontextmanager
from requests import patch
import hawk, memory.AllTools as tools, os, uvicorn, threading, json, asyncio, time
from dotenv import load_dotenv
load_dotenv()

with open("ws_history.json", "r", encoding="utf-8") as file:
    ws_chat_history = file.read()

def write_to_server_activity(data: str):
    with open("server_activity.txt", "a", encoding="utf-8") as file:
        file.write(data + "   ⏱️ Time: " + str(time.time()) + "\n")

security = HTTPBasic()
USERNAME = os.getenv("API_USERNAME")
PASSWORD = os.getenv("API_PASSWORD")
KNOWLEDGE_FILE = "memory/knowledge.json"
UI_STATE = {
    "main": {
        "backgroundColor": "#FF5100",
        "secondaryBackgroundColor": "#4401FD", # needs update

        "textColor": "#FFFFFF",

        "profileIconColor": "#4401FD",
        "profileBackgroundColor": "#3F3E3E",

        "inputHintColor": "#FFFFFFB3",
        "inputOutlineColor": "#FFFFFF", # needs update in assistant too
        "micButtonColor": "#4401FD",
        "inputBarColor": "#0F1F33",
        "hintText": "Hey, Boss",
        "sendButtonColor": "#FFFFFF", # remove

        "chatBubbleColorUser": "#B601FD",
        "chatBubbleColorHawk": "#0F1F33",
        "chatBubbleShadowColor": "#000000", # needs update
        "chatBubbleShadowBlurRadius": 4, # needs update

        "logoBoxShadowColor": "#FFC400",
        "logoBoxShadowBlurRadius": 1200,
        "logoBoxShadowSpreadRadius": 100,
    },
    "assistant": {
        "backgroundColor": "#65789B",
        "textColor": "#FFFFFF",

        "micButtonColor": "#64FFDA",
        "inputBarColor": "#0F1F33",
        "inputOutlineColor": "#FFFFFF",
        "hintText": "Let's go, Boss",
        "inputHintColor": "#FFFFFFB3",
    }
}

class UIConnectionManager:
    def __init__(self):
        pass

    async def update_main_ui(self, patch: dict):
        UI_STATE["main"].update(patch)

        await ui_manager.broadcast({
            "type": "ui_update",
            "payload": patch
        })

    async def update_assistant_ui(self, patch: dict):
        UI_STATE["assistant"].update(patch)

        await ui_manager.broadcast({
            "type": "assistant_ui_update",
            "payload": patch
        })

    async def get_main_ui_state(self):
        return { "type": "ui_full", "payload": UI_STATE["main"]}
    
    async def get_assistant_ui_state(self):
        return UI_STATE["assistant"]

def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username != USERNAME or credentials.password != PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return True

def get_auth(auth: bool = Depends(authenticate)):
    return auth

memtools = tools.MemoryManager()
remtools = tools.RemindersManager()
devtools = tools.DeviceManager()
basic = tools.BasicTools()

def triggerer():
    remtools.trigger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    t = threading.Thread(target=triggerer, daemon=True)
    t.start()
    yield  # <--- App runs here

app = FastAPI(lifespan=lifespan, debug=False)

# ✅ 1. Add CORS to allow mobile app connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ 2. Define the request body schema (optional but cleaner)
class PromptInput(BaseModel):
    prompt: str

class NotificationRequest(BaseModel):
    fcm_token: str
    title: str
    body: str
# 🧠 Core model streaming (H.A.W.K. responses)

async def heartbeat(websocket: WebSocket):
    while True:
        try:
            await websocket.send_json({"type": "ping"})
            await asyncio.sleep(20)  # every 20s
        except:
            break

ui_manager = UIConnectionManager()


@app.get("/ui/main")
async def ui_stream(dependencies=Depends(get_auth)):
    state = await ui_manager.get_main_ui_state()
    write_to_server_activity(f"📥 Main UI state requested: {state}")
    return state

@app.get("/ui/assistant")
async def ui_assistant_stream(dependencies=Depends(get_auth)):
    state = await ui_manager.get_assistant_ui_state()
    write_to_server_activity(f"📥 Assistant UI state requested: {state}")
    return state

@app.post("/save_token")
async def save_token(request: Request, dependencies=Depends(get_auth)):
    print(time.time())
    data = await request.json()  # ✅ wait for JSON to be parsed
    fcm_token = data.get("token", "")

    if not fcm_token:
        return JSONResponse(status_code=400, content={"error": "FCM token is required"})

    basic.update_env_value("FCM_TOKEN", fcm_token)

    print(f"📥 Saved FCM token: {fcm_token}")
    write_to_server_activity(f"📥 Saved FCM token: {fcm_token}")
    return {"success": True, "message": "Token saved successfully"}

# ✅ 3. POST endpoint that returns streaming response
@app.head("/hawk")
async def head_endpoint(dependencies=Depends(get_auth)):
    print(time.time())
    write_to_server_activity(f"📥 HEAD request received at /hawk")
    return {}

@app.post("/hawk")
async def stream_endpoint(request: Request, dependencies=Depends(get_auth)):
    print(time.time())
    write_to_server_activity(f"📥 POST request received at /hawk")
    return StreamingResponse("online")

@app.websocket("/hawk")
async def hawk_ws(websocket: WebSocket):
    print(time.time())
    await websocket.accept()
    hb_task = asyncio.create_task(heartbeat(websocket))
    try:
        data = await websocket.receive_json()
        prompt = data.get("prompt", "")
        location = data.get("location", "")
        write_to_server_activity(f"📥 Prompt received via WebSocket: {prompt}")
        # ✅ stream_hawk sends directly to websocket
        await hawk.stream_hawk(websocket, prompt, location)
    except WebSocketDisconnect:
        pass
    finally:
        hb_task.cancel()

@app.get("/history")
async def get_history(dependencies=Depends(get_auth)):
    history = memtools.history()
    write_to_server_activity(f"📥 History requested, {len(history)} entries returned.")
    return history

@app.post("/get_location")
async def get_location(request: Request, dependencies=Depends(get_auth)):
    data = await request.json()
    print(f"📥 Raw data received for location: {data}")
    location = data.get("location", "")
    if location == "":
        print("⚠️ No location provided.")
    else:
        print(f"📥 Location received: {location}")
        basic.update_location_json(location)
        write_to_server_activity(f"📥 Location received: {location}")

    return {"location": location}

@app.post("/get_reminders")
async def get_reminders(request: Request, dependencies=Depends(get_auth)):
    try:
        reminders = remtools.get_due_reminders()
        write_to_server_activity(f"📥 Reminders retrieved: {len(reminders)} reminders")
        return reminders
    except Exception as e:
        print("🔥 Server Error:", str(e))
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/device_info")
async def device_info(request: Request, dependencies=Depends(get_auth)):
    data = await request.json()
    print(f"📥 Raw data received: {data}")

    device = data.get("device_info")
    if not device:
        print("⚠️ device_info field is missing in the request.")
        return {"error": "device_info missing"}

    # ✅ fingerprint is directly inside device_info
    device_id = device.get("fingerprint")
    if not device_id:
        device_id = f"{device.get('manufacturer','unknown')}_{device.get('model','unknown')}"

    print(f"📥 Device ID: {device_id}")

    with open(KNOWLEDGE_FILE, "r", encoding="utf-8") as file:
        knowledge = json.load(file)

    # ✅ Ensure devices_info is a dict
    if "devices_info" not in knowledge or not isinstance(knowledge["devices_info"], dict):
        knowledge["devices_info"] = {}

    # ✅ Store / overwrite device entry
    knowledge["devices_info"][device_id] = {
        "platform": "android",
        "type": "phone",
        "last_seen": time.time(),
        "raw": device   # store raw for now (can normalize later)
    }

    with open(KNOWLEDGE_FILE, "w", encoding="utf-8") as file:
        json.dump(knowledge, file, indent=2, ensure_ascii=False)

    print(f"📥 Device registered: {device_id}")
    write_to_server_activity(f"📥 Device registered: {device_id}")

    return {
        "status": "device info stored",
        "device_id": device_id
    }

# source: "browser-extension",
# url: location.href,
# title: document.title,
# mode: extracted.mode,
# text: extracted.text?.slice(0, MAX_CHARS) || "",
# headings: extracted.headings || [],
# paragraphs: extracted.paragraphs || [],
# links: extracted.links || [],
# // html: extracted.html || "",
# excerpt: extracted.excerpt || "",
# highlight: extra.highlight || "",
# timestamp: Date.now()

@app.post("/activity")
async def get_activity(request: Request, dependencies=Depends(get_auth)):
    data = await request.json()
    source = data.get("source", "")
    if source == "browser_extension":
        basic.update_activity_json("browser_activity", data)
    elif source == "mobile_app":
        basic.update_activity_json("phone_activity", data)
    elif source == "pc_app":
        basic.update_activity_json("pc_activity", data)
        
    print("source of data:", data.get("source", "unknown"))
    print(f"📥 Activity received: {data}")
    write_to_server_activity(f"📥 Activity received: {data}")
    return data

active_connections = []
chat = []

async def broadcast(message: dict):
    for connection in active_connections:
        print("📤 Broadcasting:", message)
        await connection.send_json(message)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, dependencies=Depends(get_auth)):
    await websocket.accept()
    active_connections.append(websocket)
    print(f"📡 New WebSocket connection established.\n {active_connections}")
    try:
        while True:
            data = await websocket.receive_json()  
            chat.append(data)
            with open("ws_history.json", "w", encoding="utf-8") as file:
                json.dump(chat, file, ensure_ascii=False, indent=4)
            print("📥 Received:", data)
            await broadcast(data)

    except WebSocketDisconnect:
        active_connections.remove(websocket)
    except Exception:
        # Handles "ping/pong timeout"
        active_connections.remove(websocket)

@app.get("/ws/history")
async def websocket_history_endpoint(dependencies=Depends(get_auth)):
    with open("ws_history.json", "r", encoding="utf-8") as file:
        history = json.load(file)
    return history

# ✅ 4. Run the app with proper host
if __name__ == "__main__":
    uvicorn.run("main_jarvis:app", host="0.0.0.0", port=8000, reload=True)
