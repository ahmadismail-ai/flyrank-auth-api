from fastapi import Depends, FastAPI, HTTPException, Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.auth import get_current_user, login_user, logout_user, signup_user
from app.models import AuthRequest

app = FastAPI(
    title="FlyRank Auth API",
    description="Secure authentication API using FastAPI and Supabase Auth",
    version="1.0.0",
)

bearer_scheme = HTTPBearer(auto_error=False)


def require_authenticated_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
):
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Access token required",
        )

    if credentials.scheme.lower() != "bearer" or not credentials.credentials.strip():
        raise HTTPException(
            status_code=401,
            detail="Access token required",
        )

    return get_current_user(credentials.credentials)


@app.get("/")
def root():
    return {"message": "FlyRank Auth API is running"}


@app.get("/public/info")
def public_info():
    return {"message": "Welcome stranger! This info is public."}

@app.post("/auth/signup", status_code=201)
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
def me(user=Depends(require_authenticated_user)):
    return {
        "user": user.model_dump(),
    }


@app.get("/protected/profile")
def protected_profile(user=Depends(require_authenticated_user)):
    return {
        "user": {
            "id": user.id,
            "email": user.email,
            "created_at": user.created_at,
        }
    }


@app.get("/protected/dashboard")
def protected_dashboard(user=Depends(require_authenticated_user)):
    return {
        "message": "Welcome to your protected dashboard",
        "user_id": user.id,
    }


@app.post("/auth/logout", status_code=204)
def logout(
    response: Response,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Access token required",
        )

    if credentials.scheme.lower() != "bearer" or not credentials.credentials.strip():
        raise HTTPException(
            status_code=401,
            detail="Access token required",
        )

    logout_user(credentials.credentials)
    response.status_code = 204
    return None
