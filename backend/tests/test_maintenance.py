"""验证轻量维护脚本。"""

from datetime import timedelta

from sqlalchemy import select

from app.core.security import utc_now
from app.models import RefreshSession
from scripts.cleanup_refresh_sessions import cleanup_expired_refresh_sessions


def test_cleanup_removes_only_expired_refresh_sessions(db_session, test_user):
    now = utc_now()
    db_session.add_all(
        [
            RefreshSession(
                user_id=test_user.id,
                family_id="expired-family",
                token_hash="a" * 64,
                expires_at=now - timedelta(seconds=1),
            ),
            RefreshSession(
                user_id=test_user.id,
                family_id="active-family",
                token_hash="b" * 64,
                expires_at=now + timedelta(days=1),
            ),
        ]
    )
    db_session.commit()

    deleted_count = cleanup_expired_refresh_sessions(db_session)
    db_session.commit()

    remaining_families = set(db_session.scalars(select(RefreshSession.family_id)).all())
    assert deleted_count == 1
    assert remaining_families == {"active-family"}
