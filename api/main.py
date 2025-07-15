# API
from fastapi import FastAPI, Request
from slowapi.middleware import SlowAPIMiddleware

from core_functions.limiter import limiter

from endpoints.endpoints import router as endpoints_router
from endpoints.user_endpoints import router as user_endpoints_router

app = FastAPI(
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

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

app.include_router(endpoints_router)
app.include_router(user_endpoints_router)