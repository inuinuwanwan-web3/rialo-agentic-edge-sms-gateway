"""Provider boundary: real provider integrations belong only in this module."""

from dataclasses import dataclass
from typing import Protocol
from uuid import uuid4


@dataclass(frozen=True)
class DeliveryResult:
    message_id: str
    status: str


class SmsProvider(Protocol):
    def deliver(self, *, to: str, from_: str, message: str) -> DeliveryResult: ...


class MockProvider:
    def deliver(self, *, to: str, from_: str, message: str) -> DeliveryResult:
        # Simulation only: no network access, persistence, or actual SMS delivery.
        return DeliveryResult(message_id=f"mock_{uuid4().hex}", status="delivered")
