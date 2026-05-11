"""Category routes for FastAPI."""

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from ..schemas import CategoryCreateRequest, CategoryUpdateRequest
from ..deps import get_current_user_id, category_storage
from ..models import Category

router = APIRouter(prefix="/api/categories", tags=["categories"])


@router.get("")
def list_categories(user_id: str = Depends(get_current_user_id)):
    categories = category_storage.get_by_user(user_id)
    return [c.to_dict() for c in categories]


@router.post("", status_code=201)
def create_category(req: CategoryCreateRequest, user_id: str = Depends(get_current_user_id)):
    if not req.name:
        return JSONResponse({"error": "name is required"}, status_code=400)
    cat = Category(
        name=req.name,
        user_id=user_id,
        color=req.color or "#3498db",
        icon=req.icon or "",
        sort_order=req.sort_order or 0,
    )
    category_storage.save(cat)
    return cat.to_dict()


@router.put("/{cat_id}")
def update_category(cat_id: str, req: CategoryUpdateRequest, user_id: str = Depends(get_current_user_id)):
    cat = category_storage.get(cat_id)
    if not cat or cat.user_id != user_id:
        return JSONResponse({"error": "not found"}, status_code=404)
    if req.name is not None:
        cat.name = req.name
    if req.color is not None:
        cat.color = req.color
    if req.icon is not None:
        cat.icon = req.icon
    if req.sort_order is not None:
        cat.sort_order = req.sort_order
    category_storage.save(cat)
    return cat.to_dict()


@router.delete("/{cat_id}")
def delete_category(cat_id: str, user_id: str = Depends(get_current_user_id)):
    cat = category_storage.get(cat_id)
    if not cat or cat.user_id != user_id:
        return JSONResponse({"error": "not found"}, status_code=404)
    category_storage.delete(cat_id)
    return {"message": "deleted"}
