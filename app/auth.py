from fastapi import HTTPException
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY"),
)

def signup_user(email: str, password: str):
    try:
        response = supabase.auth.sign_up({
            "email": email,
            "password": password,
        })
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail="Signup failed",
        ) from exc

    if response.user is None:
        raise HTTPException(status_code=400, detail="Signup failed")

    return response

def login_user(email: str, password: str):
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password,
        })
    except Exception as exc:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
        ) from exc

    if response.user is None or response.session is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return response

def get_current_user(access_token: str):
    try:
        response = supabase.auth.get_user(access_token)
    except Exception as exc:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
        ) from exc

    if response.user is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return response.user

def logout_user(access_token: str):
    try:
        supabase.auth.admin.sign_out(access_token, "global")
    except Exception as exc:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
        ) from exc
