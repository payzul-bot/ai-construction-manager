from __future__ import annotations


class CalcError(Exception):
    """
    Чистая доменная ошибка (без FastAPI / HTTPException).
    Usecases/API слой сам решает, как мапить это в HTTP.
    """

    code: str = "calc_error"

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class CalcInvalidInput(CalcError):
    code = "calc_invalid_input"


class CalcUnknownWork(CalcError):
    code = "calc_unknown_work"


class CalcFailed(CalcError):
    code = "calc_failed"
