"""Shared data types for the CV pipeline."""
from dataclasses import dataclass
from typing import Tuple
import numpy as np


@dataclass
class Frame:
    image: np.ndarray          # BGR image, shape (H, W, 3)
    timestamp: float           # Unix time (seconds)
    camera_id: str = "cam0"


@dataclass
class Detection:
    bbox: Tuple[float, float, float, float]  # (x1, y1, x2, y2) in pixels
    label: str
    confidence: float          # 0.0 - 1.0
