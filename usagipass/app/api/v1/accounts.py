import string

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

from usagipass.app.database import require_session
from usagipass.app.models import AccountServer, User, UserAccount

router = APIRouter()


class UserAccountSensitive(SQLModel):
    account_name: str
    account_server: AccountServer
    account_password: str


async def require_token(token: str, session: AsyncSession = Depends(require_session)):
    if all(c in string.hexdigits for c in token):
        if user := (await session.exec(select(User).where(User.api_token == token))).first():
            return user
        raise HTTPException(status_code=403, detail="Token 无效或已过期")
    raise HTTPException(status_code=400, detail="Token 不是有效的十六进制字符串")


@router.get("/accounts", response_model=list[UserAccountSensitive])
async def get_accounts(user: User = Depends(require_token), session: AsyncSession = Depends(require_session)):
    accounts = await session.exec(select(UserAccount).where(UserAccount.username == user.username))
    return [UserAccountSensitive.model_validate(account) for account in accounts]
