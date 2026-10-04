"""Orchestrates the end-to-end pipeline."""
from data_ingestion import DataIngestion
from image_preprocessor import ImagePreprocessor
from model_inference_engine import ModelInferenceEngine
from alert_logger import AlertLogger


def run(source: str, model_path: str, labels: list) -> None:
    ingest = DataIngestion(source)
    pre = ImagePreprocessor()
    engine = ModelInferenceEngine(model_path, labels)
    logger = AlertLogger()

    engine.load_model()
    engine.warmup()
    if not ingest.connect():
        raise RuntimeError("Cannot open video source")

    try:
        while (frame := ingest.read_frame()) is not None:
            tensor = pre.process(frame)
            detections = pre.scale_boxes_back(engine.infer(tensor), frame)
            logger.log(detections, frame)
            if logger.should_alert(detections):
                logger.send_alert(detections, frame)
    finally:
        ingest.release()


if __name__ == "__main__":
    run("rtsp://camera/stream", "model.onnx", ["person", "car"])
