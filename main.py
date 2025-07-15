# Main
from fastapi import FastAPI, Request, Response, HTTPException
from slowapi.middleware import SlowAPIMiddleware

from api.core_functions.limiter import limiter

import httpx
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    docs_url=None,
    redoc_url=None,
    openapi_url=None
)

web_url = "http://localhost:8001"
api_url = "http://localhost:8002"

app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Expires"] = "0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Referrer-Policy"] = "same-origin"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Access-Control-Allow-Methodes"] = "GET, POST"
    response.headers["Access-Control-Allow-Origin"] = "*"

    return response

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy(request: Request, path: str):
    print(f"Received request for path: {path}")
    referer = request.headers.get('referer')
    print(f"Referer of request: {referer}")
    if referer and "/api/" in referer:
        if path.startswith("openapi.json"):
            target_url = f"{api_url}/openapi.json"
            print(f"Target URL for OpenAPI: {target_url}")

        elif path.startswith("redoc"):
            target_url = f"{api_url}/redoc"
            print(f"Target URL for Redoc: {target_url}")

    elif path.startswith("api/"):
        sub_path = path[4:] if path.startswith("api/") else ""
        print(f"Sub-path for API: {sub_path}")
        target_url = f"{api_url}/{sub_path}"
        print(f"Target URL for API: {target_url}")

    else:
        target_url = f"{web_url}/{path}"
        print(f"Target URL for non-API: {target_url}")

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
        logger.error(f"Timeout when calling {target_url}")
        raise HTTPException(status_code=504, detail=f"Gateway Timeout: Target server {target_url} not reachable")
    except httpx.ConnectError:
        logger.error(f"Connection error to {target_url}")
        raise HTTPException(status_code=502, detail=f"Bad Gateway: Cannot connect to {target_url}")
    except Exception as e:
        logger.error(f"Unknown error when proxying to {target_url}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)