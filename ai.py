from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_BASE = "https://sii3.moayman.top/api/veo3.php"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

@app.get("/generate")
async def generate_get(text: str, link: str = None):
    params = {"text": text}
    if link:
        params["link"] = link

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(API_BASE, params=params, headers=HEADERS, timeout=60)
            response.raise_for_status()
            if not response.text.strip():
                return JSONResponse(content={"success": False, "error": "Empty response from remote API"})
            return JSONResponse(content={"success": True, "data": response.text})
        except httpx.HTTPError as e:
            return JSONResponse(content={"success": False, "error": str(e)})

@app.post("/generate")
async def generate_post(text: str = Form(...), link: str = Form(None)):
    data = {"text": text}
    if link:
        data["link"] = link

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(API_BASE, data=data, headers=HEADERS, timeout=60)
            response.raise_for_status()
            if not response.text.strip():
                return JSONResponse(content={"success": False, "error": "Empty response from remote API"})
            return JSONResponse(content={"success": True, "data": response.text})
        except httpx.HTTPError as e:
            return JSONResponse(content={"success": False, "error": str(e)})
