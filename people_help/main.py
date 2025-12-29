import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import db
from .routes import auth_routes

app = FastAPI(
    title="People Help The People API",
    version="1.0.0"
)

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

@app.on_event("startup")
async def startup():
    print("🚀 Starting server...")
    db.init()
    await db.create_all()
    print("✅ Database initialized successfully")

@app.on_event("shutdown")
async def shutdown():
    await db.close()
    print("🛑 Database connection closed")

@app.get("/")
async def root():
    return {"message": "People Help The People API"}

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8888)