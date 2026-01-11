from __future__ import annotations

import logging
import sys

from app.common.context import request_id_var, tenant_id_var


class ContextFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_var.get() or "-"
        record.tenant_id = tenant_id_var.get() or "-"
        return True


def setup_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(levelname)s %(asctime)s %(name)s request_id=%(request_id)s tenant_id=%(tenant_id)s %(message)s",
        stream=sys.stdout,
    )
    logging.getLogger().addFilter(ContextFilter())
