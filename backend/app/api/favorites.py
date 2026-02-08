"""收藏和笔记 API"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List

from app.db.database import get_db
from app.models.models import Favorite, Note, User, Case
from app.schemas.schemas import (
    FavoriteCreate, FavoriteResponse,
    NoteCreate, NoteUpdate, NoteResponse
)
from app.api.auth import get_current_user

router = APIRouter(prefix="/favorites", tags=["收藏和笔记"])


# ==================== 收藏相关 ====================

@router.post("/", response_model=FavoriteResponse, status_code=201)
async def add_favorite(
    favorite_data: FavoriteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """添加收藏"""
    # 检查案例是否存在
    result = await db.execute(select(Case).where(Case.id == favorite_data.case_id))
    case = result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="案例不存在")

    # 检查是否已收藏
    result = await db.execute(
        select(Favorite).where(
            and_(
                Favorite.user_id == current_user.id,
                Favorite.case_id == favorite_data.case_id
            )
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="已收藏该案例")

    # 创建收藏
    favorite = Favorite(
        user_id=current_user.id,
        case_id=favorite_data.case_id
    )
    db.add(favorite)
    await db.commit()
    await db.refresh(favorite)

    return favorite


@router.delete("/{case_id}", status_code=204)
async def remove_favorite(
    case_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """取消收藏"""
    result = await db.execute(
        select(Favorite).where(
            and_(
                Favorite.user_id == current_user.id,
                Favorite.case_id == case_id
            )
        )
    )
    favorite = result.scalar_one_or_none()

    if not favorite:
        raise HTTPException(status_code=404, detail="未收藏该案例")

    await db.delete(favorite)
    await db.commit()


@router.get("/", response_model=List[FavoriteResponse])
async def get_favorites(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取我的收藏列表"""
    result = await db.execute(
        select(Favorite)
        .where(Favorite.user_id == current_user.id)
        .order_by(Favorite.created_at.desc())
    )
    favorites = result.scalars().all()
    return favorites


@router.get("/check/{case_id}")
async def check_favorite(
    case_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """检查是否已收藏"""
    result = await db.execute(
        select(Favorite).where(
            and_(
                Favorite.user_id == current_user.id,
                Favorite.case_id == case_id
            )
        )
    )
    favorite = result.scalar_one_or_none()
    return {"is_favorited": favorite is not None}


# ==================== 笔记相关 ====================

@router.post("/notes", response_model=NoteResponse, status_code=201)
async def create_note(
    note_data: NoteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建笔记"""
    # 检查案例是否存在
    result = await db.execute(select(Case).where(Case.id == note_data.case_id))
    case = result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="案例不存在")

    # 创建笔记
    note = Note(
        user_id=current_user.id,
        case_id=note_data.case_id,
        content=note_data.content
    )
    db.add(note)
    await db.commit()
    await db.refresh(note)

    return note


@router.get("/notes/{case_id}", response_model=List[NoteResponse])
async def get_notes(
    case_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取案例的笔记列表"""
    result = await db.execute(
        select(Note)
        .where(
            and_(
                Note.user_id == current_user.id,
                Note.case_id == case_id
            )
        )
        .order_by(Note.created_at.desc())
    )
    notes = result.scalars().all()
    return notes


@router.put("/notes/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: int,
    note_data: NoteUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新笔记"""
    result = await db.execute(
        select(Note).where(
            and_(
                Note.id == note_id,
                Note.user_id == current_user.id
            )
        )
    )
    note = result.scalar_one_or_none()

    if not note:
        raise HTTPException(status_code=404, detail="笔记不存在")

    note.content = note_data.content
    await db.commit()
    await db.refresh(note)

    return note


@router.delete("/notes/{note_id}", status_code=204)
async def delete_note(
    note_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除笔记"""
    result = await db.execute(
        select(Note).where(
            and_(
                Note.id == note_id,
                Note.user_id == current_user.id
            )
        )
    )
    note = result.scalar_one_or_none()

    if not note:
        raise HTTPException(status_code=404, detail="笔记不存在")

    await db.delete(note)
    await db.commit()
