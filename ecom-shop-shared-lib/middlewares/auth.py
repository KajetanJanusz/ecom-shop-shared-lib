import datetime
from typing import Literal

import jwt
from fastapi import Request
from pydantic import BaseModel, ValidationError
from starlette.responses import JSONResponse


class TokenPayload(BaseModel):
    user_id: str
    exp: datetime.datetime
    type: Literal["access", "refresh"]
    admin: bool


class AuthMiddleware:
    def __init__(self, key: str, algorithm: str):
        self.key = key
        self.algorithm = algorithm

    async def __call__(self, request: Request, call_next):
        token = request.headers.get("Authorization", None)

        if not token or not isinstance(token, str):
            return JSONResponse(content="Token is missing", status_code=401)

        if not token.startswith("Bearer "):
            return JSONResponse(content="Token is invalid", status_code=401)

        parsed_token = token.removeprefix("Bearer ")

        try:
            decoded = jwt.decode(
                parsed_token,
                key=self.key,
                algorithms=[
                    self.algorithm,
                ],
            )
            token_payload = TokenPayload.model_validate(decoded)
        except (jwt.InvalidTokenError, jwt.DecodeError, ValidationError):
            return JSONResponse(content="Token is invalid or expired", status_code=401)

        request.state.user = token_payload

        response = await call_next(request)

        return response
