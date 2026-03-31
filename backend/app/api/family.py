"""
家人关注接口模块
子女可绑定父母账号，远程查看训练情况
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/bind", summary="绑定家人账号")
async def bind_family(
    family_username: str,
    current_user=Depends(AuthService.get_current_user),
    db: Session = Depends(get_db),
):
    """
    绑定家人账号
    - family_username: 要关注的家人的用户名
    子女绑定后可查看父母的训练情况
    """
    auth_service = AuthService(db)
    family_user = auth_service.get_user_by_username(family_username)
    if not family_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="该用户不存在",
        )
    if family_user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能关注自己",
        )
    # TODO: 实现绑定逻辑（需要添加关系表）
    return {"message": f"已成功关注用户 {family_username}", "status": "success"}


@router.get("/list", summary="获取关注的家人列表")
async def get_family_list(
    current_user=Depends(AuthService.get_current_user),
    db: Session = Depends(get_db),
):
    """获取当前用户关注的所有家人列表"""
    # TODO: 实现获取家人列表逻辑
    return {"family_list": [], "total": 0}


@router.get("/{family_id}/report", summary="查看家人训练报告")
async def get_family_report(
    family_id: int,
    current_user=Depends(AuthService.get_current_user),
    db: Session = Depends(get_db),
):
    """
    查看绑定家人的训练报告
    - family_id: 家人的用户ID
    需要先绑定才能查看
    """
    # TODO: 验证是否已绑定该家人，然后返回其训练报告
    return {"message": "家人训练报告功能开发中", "family_id": family_id}


@router.delete("/unbind/{family_id}", summary="解除家人绑定")
async def unbind_family(
    family_id: int,
    current_user=Depends(AuthService.get_current_user),
    db: Session = Depends(get_db),
):
    """解除对指定家人账号的关注"""
    # TODO: 实现解除绑定逻辑
    return {"message": "已解除关注", "family_id": family_id}
