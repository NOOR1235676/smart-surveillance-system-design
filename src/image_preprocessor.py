"""ImagePreprocessor: converts raw frames into model-ready tensors."""
from typing import List, Tuple
import numpy as np
from interfaces import Frame, Detection


class ImagePreprocessor:
    """Responsibility: letterbox resize, BGR->RGB, normalize, NCHW layout."""

    def __init__(self, target_size: Tuple[int, int] = (640, 640),
                 mean: float = 0.0, std: float = 255.0) -> None:
        self.target_size = target_size
        self.mean = mean
        self.std = std

    def process(self, frame: Frame) -> np.ndarray:
        """Input: Frame. Output: float32 tensor of shape (1, 3, H, W)."""
        raise NotImplementedError

    def scale_boxes_back(self, detections: List[Detection],
                         frame: Frame) -> List[Detection]:
        """Map boxes from model input space back to original frame coordinates."""
        raise NotImplementedError
