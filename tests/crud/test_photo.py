"""
Tests for PhotoRepository CRUD operations.
"""

from tagline_backend_app.crud.photo import PhotoRepository
from tagline_backend_app.models import Photo


# TODO: Uncomment and implement after PhotoRepository is created
# @pytest.fixture
def sample_photo():
    return Photo(
        filename="test.jpg",
        description="A test photo",
    )


def test_create_photo(db_session):
    repo = PhotoRepository(db_session)
    photo = repo.create(filename="test.jpg", metadata={"description": "A test photo"})
    assert photo.id is not None
    assert photo.filename == "test.jpg"
    assert photo.description == "A test photo"


def test_get_photo_by_id(db_session):
    repo = PhotoRepository(db_session)
    created = repo.create(filename="test.jpg", metadata={})
    found = repo.get(created.id)
    assert found is not None
    assert found.id == created.id


def test_list_photos(db_session):
    repo = PhotoRepository(db_session)
    repo.create(filename="a.jpg", metadata={})
    repo.create(filename="b.jpg", metadata={})
    photos = repo.list()
    assert len(photos) == 2


def test_update_photo(db_session):
    repo = PhotoRepository(db_session)
    created = repo.create(filename="old.jpg", metadata={})
    updated = repo.update(created.id, filename="new.jpg", description="Updated!")
    assert (
        updated is not None
    ), "Update should return the updated Photo object, not None"
    assert updated.filename == "new.jpg"
    assert updated.description == "Updated!"


def test_delete_photo(db_session):
    repo = PhotoRepository(db_session)
    created = repo.create(filename="gone.jpg", metadata={})
    repo.delete(created.id)
    assert repo.get(created.id) is None
