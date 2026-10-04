"""ModelInferenceEngine: runs the detection model."""
from typing import List
import numpy as np
from interfaces import Detection


class ModelInferenceEngine:
    """Responsibility: load model, run inference, decode outputs, apply NMS."""

    def __init__(self, model_path: str, labels: List[str],
                 conf_threshold: float = 0.5, iou_threshold: float = 0.45,
                 device: str = "cpu") -> None:
        self.model_path = model_path
        self.labels = labels
        self.conf_threshold = conf_threshold
        self.iou_threshold = iou_threshold
        self.device = device
        self._session = None

    def load_model(self) -> None:
        """Load ONNX/TensorRT model into memory."""
        raise NotImplementedError

    def warmup(self) -> None:
        """Run a dummy inference to avoid first-call latency."""
        raise NotImplementedError

    def infer(self, tensor: np.ndarray) -> List[Detection]:
        """Input: (1,3,H,W) float32 tensor. Output: detections after
        confidence filtering and NMS."""
        raise NotImplementedError
