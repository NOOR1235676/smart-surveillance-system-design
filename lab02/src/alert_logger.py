"""AlertLogger: persists detections and raises alerts."""
from typing import List
from interfaces import Frame, Detection


class AlertLogger:
    """Responsibility: write detection logs, evaluate alert rules, notify."""

    def __init__(self, db_path: str = "detections.db",
                 alert_labels: List[str] = None,
                 min_confidence: float = 0.6,
                 cooldown_seconds: int = 30) -> None:
        self.db_path = db_path
        self.alert_labels = alert_labels or ["person"]
        self.min_confidence = min_confidence
        self.cooldown_seconds = cooldown_seconds

    def log(self, detections: List[Detection], frame: Frame) -> int:
        """Store detections (timestamp, camera, bbox, label, conf).
        Returns number of records written."""
        raise NotImplementedError

    def should_alert(self, detections: List[Detection]) -> bool:
        """Apply rules (label, confidence, cooldown). Returns True if alert needed."""
        raise NotImplementedError

    def send_alert(self, detections: List[Detection], frame: Frame) -> bool:
        """Save snapshot and dispatch notification. Returns True on success."""
        raise NotImplementedError
