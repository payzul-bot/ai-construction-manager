from __future__ import annotations

from jose import jwt
from jose.exceptions import JWTError


class JwtVerifier:
    def __init__(self, secret: str, issuer: str, audience: str):
        self.secret = secret
        self.issuer = issuer
        self.audience = audience

    def verify(self, token: str) -> dict:
        try:
            return jwt.decode(
                token,
                self.secret,
                algorithms=["HS256"],
                issuer=self.issuer,
                audience=self.audience,
                options={"require_aud": True, "require_iss": True},
            )
        except JWTError as e:
            raise ValueError(str(e)) from e
