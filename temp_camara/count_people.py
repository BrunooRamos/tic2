import cv2
from ultralytics import YOLO

def count_people(frame, model):
    """
    Detects people in a video frame using the provided YOLO model.

    Args:
        frame: The image frame (numpy array) to process.
        model: The YOLO model instance for detection.

    Returns:
        tuple: (frame_procesado, personas_detectadas)
            - frame_procesado: The frame with bounding boxes and labels drawn.
            - personas_detectadas: The number of people detected in the frame.
    """
    results = model(frame, verbose=False)
    personas_detectadas = 0
    
    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = box.conf[0].item()
            cls = int(box.cls[0])

            if cls == 0: 
                personas_detectadas += 1
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"Person {conf:.2f}", (x1, y1 - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    return frame, personas_detectadas


def get_people_stream(model_path="yolov8n.pt"):
    """
    Generator that captures video from the default camera and counts people.

    Args:
        model_path (str): Path to the YOLO model weights file.

    Yields:
        int: The number of people detected in the current frame.
    """
    model = YOLO(model_path)
    cap = cv2.VideoCapture(0)
    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            frame_procesado, people_count = count_people(frame, model)
            cv2.imshow("YOLOv8 Person Detection", frame_procesado)
            yield people_count
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()