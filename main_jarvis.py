from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from contextlib import asynccontextmanager
from fastapi import FastAPI
import hawk, memory.AllTools as tools, os, uvicorn, threading
from dotenv import load_dotenv
load_dotenv()



security = HTTPBasic()
USERNAME = os.getenv("API_USERNAME")
PASSWORD = os.getenv("API_PASSWORD")

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

@app.post("/save_token")
async def save_token(request: Request, dependencies=Depends(get_auth)):
    data = await request.json()  # ✅ wait for JSON to be parsed
    fcm_token = data.get("token", "")

    if not fcm_token:
        return JSONResponse(status_code=400, content={"error": "FCM token is required"})

    basic.update_env_value("FCM_TOKEN", fcm_token)

    print(f"📥 Saved FCM token: {fcm_token}")
    return {"success": True, "message": "Token saved successfully"}

# ✅ 3. POST endpoint that returns streaming response
@app.head("/hawk")
async def head_endpoint(dependencies=Depends(get_auth)):
    return {}

@app.post("/hawk")
async def stream_endpoint(request: Request, dependencies=Depends(get_auth)):
    data = await request.json()
    prompt = data.get("prompt", "")
    location = data.get("location", "")
    # hawk.stream_hawk(prompt) must yield strings for StreamingResponse
    return StreamingResponse(hawk.stream_hawk(prompt, location), media_type="text/event-stream")

@app.post("/get_location")
async def get_location(request: Request, dependencies=Depends(get_auth)):
    data = await request.json()
    location = data.get("location", "")
    return {"location": location}

@app.post("/get_reminders")
async def get_reminders(request: Request, dependencies=Depends(get_auth)):
    try:
        reminders = remtools.get_due_reminders()
        return reminders
    except Exception as e:
        print("🔥 Server Error:", str(e))
        return JSONResponse(status_code=500, content={"error": str(e)})
    
@app.post("/new_device")
async def new_device(request: Request, dependencies=Depends(get_auth)):
    data = await request.json()
    device_info = data.get("device_info", "")
    devtools.add_device(device_info)
    print(f"📥 Saved device info: {device_info}")
    return {"success": True, "message": "Device info saved successfully"}

# ✅ 4. Run the app with proper host
if __name__ == "__main__":
    uvicorn.run("main_jarvis:app", host="0.0.0.0", port=8000, reload=True)
