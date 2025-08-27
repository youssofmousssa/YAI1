from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
import json

app = FastAPI(
    title="DarkAI Video API",
    description="Generate videos from text or text+image using a unified endpoint.",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Remote API base
API_BASE = "https://sii3.moayman.top/api/veo3.php"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}


# ---------- Helpers ----------
async def forward_request(method: str, payload: dict):
    """Forward request to remote API and normalize JSON response"""
    async with httpx.AsyncClient() as client:
        try:
            if method == "GET":
                response = await client.get(API_BASE, params=payload, headers=HEADERS, timeout=60)
            else:
                response = await client.post(API_BASE, data=payload, headers=HEADERS, timeout=60)

            response.raise_for_status()

            # Try to parse JSON
            try:
                parsed = response.json()
            except Exception:
                parsed = response.text.strip()

            if not parsed:
                return {"success": False, "error": "Empty response from remote API"}

            return {"success": True, "data": parsed}

        except httpx.HTTPError as e:
            return {"success": False, "error": str(e)}


# ---------- Endpoints ----------

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
    result = await forward_request("GET", payload)
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
    result = await forward_request("POST", payload)
    return JSONResponse(content=result)
