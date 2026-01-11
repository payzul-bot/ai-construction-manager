from app.infra.db.models.audit_event import AuditEvent


class AuditRepo:
    def __init__(self, session):
        self.session = session

    def log(
        self,
        *,
        tenant_id: str,
        actor: str,
        action: str,
        entity_type: str,
        entity_id: str,
        payload: dict | None = None,
    ) -> None:
        event = AuditEvent(
            tenant_id=tenant_id,
            actor=actor,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            payload=payload or {},
        )
        self.session.add(event)
