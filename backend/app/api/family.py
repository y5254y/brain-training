"""
家人关注接口模块
子女可绑定父母账号，远程查看训练情况
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.family import FamilyBindRequest
from app.services.auth_service import AuthService
from app.services.family_service import FamilyService

router = APIRouter()


@router.post("/invite-code", summary="生成邀请码")
async def generate_invite_code(
    current_user=Depends(AuthService.get_current_user),
    db: Session = Depends(get_db),
):
    """
    生成6位数字邀请码，有效期30分钟
    将邀请码分享给家人，家人输入后即可绑定
    """
    family_service = FamilyService(db)
    result = family_service.generate_invite_code(current_user.id)
    return result


@router.post("/bind", summary="绑定家人账号")
async def bind_family(
    bind_data: FamilyBindRequest,
    current_user=Depends(AuthService.get_current_user),
    db: Session = Depends(get_db),
):
    """
    通过邀请码绑定家人账号
    - invite_code: 家人分享的6位邀请码
    """
    family_service = FamilyService(db)
    try:
        result = family_service.bind_family(current_user.id, bind_data.invite_code)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/list", summary="获取关注的家人列表")
async def get_family_list(
    current_user=Depends(AuthService.get_current_user),
    db: Session = Depends(get_db),
):
    """获取当前用户关注的所有家人列表"""
    family_service = FamilyService(db)
    family_list = family_service.get_family_list(current_user.id)
    return {"family_list": family_list, "total": len(family_list)}


@router.get("/{family_id}/report", summary="查看家人训练报告")
async def get_family_report(
    family_id: int,
    current_user=Depends(AuthService.get_current_user),
    db: Session = Depends(get_db),
):
    """
    查看绑定家人的训练报告
    - family_id: 家人的用户ID
    包含训练数据、能力雷达图、异常预警等
    """
    family_service = FamilyService(db)
    try:
        report = family_service.get_family_report(current_user.id, family_id)
        return report
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.delete("/unbind/{relation_id}", summary="解除家人绑定")
async def unbind_family(
    relation_id: int,
    current_user=Depends(AuthService.get_current_user),
    db: Session = Depends(get_db),
):
    """解除对指定家人账号的关注"""
    family_service = FamilyService(db)
    try:
        family_service.unbind_family(current_user.id, relation_id)
        return {"message": "已解除关注", "relation_id": relation_id}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
