from fastapi import FastAPI, Request, Response, HTTPException
import httpx
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    docs_url=None,
    redoc_url=None,
    openapi_url=None
)

TARGET_API_1 = "http://localhost:8001"
TARGET_API_2 = "http://localhost:8002"

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy(request: Request, path: str):
    if path.startswith("api"):
        sub_path = path[4:] if path.startswith("api/") else ""
        target_url = f"{TARGET_API_2}/{sub_path}"
    else:
        target_url = f"{TARGET_API_1}/{path}"

    req_headers = {k: v for k, v in request.headers.items() if k.lower() != "host"}
    req_body = await request.body()

    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(5.0)) as client:
            resp = await client.request(
                request.method,
                target_url,
                headers=req_headers,
                content=req_body,
                params=request.query_params
            )

        response_headers = {k: v for k, v in resp.headers.items() if k.lower() != "content-encoding"}
        return Response(
            content=resp.content,
            status_code=resp.status_code,
            headers=response_headers,
        )
    except httpx.TimeoutException:
        logger.error(f"Timeout beim Aufruf von {target_url}")
        raise HTTPException(status_code=504, detail=f"Gateway Timeout: Zielserver {target_url} nicht erreichbar")
    except httpx.ConnectError:
        logger.error(f"Verbindungsfehler zu {target_url}")
        raise HTTPException(status_code=502, detail=f"Bad Gateway: Kann nicht zu {target_url} verbinden")
    except Exception as e:
        logger.error(f"Unbekannter Fehler beim Proxy zu {target_url}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Interner Server Fehler: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)