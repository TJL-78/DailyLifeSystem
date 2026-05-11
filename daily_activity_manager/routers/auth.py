"""Auth routes for FastAPI."""

import os
import re
import random
import base64
import logging
from datetime import datetime, timedelta

from fastapi import APIRouter, Request, Depends, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse

from ..schemas import (
    RegisterRequest, LoginRequest, SmsSendRequest, SmsLoginRequest,
    ProfileUpdateRequest, PasswordChangeRequest, AvatarBase64Request,
)
from ..deps import (
    user_storage, category_storage,
    get_current_user_id, _get_client_key, _check_lockout,
    _record_failed_attempt, _clear_attempts,
    _login_attempts, _sms_codes, LOGIN_MAX_ATTEMPTS,
    UPLOAD_DIR,
)
from ..models import Category
from ..user_model import User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", status_code=201)
def api_register(req: RegisterRequest, request: Request):
    username = req.username.strip()
    password = req.password
    email = (req.email or "").strip()
    display_name = (req.display_name or "").strip()

    if not username or not password:
        return JSONResponse({"error": "用户名和密码不能为空"}, status_code=400)
    if len(username) < 3:
        return JSONResponse({"error": "用户名至少3个字符"}, status_code=400)
    if len(password) < 6:
        return JSONResponse({"error": "密码至少6个字符"}, status_code=400)
    if user_storage.username_exists(username):
        return JSONResponse({"error": "用户名已存在"}, status_code=409)

    user = User(
        username=username,
        password_hash=User.hash_password(password),
        email=email,
        display_name=display_name or username,
    )
    user_storage.save(user)

    defaults = [
        ("工作", "#3498db", "💼"),
        ("学习", "#9b59b6", "📚"),
        ("健身", "#27ae60", "🏃"),
        ("生活", "#f39c12", "🏠"),
        ("娱乐", "#e74c3c", "🎮"),
    ]
    for i, (name, color, icon) in enumerate(defaults):
        cat = Category(name=name, user_id=user.id, color=color, icon=icon, sort_order=i)
        category_storage.save(cat)

    request.session["user_id"] = user.id
    request.session["username"] = user.username
    return {"message": "注册成功", "user": user.to_dict()}


@router.post("/login")
def api_login(req: LoginRequest, request: Request):
    locked, remaining = _check_lockout(request)
    if locked:
        return JSONResponse({"error": f"登录尝试过多，请{remaining}秒后再试", "locked": True, "remaining": remaining}, status_code=429)

    username = req.username.strip()
    password = req.password
    if not username or not password:
        return JSONResponse({"error": "用户名和密码不能为空"}, status_code=400)

    user = user_storage.get_by_username(username)
    if not user or not User.verify_password(password, user.password_hash):
        locked, remaining = _record_failed_attempt(request)
        if locked:
            return JSONResponse({"error": f"登录尝试过多，请{remaining}秒后再试", "locked": True, "remaining": remaining}, status_code=429)
        key = _get_client_key(request)
        attempts_left = LOGIN_MAX_ATTEMPTS - _login_attempts.get(key, {}).get("count", 0)
        return JSONResponse({"error": f"用户名或密码错误，还剩{attempts_left}次机会"}, status_code=401)

    _clear_attempts(request)
    request.session["user_id"] = user.id
    request.session["username"] = user.username
    return {"message": "登录成功", "user": user.to_dict()}


@router.post("/sms/send")
def send_sms_code(req: SmsSendRequest, request: Request):
    locked, remaining = _check_lockout(request)
    if locked:
        return JSONResponse({"error": f"操作过于频繁，请{remaining}秒后再试", "locked": True, "remaining": remaining}, status_code=429)

    phone = req.phone.strip()
    if not phone or not re.match(r'^\+?[\d]{6,20}$', phone):
        return JSONResponse({"error": "手机号格式不正确"}, status_code=400)

    user = user_storage.get_by_phone(phone)
    if not user:
        return JSONResponse({"error": "该手机号未绑定任何账号"}, status_code=404)

    code = str(random.randint(100000, 999999))
    _sms_codes[phone] = {"code": code, "expires": datetime.now() + timedelta(minutes=5)}

    logger.warning(f"[SMS] Verification code for {phone}: {code}")
    print(f"\n{'='*40}\n  验证码 (Verification Code): {code}\n  手机号 (Phone): {phone}\n  有效期: 5分钟\n{'='*40}\n")

    return {"message": "验证码已发送"}


@router.post("/sms/login")
def sms_login(req: SmsLoginRequest, request: Request):
    locked, remaining = _check_lockout(request)
    if locked:
        return JSONResponse({"error": f"登录尝试过多，请{remaining}秒后再试", "locked": True, "remaining": remaining}, status_code=429)

    phone = req.phone.strip()
    code = req.code.strip()
    if not phone or not code:
        return JSONResponse({"error": "请输入手机号和验证码"}, status_code=400)

    sms_info = _sms_codes.get(phone)
    if not sms_info or sms_info["code"] != code:
        locked, remaining = _record_failed_attempt(request)
        if locked:
            return JSONResponse({"error": f"登录尝试过多，请{remaining}秒后再试", "locked": True, "remaining": remaining}, status_code=429)
        key = _get_client_key(request)
        attempts_left = LOGIN_MAX_ATTEMPTS - _login_attempts.get(key, {}).get("count", 0)
        return JSONResponse({"error": f"验证码错误，还剩{attempts_left}次机会"}, status_code=401)

    if datetime.now() > sms_info["expires"]:
        _sms_codes.pop(phone, None)
        return JSONResponse({"error": "验证码已过期，请重新获取"}, status_code=401)

    user = user_storage.get_by_phone(phone)
    if not user:
        return JSONResponse({"error": "该手机号未绑定任何账号"}, status_code=404)

    _sms_codes.pop(phone, None)
    _clear_attempts(request)
    request.session["user_id"] = user.id
    request.session["username"] = user.username
    return {"message": "登录成功", "user": user.to_dict()}


@router.get("/lockout")
def check_lockout(request: Request):
    locked, remaining = _check_lockout(request)
    return {"locked": locked, "remaining": remaining}


@router.post("/logout")
def api_logout(request: Request):
    request.session.clear()
    return {"message": "已退出登录"}


@router.get("/me")
def api_me(request: Request):
    if "user_id" not in request.session:
        return JSONResponse({"logged_in": False}, status_code=401)
    user = user_storage.get_by_id(request.session["user_id"])
    if not user:
        request.session.clear()
        return JSONResponse({"logged_in": False}, status_code=401)
    return {"logged_in": True, "user": user.to_dict()}


@router.put("/profile")
def update_profile(req: ProfileUpdateRequest, request: Request, user_id: str = Depends(get_current_user_id)):
    user = user_storage.get_by_id(user_id)
    if not user:
        return JSONResponse({"error": "not found"}, status_code=404)
    if req.display_name is not None:
        user.display_name = req.display_name
    if req.email is not None:
        user.email = req.email
    if req.phone is not None:
        phone = req.phone.strip()
        if phone and not re.match(r'^\+?[\d\s\-]{6,20}$', phone):
            return JSONResponse({"error": "手机号格式不正确"}, status_code=400)
        user.phone = phone
    user_storage.save(user)
    return {"message": "更新成功", "user": user.to_dict()}


@router.put("/password")
def change_password(req: PasswordChangeRequest, request: Request, user_id: str = Depends(get_current_user_id)):
    if not req.old_password or not req.new_password:
        return JSONResponse({"error": "请填写旧密码和新密码"}, status_code=400)
    if len(req.new_password) < 6:
        return JSONResponse({"error": "新密码至少6个字符"}, status_code=400)
    user = user_storage.get_by_id(user_id)
    if not User.verify_password(req.old_password, user.password_hash):
        return JSONResponse({"error": "旧密码错误"}, status_code=401)
    user.password_hash = User.hash_password(req.new_password)
    user_storage.save(user)
    return {"message": "密码修改成功"}


@router.post("/avatar")
async def upload_avatar(request: Request, user_id: str = Depends(get_current_user_id)):
    user = user_storage.get_by_id(user_id)
    if not user:
        return JSONResponse({"error": "not found"}, status_code=404)

    filename = f"{user.id}.png"
    filepath = os.path.join(UPLOAD_DIR, filename)

    content_type = request.headers.get("content-type", "")
    if "multipart" in content_type:
        form = await request.form()
        file = form.get("avatar")
        if not file:
            return JSONResponse({"error": "请选择头像文件"}, status_code=400)
        data = await file.read()
        if len(data) > 2 * 1024 * 1024:
            return JSONResponse({"error": "头像文件不能超过2MB"}, status_code=400)
        with open(filepath, "wb") as f:
            f.write(data)
    else:
        body = await request.json()
        if not body or not body.get("avatar_base64"):
            return JSONResponse({"error": "请提供头像数据"}, status_code=400)
        img_data = body["avatar_base64"]
        if ',' in img_data:
            img_data = img_data.split(',', 1)[1]
        try:
            raw = base64.b64decode(img_data)
        except Exception:
            return JSONResponse({"error": "头像数据格式错误"}, status_code=400)
        if len(raw) > 2 * 1024 * 1024:
            return JSONResponse({"error": "头像文件不能超过2MB"}, status_code=400)
        with open(filepath, 'wb') as f:
            f.write(raw)

    user.avatar_url = f"/uploads/avatars/{filename}"
    user_storage.save(user)
    return {"message": "头像更新成功", "avatar_url": user.avatar_url}
