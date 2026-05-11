"""Journal routes for FastAPI."""

import os
import uuid as _uuid
from datetime import date, datetime

from fastapi import APIRouter, Request, Depends, UploadFile, File
from fastapi.responses import JSONResponse

from ..schemas import JournalCreateRequest, JournalUpdateRequest, JournalCommentCreateRequest
from ..deps import get_current_user_id, journal_storage, journal_comment_storage, user_storage, JOURNAL_IMG_DIR
from ..models import Journal, JournalComment

router = APIRouter(prefix="/api/journals", tags=["journals"])


@router.get("")
def list_journals(user_id: str = Depends(get_current_user_id)):
    journals = journal_storage.get_by_user(user_id)
    return [j.to_dict() for j in journals]


@router.post("")
def create_or_update_journal(req: JournalCreateRequest, user_id: str = Depends(get_current_user_id)):
    if not req.journal_date:
        return JSONResponse({"error": "journal_date required"}, status_code=400)
    journal_date = date.fromisoformat(req.journal_date)

    existing = journal_storage.get_by_date(user_id, journal_date)
    if existing:
        existing.content = req.content if req.content is not None else existing.content
        existing.weather = req.weather if req.weather is not None else existing.weather
        existing.mood = req.mood if req.mood is not None else existing.mood
        if req.images is not None:
            existing.images = req.images
        existing.updated_at = datetime.now()
        journal_storage.save(existing)
        return existing.to_dict()

    journal = Journal(
        user_id=user_id,
        journal_date=journal_date,
        content=req.content or "",
        weather=req.weather or "",
        mood=req.mood or "",
        images=req.images or [],
    )
    journal_storage.save(journal)
    return JSONResponse(journal.to_dict(), status_code=201)


@router.get("/date/{date_str}")
def get_journal_by_date(date_str: str, user_id: str = Depends(get_current_user_id)):
    journal_date = date.fromisoformat(date_str)
    journal = journal_storage.get_by_date(user_id, journal_date)
    if not journal:
        return JSONResponse({"error": "not found"}, status_code=404)
    return journal.to_dict()


@router.post("/upload-image")
async def upload_journal_image(request: Request, user_id: str = Depends(get_current_user_id)):
    form = await request.form()
    file = form.get("image")
    if not file:
        return JSONResponse({"error": "请选择图片"}, status_code=400)

    data = await file.read()
    if len(data) > 5 * 1024 * 1024:
        return JSONResponse({"error": "图片不能超过5MB"}, status_code=400)

    ext = os.path.splitext(file.filename)[1].lower() if file.filename else '.jpg'
    if ext not in ('.jpg', '.jpeg', '.png', '.gif', '.webp'):
        ext = '.jpg'
    filename = f"{_uuid.uuid4().hex}{ext}"
    filepath = os.path.join(JOURNAL_IMG_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(data)

    url = f"/uploads/journals/{filename}"
    return {"url": url, "filename": filename}


@router.get("/{journal_id}")
def get_journal(journal_id: str, user_id: str = Depends(get_current_user_id)):
    journal = journal_storage.get(journal_id)
    if not journal or journal.user_id != user_id:
        return JSONResponse({"error": "not found"}, status_code=404)
    return journal.to_dict()


@router.put("/{journal_id}")
def update_journal(journal_id: str, req: JournalUpdateRequest, user_id: str = Depends(get_current_user_id)):
    journal = journal_storage.get(journal_id)
    if not journal or journal.user_id != user_id:
        return JSONResponse({"error": "not found"}, status_code=404)
    if req.content is not None:
        journal.content = req.content
    if req.weather is not None:
        journal.weather = req.weather
    if req.mood is not None:
        journal.mood = req.mood
    if req.images is not None:
        journal.images = req.images
    journal.updated_at = datetime.now()
    journal_storage.save(journal)
    return journal.to_dict()


@router.delete("/{journal_id}")
def delete_journal(journal_id: str, user_id: str = Depends(get_current_user_id)):
    journal = journal_storage.get(journal_id)
    if not journal or journal.user_id != user_id:
        return JSONResponse({"error": "not found"}, status_code=404)
    journal_comment_storage.delete_by_journal(journal_id)
    journal_storage.delete(journal_id)
    return {"message": "deleted"}


@router.get("/{journal_id}/comments")
def list_journal_comments(journal_id: str, user_id: str = Depends(get_current_user_id)):
    journal = journal_storage.get(journal_id)
    if not journal or journal.user_id != user_id:
        return JSONResponse({"error": "not found"}, status_code=404)
    comments = journal_comment_storage.get_by_journal(journal_id)
    result = []
    for c in comments:
        d = c.to_dict()
        user = user_storage.get_by_id(c.user_id)
        d["display_name"] = user.display_name if user else "未知"
        result.append(d)
    return result


@router.post("/{journal_id}/comments", status_code=201)
def add_journal_comment(journal_id: str, req: JournalCommentCreateRequest, user_id: str = Depends(get_current_user_id)):
    journal = journal_storage.get(journal_id)
    if not journal or journal.user_id != user_id:
        return JSONResponse({"error": "not found"}, status_code=404)
    if not req.content.strip():
        return JSONResponse({"error": "评论内容不能为空"}, status_code=400)
    comment = JournalComment(
        journal_id=journal_id,
        user_id=user_id,
        content=req.content.strip(),
    )
    journal_comment_storage.save(comment)
    d = comment.to_dict()
    user = user_storage.get_by_id(user_id)
    d["display_name"] = user.display_name if user else "未知"
    return d


@router.delete("/comments/{comment_id}")
def delete_journal_comment(comment_id: str, user_id: str = Depends(get_current_user_id)):
    comment = None
    if hasattr(journal_comment_storage, 'get'):
        comment = journal_comment_storage.get(comment_id)
    if not comment:
        return JSONResponse({"error": "not found"}, status_code=404)
    if comment.user_id != user_id:
        return JSONResponse({"error": "not found"}, status_code=404)
    journal_comment_storage.delete(comment_id)
    return {"message": "deleted"}
