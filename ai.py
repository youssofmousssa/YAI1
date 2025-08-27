from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx

app = FastAPI(
    title="DarkAI Unified API",
    description="Generate videos from text or image and edit images using GPT-5",
    version="1.0.0"
)

# ---------- Enable CORS ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Remote API Bases ----------
VIDEO_API = "https://sii3.moayman.top/api/veo3.php"       # Text-to-video & Image-to-video
IMG_EDIT_API = "https://sii3.moayman.top/api/gpt-img.php" # GPT-5 Image Editing
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

# ---------- Helper Function ----------
async def forward_request(api_url: str, method: str, payload: dict):
    """Forward request to remote API and normalize JSON response"""
    async with httpx.AsyncClient() as client:
        try:
            if method.upper() == "GET":
                response = await client.get(api_url, params=payload, headers=HEADERS, timeout=60)
            else:
                response = await client.post(api_url, data=payload, headers=HEADERS, timeout=60)

            response.raise_for_status()
            
            # Try to parse JSON, fallback to text
            try:
                parsed = response.json()
            except Exception:
                parsed = response.text.strip()

            if not parsed:
                return {"success": False, "error": "Empty response from remote API"}

            return {"success": True, "data": parsed}

        except httpx.HTTPError as e:
            return {"success": False, "error": str(e)}

# ---------- Video Endpoints ----------
@app.get("/generate")
async def generate_get(text: str, link: str = None):
    """
    Generate video using GET request.
    - text: description of video
    - link: optional image URL for image-to-video
    """
    payload = {"text": text}
    if link:
        payload["link"] = link
    result = await forward_request(VIDEO_API, "GET", payload)
    return JSONResponse(content=result)

@app.post("/generate")
async def generate_post(text: str = Form(...), link: str = Form(None)):
    """
    Generate video using POST request.
    - text: description of video
    - link: optional image URL for image-to-video
    """
    payload = {"text": text}
    if link:
        payload["link"] = link
    result = await forward_request(VIDEO_API, "POST", payload)
    return JSONResponse(content=result)

# ---------- GPT-5 Image Editing Endpoints ----------
@app.get("/edit-img")
async def edit_img_get(text: str, link: str):
    """
    Edit an image using GET request.
    - text: prompt for GPT-5 image editing
    - link: image URL to edit
    """
    payload = {"text": text, "link": link}
    result = await forward_request(IMG_EDIT_API, "GET", payload)
    return JSONResponse(content=result)

@app.post("/edit-img")
async def edit_img_post(text: str = Form(...), link: str = Form(...)):
    """
    Edit an image using POST request.
    - text: prompt for GPT-5 image editing
    - link: image URL to edit
    """
    payload = {"text": text, "link": link}
    result = await forward_request(IMG_EDIT_API, "POST", payload)
    return JSONResponse(content=result)
