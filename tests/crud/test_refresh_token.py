"""
Tests for RefreshTokenRepository CRUD operations.
"""

from app.models import RefreshToken

# from app.crud.refresh_token import RefreshTokenRepository (to be implemented)


# TODO: Uncomment and implement after RefreshTokenRepository is created
# @pytest.fixture
def sample_token():
    return RefreshToken(
        token="sometoken",
        issued_at=None,
        expires_at=None,
        revoked=False,
    )


def test_create_refresh_token(db_session):
    # repo = RefreshTokenRepository(db_session)
    # token = repo.create(token="sometoken", expires_at=...)
    # assert token.id is not None
    # assert token.token == "sometoken"
    pass


def test_get_refresh_token_by_id(db_session):
    # repo = RefreshTokenRepository(db_session)
    # created = repo.create(token="sometoken", expires_at=...)
    # found = repo.get(created.id)
    # assert found is not None
    # assert found.id == created.id
    pass


def test_list_refresh_tokens(db_session):
    # repo = RefreshTokenRepository(db_session)
    # repo.create(token="tok1", expires_at=...)
    # repo.create(token="tok2", expires_at=...)
    # tokens = repo.list()
    # assert len(tokens) == 2
    pass


def test_update_refresh_token(db_session):
    # repo = RefreshTokenRepository(db_session)
    # created = repo.create(token="tok", expires_at=...)
    # updated = repo.update(created.id, revoked=True)
    # assert updated.revoked is True
    pass


def test_delete_refresh_token(db_session):
    # repo = RefreshTokenRepository(db_session)
    # created = repo.create(token="tok", expires_at=...)
    # repo.delete(created.id)
    # assert repo.get(created.id) is None
    pass
