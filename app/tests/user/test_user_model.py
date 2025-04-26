# tests/user/test_user_model.py
from app.models.user import User, UserRole


def test_user_repr():
    user = User(id=1, email="john@example.com", role=UserRole.ADMIN)
    assert repr(user) == (
        "<User(id=1, email=john@example.com, role=admin)>"
    )


def test_is_superuser():
    user = User(role=UserRole.ADMIN)
    assert user.is_superuser is True

    guest = User(role=UserRole.GUEST)
    assert guest.is_superuser is False
