"""
认证业务逻辑服务
处理用户注册、登录、Token 验证等逻辑
"""
from datetime import datetime
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import verify_password, hash_password, create_access_token, decode_token
from app.models.user import User
from app.schemas.user import UserCreate, Token

# OAuth2 Bearer Token 验证方案
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


class AuthService:
    """认证服务类"""

    def __init__(self, db: Session):
        self.db = db

    def get_user_by_username(self, username: str) -> Optional[User]:
        """根据用户名查询用户"""
        return self.db.query(User).filter(User.username == username).first()

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """根据ID查询用户"""
        return self.db.query(User).filter(User.id == user_id).first()

    def create_user(self, user_data: UserCreate) -> User:
        """创建新用户"""
        # 对密码进行哈希处理
        password_hash = hash_password(user_data.password)
        db_user = User(
            username=user_data.username,
            password_hash=password_hash,
            nickname=user_data.nickname or user_data.username,
            age_group=user_data.age_group,
            phone=user_data.phone,
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """验证用户名和密码"""
        user = self.get_user_by_username(username)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user

    def create_access_token(self, user: User) -> Token:
        """为用户创建 JWT Token"""
        token_data = {"sub": str(user.id), "username": user.username}
        access_token = create_access_token(data=token_data)
        return Token(
            access_token=access_token,
            token_type="bearer",
            user=user,
        )

    def update_user(self, user_id: int, update_data: dict) -> User:
        """更新用户信息"""
        user = self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        # 只允许更新以下字段
        allowed_fields = {"nickname", "avatar", "phone"}
        for key, value in update_data.items():
            if key in allowed_fields:
                setattr(user, key, value)
        user.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(user)
        return user

    @staticmethod
    async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db),
    ) -> User:
        """从 JWT Token 中获取当前登录用户（依赖注入）"""
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )
        payload = decode_token(token)
        if payload is None:
            raise credentials_exception
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        user = db.query(User).filter(User.id == int(user_id)).first()
        if user is None:
            raise credentials_exception
        return user
