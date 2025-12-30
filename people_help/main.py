import uvicorn
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from .config import db, RATE_LIMIT_ENABLED, RATE_LIMIT_PER_MINUTE
from .routes import auth_routes, community_routes, feed_routes

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[f"{RATE_LIMIT_PER_MINUTE}/minute"] if RATE_LIMIT_ENABLED else []
)

app = FastAPI(
    title="People Help The People API",
    version="1.0.0"
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS settings
origins = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:8888",
    "http://127.0.0.1:8888",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_routes.router, prefix="/api")
app.include_router(community_routes.router, prefix="/api")
app.include_router(feed_routes.router, prefix="/api")

@app.on_event("startup")
async def startup():
    logger.info("🚀 Starting server...")
    logger.info(f"Rate limiting: {'enabled' if RATE_LIMIT_ENABLED else 'disabled'}")
    if RATE_LIMIT_ENABLED:
        logger.info(f"Rate limit: {RATE_LIMIT_PER_MINUTE} requests/minute per IP")
    db.init()
    await db.create_all()
    logger.info("✅ Database initialized successfully")

@app.on_event("shutdown")
async def shutdown():
    await db.close()
    logger.info("🛑 Database connection closed")

@app.get("/")
async def root():
    return {"message": "People Help The People API", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "ok", "rate_limiting": RATE_LIMIT_ENABLED}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8888)