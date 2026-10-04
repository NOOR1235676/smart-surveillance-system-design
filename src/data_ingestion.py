"""DataIngestion: acquires frames from an RTSP stream or video file."""
from typing import Optional
from interfaces import Frame


class DataIngestion:
    """Responsibility: connect to a source, read frames, handle reconnects."""

    def __init__(self, source_uri: str, camera_id: str = "cam0",
                 max_retries: int = 5) -> None:
        self.source_uri = source_uri
        self.camera_id = camera_id
        self.max_retries = max_retries
        self._capture = None

    def connect(self) -> bool:
        """Open the stream (cv2.VideoCapture). Retry up to max_retries.
        Returns True if connected."""
        raise NotImplementedError

    def read_frame(self) -> Optional[Frame]:
        """Grab the next frame. Returns Frame or None if the stream ended/failed."""
        raise NotImplementedError

    def release(self) -> None:
        """Release stream resources."""
        raise NotImplementedError
