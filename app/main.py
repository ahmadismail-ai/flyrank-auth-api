from fastapi import FastAPI, Header, HTTPException
from app.models import AuthRequest
from app.auth import signup_user, login_user, get_current_user

app = FastAPI(
    title="FlyRank Auth API",
    description="Secure authentication API using FastAPI and Supabase Auth",
    version="1.0.0",
)

@app.get("/")
def root():
    return {"message": "FlyRank Auth API is running"}

@app.post("/auth/signup")
def signup(request: AuthRequest):
    response = signup_user(request.email, request.password)
    return {
        "message": "Signup successful",
        "user": response.user.model_dump() if response.user else None,
    }

@app.post("/auth/login")
def login(request: AuthRequest):
    response = login_user(request.email, request.password)
    return {
        "message": "Login successful",
        "access_token": response.session.access_token,
        "refresh_token": response.session.refresh_token,
        "user": response.user.model_dump(),
    }

@app.get("/auth/me")
def me(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Authorization header must use Bearer token",
        )

    access_token = authorization.removeprefix("Bearer ").strip()

    if not access_token:
        raise HTTPException(status_code=401, detail="Access token is required")

    user = get_current_user(access_token)

    return {
        "user": user.model_dump(),
    }
