from __future__ import annotations

from dataclasses import dataclass
from fastapi import HTTPException


@dataclass
class AppError(Exception):
    code: str
    message: str
    status_code: int = 400


def raise_http(err: AppError) -> None:
    raise HTTPException(status_code=err.status_code, detail={"code": err.code, "message": err.message})
