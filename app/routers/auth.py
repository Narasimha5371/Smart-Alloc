from fastapi import APIRouter, Depends, Request, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.utils.template_renderer import render_template
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user_for_pages
from app.services.auth_service import authenticate_user, register_user, create_token_for_user
from app.models.enums import UserRole
from app.utils.security import generate_csrf_token, validate_csrf_token

router = APIRouter(tags=["auth"])
templates = Jinja2Templates(directory="app/templates")
# Keep templates available for other usages; prefer `render_template` helper


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_for_pages(request, db)
    if user:
        return RedirectResponse(url="/dashboard", status_code=302)
    csrf_token = generate_csrf_token()
    return render_template(request, "auth/login.html", {
        "csrf_token": csrf_token,
    })


@router.post("/login")
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    csrf_token: str = Form(...),
    db: Session = Depends(get_db),
):
    if not validate_csrf_token(csrf_token):
        return render_template(request, "auth/login.html", {
            "error": "Invalid session. Please try again.",
            "csrf_token": generate_csrf_token(),
        }, status_code=400)

    user = authenticate_user(db, email, password)
    if not user:
        return render_template(request, "auth/login.html", {
            "error": "Invalid email or password",
            "csrf_token": generate_csrf_token(),
        }, status_code=401)

    token = create_token_for_user(user)
    response = RedirectResponse(url="/dashboard", status_code=302)
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        max_age=1800,
    )
    return response


@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_for_pages(request, db)
    if user:
        return RedirectResponse(url="/dashboard", status_code=302)
    csrf_token = generate_csrf_token()
    return render_template(request, "auth/register.html", {
        "csrf_token": csrf_token,
        "roles": [UserRole.CLIENT],  # Only client self-registration
    })


@router.post("/register")
def register(
    request: Request,
    email: str = Form(...),
    full_name: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    csrf_token: str = Form(...),
    db: Session = Depends(get_db),
):
    if not validate_csrf_token(csrf_token):
        return render_template(request, "auth/register.html", {
            "error": "Invalid session. Please try again.",
            "csrf_token": generate_csrf_token(),
            "roles": [UserRole.CLIENT],
        }, status_code=400)

    if password != confirm_password:
        return render_template(request, "auth/register.html", {
            "error": "Passwords do not match",
            "csrf_token": generate_csrf_token(),
            "roles": [UserRole.CLIENT],
        }, status_code=400)

    if len(password) < 6:
        return render_template(request, "auth/register.html", {
            "error": "Password must be at least 6 characters",
            "csrf_token": generate_csrf_token(),
            "roles": [UserRole.CLIENT],
        }, status_code=400)

    try:
        user = register_user(db, email, full_name, password, role=UserRole.CLIENT)
    except ValueError as e:
        return render_template(request, "auth/register.html", {
            "error": str(e),
            "csrf_token": generate_csrf_token(),
            "roles": [UserRole.CLIENT],
        }, status_code=400)

    token = create_token_for_user(user)
    response = RedirectResponse(url="/dashboard", status_code=302)
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        max_age=1800,
    )
    return response


@router.get("/logout")
def logout():
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("access_token")
    return response
