# System Design Specification: AI Smart Surveillance & Attendance System

**Course:** AI Project Design and Development (AI-316)
**Lab:** 02 – System Requirements & Software Architecture for AI Projects
**University:** Air University Islamabad, Department of Creative Technologies
**Student:** _<Name / Reg. No.>_

---

## Table of Contents
1. [Functional & Non-Functional Requirements (Task 1)](#1-requirements)
2. [System Boundary, Actors & I/O Mapping (Task 2)](#2-system-boundary-actors--inputoutput-mapping)
3. [Data-Flow Diagrams (Task 3)](#3-data-flow-diagrams)
4. [Modular Software Architecture (Task 4)](#4-modular-software-architecture)
5. [Repository Structure](#5-repository-structure)

---

## 1. Requirements

**Case study:** Smart Automated Attendance System (face detection + recognition on classroom cameras).

### 1.1 Functional Requirements

| ID | Requirement | Description | Acceptance Criterion |
|----|-------------|-------------|----------------------|
| FR-01 | Face Detection | The system shall detect all faces in each processed frame. | Detection latency ≤ 50 ms per frame on the edge device |
| FR-02 | Face Recognition | The system shall match each detected face against enrolled student embeddings. | Top-1 match with cosine similarity ≥ 0.60 |
| FR-03 | Attendance Logging | The system shall record student ID, timestamp, camera ID and confidence for each recognized student, once per class session. | No duplicate entries per student per session |
| FR-04 | Database Synchronization | The system shall sync local attendance records to the central database. | Sync within 30 s of connectivity; offline queue retained |
| FR-05 | Reporting & Manual Override | The system shall let an Admin/Instructor view reports and correct attendance manually. | Export to CSV/PDF; all edits audit-logged |

### 1.2 Non-Functional Requirements

| ID | Category | Requirement | Measurable Target |
|----|----------|-------------|-------------------|
| NFR-01 | Performance | Minimum processing frame rate | ≥ 15 FPS end-to-end |
| NFR-02 | Accuracy | Model accuracy thresholds | Face detection mAP@0.5 ≥ 0.90; recognition accuracy ≥ 95%; false accept rate ≤ 1% |
| NFR-03 | Power / Resources | Edge device power usage | ≤ 15 W average (e.g., Jetson Nano class); RAM ≤ 4 GB |
| NFR-04 | Security & Privacy | Data privacy | Embeddings encrypted at rest (AES-256), TLS 1.2+ in transit, no raw video stored beyond 24 h, consent-based enrollment |
| NFR-05 | Reliability & Scalability | Availability and scale | 99% uptime during class hours; supports ≥ 4 concurrent camera streams; auto-recovery from stream drop within 10 s |

---

## 2. System Boundary, Actors & Input/Output Mapping

**Case study:** AI-powered surveillance application (people/object detection with alerts).

### 2.1 System Actors

| Actor | Type | Role | Interaction |
|-------|------|------|-------------|
| Security Operator | Human (primary) | Monitors live feeds, acknowledges alerts | Dashboard, alert console |
| System Administrator | Human (primary) | Configures cameras, models, thresholds, users | Admin panel, config files |
| Automated Trigger System | External system | Sends events (door sensor, motion sensor) to start/prioritize analysis | MQTT / REST |
| IP Camera | Hardware | Supplies video stream | RTSP |
| Notification Service | External system | Delivers SMS/email/push alerts | HTTPS API |

### 2.2 System Inputs

| Input | Source | Format / Parameters |
|-------|--------|---------------------|
| Video stream | IP camera | RTSP, H.264/H.265, 1920×1080 @ 25–30 FPS (downscaled to 640×640 for inference) |
| Sensor parameters | Motion/door sensors | JSON: `{sensor_id, event, timestamp}` |
| Configuration | Administrator | YAML: confidence threshold (default 0.5), NMS IoU (0.45), ROI polygons, alert rules |
| Model weights | Admin / model registry | ONNX / TensorRT (`.onnx`, `.engine`) |
| Operator feedback | Security Operator | Alert acknowledge / false-positive flag |

### 2.3 System Outputs

| Output | Destination | Format |
|--------|-------------|--------|
| Bounding boxes | Overlay on dashboard, database | `[x1, y1, x2, y2, class, confidence]` (pixels) |
| Alert notifications | Operator, Notification Service | JSON + snapshot JPEG; channels: push/SMS/email |
| Log entries | Log store / DB | `timestamp, camera_id, class, conf, bbox, alert_level` |
| Analytics reports | Admin | Counts per class/hour, heatmaps (CSV/PDF) |
| Annotated clips | Storage | MP4, 10 s pre/post event |

### 2.4 Operational Constraints

| Constraint | Limit |
|------------|-------|
| Maximum memory footprint | ≤ 4 GB RAM, ≤ 2 GB GPU memory (model + buffers) |
| Bandwidth | ≤ 4 Mbps per camera stream; ≤ 1 Mbps upstream for alerts/metadata (only snapshots uploaded, not full video) |
| Inference latency | ≤ 100 ms per frame end-to-end |
| Storage | Rolling 7-day video buffer; 90-day metadata retention |
| Hardware | Edge device with GPU/NPU; no cloud dependency for inference |
| Compliance | Camera zones signposted; access restricted by role (RBAC) |

---

## 3. Data-Flow Diagrams

### 3.1 Level 0 – Context Diagram

```mermaid
flowchart LR
    CAM[/"Entity: IP Camera"/]
    OP[/"Entity: Security Operator"/]
    ADM[/"Entity: Administrator"/]
    TRG[/"Entity: Automated Trigger System"/]
    NOTIF[/"Entity: Notification Service"/]

    SYS(("0.0<br/>AI Object Detection<br/>& Analytics System"))

    CAM -- "RTSP video stream" --> SYS
    TRG -- "Sensor events" --> SYS
    ADM -- "Config, thresholds, model weights" --> SYS
    OP -- "Alert acknowledgement / feedback" --> SYS
    SYS -- "Live annotated feed, alerts" --> OP
    SYS -- "Reports, system health" --> ADM
    SYS -- "Alert payload + snapshot" --> NOTIF
```

### 3.2 Level 1 DFD

```mermaid
flowchart TD
    CAM[/"E1: IP Camera"/]
    TRG[/"E2: Trigger System"/]
    ADM[/"E3: Administrator"/]
    OP[/"E4: Security Operator"/]
    NOTIF[/"E5: Notification Service"/]

    P1(("1.0<br/>Data Ingestion"))
    P2(("2.0<br/>Image Preprocessing"))
    P3(("3.0<br/>Model Inference"))
    P4(("4.0<br/>Post-processing<br/>(NMS, tracking, rules)"))
    P5(("5.0<br/>Alert & Logging"))
    P6(("6.0<br/>Analytics & Reporting"))

    D1[("D1: Config Store")]
    D2[("D2: Model Registry")]
    D3[("D3: Detection Log DB")]
    D4[("D4: Snapshot/Clip Storage")]

    CAM -- "RTSP stream" --> P1
    TRG -- "sensor event" --> P1
    ADM -- "settings" --> D1
    ADM -- "model weights" --> D2
    D1 -- "stream URLs, thresholds" --> P1
    D1 -- "resize / normalization params" --> P2
    D1 -- "alert rules" --> P4

    P1 -- "raw frames + timestamp" --> P2
    P2 -- "normalized tensor (1x3x640x640)" --> P3
    D2 -- "loaded model" --> P3
    P3 -- "raw predictions" --> P4
    P4 -- "filtered detections (bbox, class, conf)" --> P5
    P4 -- "annotated frame" --> OP
    P5 -- "detection records" --> D3
    P5 -- "snapshot / clip" --> D4
    P5 -- "alert payload" --> NOTIF
    P5 -- "alerts" --> OP
    OP -- "acknowledge / false-positive" --> P5
    D3 -- "historical records" --> P6
    P6 -- "reports, statistics" --> ADM
```

**Legend:** parallelogram = external entity, circle = process, cylinder = data store, arrow = data flow.

---

## 4. Modular Software Architecture

### 4.1 Module Responsibilities

| Module | Responsibility | Input | Output |
|--------|----------------|-------|--------|
| `DataIngestion` | Connect to RTSP/video source, grab frames, reconnect on failure | Source URI | `Frame` objects |
| `ImagePreprocessor` | Resize (letterbox), color convert, normalize, batch | `Frame` | `np.ndarray` tensor (1,3,H,W) |
| `ModelInferenceEngine` | Load model, run inference, decode + NMS | Tensor | `list[Detection]` |
| `AlertLogger` | Evaluate rules, log detections, dispatch alerts | `list[Detection]` | `bool` / log record IDs |

### 4.2 Class Specifications

| Class | Method | Parameters | Returns |
|-------|--------|-----------|---------|
| `DataIngestion` | `connect()` | – | `bool` |
| | `read_frame()` | – | `Optional[Frame]` |
| | `release()` | – | `None` |
| `ImagePreprocessor` | `process(frame)` | `Frame` | `np.ndarray` |
| | `scale_boxes_back(boxes, frame)` | `list[Detection]`, `Frame` | `list[Detection]` |
| `ModelInferenceEngine` | `load_model()` | – | `None` |
| | `infer(tensor)` | `np.ndarray` | `list[Detection]` |
| | `warmup()` | – | `None` |
| `AlertLogger` | `log(detections, frame)` | `list[Detection]`, `Frame` | `int` (records written) |
| | `should_alert(detections)` | `list[Detection]` | `bool` |
| | `send_alert(detections, frame)` | `list[Detection]`, `Frame` | `bool` |

Skeleton code is in [`src/`](src/) (`interfaces.py`, `data_ingestion.py`, `image_preprocessor.py`, `model_inference_engine.py`, `alert_logger.py`, `pipeline.py`).

### 4.3 Class Diagram

```mermaid
classDiagram
    class Frame {
        +ndarray image
        +float timestamp
        +str camera_id
    }
    class Detection {
        +tuple bbox
        +str label
        +float confidence
    }
    class DataIngestion {
        +connect() bool
        +read_frame() Frame
        +release() None
    }
    class ImagePreprocessor {
        +process(frame) ndarray
        +scale_boxes_back(dets, frame) list
    }
    class ModelInferenceEngine {
        +load_model() None
        +warmup() None
        +infer(tensor) list
    }
    class AlertLogger {
        +log(dets, frame) int
        +should_alert(dets) bool
        +send_alert(dets, frame) bool
    }
    DataIngestion --> Frame
    ImagePreprocessor --> Frame
    ModelInferenceEngine --> Detection
    AlertLogger --> Detection
```

---

## 5. Repository Structure

```
project/
├── ARCHITECTURE.md
├── requirements.txt
└── src/
    ├── interfaces.py
    ├── data_ingestion.py
    ├── image_preprocessor.py
    ├── model_inference_engine.py
    ├── alert_logger.py
    └── pipeline.py
```

### Requirement Traceability

| Requirement | Satisfied By |
|-------------|--------------|
| FR-01, NFR-01, NFR-02 | `ImagePreprocessor` + `ModelInferenceEngine` |
| FR-03, FR-04 | `AlertLogger` |
| Stream resilience (NFR-05) | `DataIngestion.connect()` retry logic |
| Privacy (NFR-04) | `AlertLogger` (encrypted storage, retention policy) |
