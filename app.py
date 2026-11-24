import os
import time
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

FOOTBALL_TOKEN = os.getenv("FOOTBALL_DATA_TOKEN", "bf0361af62ba447581a3f1ca107d9828")
CACHE = {"timestamp": 0, "data": None}
CACHE_TTL = 120  # Caché de 2 minutos para cuidar las peticiones de la API gratuita


@app.get("/")
async def serve_app():
    return FileResponse("index.html")


@app.get("/api/laliga")
async def get_laliga_matches():
    now = time.time()
    if CACHE["data"] and (now - CACHE["timestamp"] < CACHE_TTL):
        return CACHE["data"]

    url = "https://api.football-data.org/v4/competitions/PD/matches"
    headers = {"X-Auth-Token": FOOTBALL_TOKEN}

    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(url, headers=headers)

    if resp.status_code != 200:
        raise HTTPException(
            status_code=resp.status_code,
            detail="Error consultando Football-data.org",
        )

    data = resp.json()
    CACHE["timestamp"] = now
    CACHE["data"] = data
    return data