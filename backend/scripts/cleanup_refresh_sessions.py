"""删除已经超过有效期的 Refresh Session。"""

from typing import Any, cast

from sqlalchemy import delete
from sqlalchemy.engine import CursorResult
from sqlalchemy.orm import Session

from app.core.db import SessionLocal
from app.core.logging import logger, setup_logging
from app.core.security import utc_now
from app.models import RefreshSession


def cleanup_expired_refresh_sessions(db: Session) -> int:
    result = cast(
        CursorResult[Any],
        db.execute(
            delete(RefreshSession).where(RefreshSession.expires_at <= utc_now())
        ),
    )
    return result.rowcount


def main() -> None:
    setup_logging()
    with SessionLocal.begin() as db:
        deleted_count = cleanup_expired_refresh_sessions(db)
    logger.info("已清理过期 Refresh Session | count={}", deleted_count)


if __name__ == "__main__":
    main()
