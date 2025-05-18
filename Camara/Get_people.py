from ultralytics import YOLO
import cv2
from Camara.Count_people import count_people

def get_people_data():
    model = YOLO("yolov8n.pt")
    cap = cv2.VideoCapture(0,cv2.CAP_V4L2)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_procesado, results = count_people(frame, model)
        cv2.imshow("YOLOv8 Person Detection", frame_procesado)

        # Sale si se presiona 'q'
        if cv2.waitKey(1) & 0xFF == ord("q"):
            cap.release()
            cv2.destroyAllWindows()
            return results
        
        print(results)

        # Devuelve los resultados en cada frame (puedes ajustar esto según tu lógica)
        return results

    cap.release()
    cv2.destroyAllWindows()
    return None
