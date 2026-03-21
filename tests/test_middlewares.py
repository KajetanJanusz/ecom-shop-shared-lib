import datetime
import uuid

import jwt
import pytest
from starlette.datastructures import Headers
from starlette.requests import Request
from starlette.responses import Response

from shared.middlewares.auth import AuthMiddleware, TokenPayload

_KEY = "123456789123456789123456789123456789"
_ALGORITHM = "HS256"


def _make_token(
    user_id: str = str(uuid.uuid4()),
    token_type: str = "access",
    admin: bool = False,
    exp_delta_seconds: int = 3600,
) -> str:
    payload = {
        "user_id": user_id,
        "type": token_type,
        "admin": admin,
        "exp": datetime.datetime.now(datetime.timezone.utc)
        + datetime.timedelta(seconds=exp_delta_seconds),
    }
    return jwt.encode(payload, _KEY, algorithm=_ALGORITHM)


def _make_request(headers: dict[str, str] | None = None) -> Request:
    raw_headers = Headers(headers=headers or {}).raw
    scope = {"type": "http", "method": "GET", "path": "/", "headers": raw_headers}
    return Request(scope)


async def _call_next(_request: Request) -> Response:
    return Response(status_code=200)


@pytest.fixture
def middleware() -> AuthMiddleware:
    return AuthMiddleware(key=_KEY, algorithm=_ALGORITHM)


class TestAuthMiddleware:
    async def test_when_authorization_header_missing_returns_401(self, middleware):
        # Arrange
        request = _make_request()

        # Act
        response = await middleware(request, _call_next)

        # Assert
        assert response.status_code == 401

    async def test_when_token_has_no_bearer_prefix_returns_401(self, middleware):
        # Arrange
        request = _make_request({"Authorization": _make_token()})

        # Act
        response = await middleware(request, _call_next)

        # Assert
        assert response.status_code == 401

    async def test_when_token_is_malformed_returns_401(self, middleware):
        # Arrange
        request = _make_request({"Authorization": "Bearer not.a.valid.jwt"})

        # Act
        response = await middleware(request, _call_next)

        # Assert
        assert response.status_code == 401

    async def test_when_token_is_expired_returns_401(self, middleware):
        # Arrange
        expired_token = _make_token(exp_delta_seconds=-1)
        request = _make_request({"Authorization": f"Bearer {expired_token}"})

        # Act
        response = await middleware(request, _call_next)

        # Assert
        assert response.status_code == 401

    async def test_when_token_signed_with_wrong_key_returns_401(self, middleware):
        # Arrange
        token = jwt.encode(
            {"user_id": "u1", "type": "access", "admin": False},
            "wrong-key-1234567812345678943124234143",
            algorithm=_ALGORITHM,
        )
        request = _make_request({"Authorization": f"Bearer {token}"})

        # Act
        response = await middleware(request, _call_next)

        # Assert
        assert response.status_code == 401

    async def test_when_token_payload_schema_mismatch_returns_401(self, middleware):
        # Arrange
        token = jwt.encode({"sub": "someone"}, _KEY, algorithm=_ALGORITHM)
        request = _make_request({"Authorization": f"Bearer {token}"})

        # Act
        response = await middleware(request, _call_next)

        # Assert
        assert response.status_code == 401

    async def test_when_valid_token_returns_200(self, middleware):
        # Arrange
        request = _make_request({"Authorization": f"Bearer {_make_token()}"})

        # Act
        response = await middleware(request, _call_next)

        # Assert
        assert response.status_code == 200

    async def test_when_valid_token_sets_user_on_request_state(self, middleware):
        # Arrange
        user_id = str(uuid.uuid4())
        request = _make_request(
            {"Authorization": f"Bearer {_make_token(user_id=user_id)}"}
        )

        # Act
        await middleware(request, _call_next)

        # Assert
        assert isinstance(request.state.user, TokenPayload)
        assert request.state.user.user_id == user_id

    async def test_when_admin_token_sets_admin_true_on_request_state(self, middleware):
        # Arrange
        request = _make_request({"Authorization": f"Bearer {_make_token(admin=True)}"})

        # Act
        await middleware(request, _call_next)

        # Assert
        assert request.state.user.admin is True

    async def test_when_refresh_token_sets_correct_type_on_request_state(
        self, middleware
    ):
        # Arrange
        request = _make_request(
            {"Authorization": f"Bearer {_make_token(token_type='refresh')}"}
        )

        # Act
        await middleware(request, _call_next)

        # Assert
        assert request.state.user.type == "refresh"
