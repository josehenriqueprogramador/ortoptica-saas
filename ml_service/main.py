from fastapi import FastAPI, UploadFile, File
import cv2
import mediapipe as mp
import numpy as np

app = FastAPI(
    title="Ortoptica IA Vision",
    description="Motor de processamento e tracking ocular de precisão clínica",
    version="2.0.0"
)

mp_face_mesh = mp.solutions.face_mesh

@app.get("/")
def health_check():
    return {"status": "online", "engine": "MediaPipe Iris Context", "version": "2.0.0"}

@app.post("/tracking/live")
async def tracking_live(file: UploadFile = File(...)):
    contents = await file.read()
    npimg = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

    if image is None:
        return {"face_detected": False, "error": "Incapaz de decodificar a imagem recebida."}

    # Ativando malha facial com refinamento para capturar os pontos exatos da ÍRIS
    with mp_face_mesh.FaceMesh(
        static_image_mode=True,
        max_num_faces=1,
        refine_landmarks=True
    ) as face_mesh:

        results = face_mesh.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

        if not results.multi_face_landmarks:
            return {"face_detected": False, "message": "Nenhuma face encontrada no enquadramento."}

        face_landmarks = results.multi_face_landmarks[0]

        # Mapeamento dos marcos anatômicos da Íris (Sub-pixel tracking)
        left_iris = face_landmarks.landmark[468]
        right_iris = face_landmarks.landmark[473]

        # Marcos de ancoragem dos cantos dos olhos (Estrutura óssea fixa)
        left_eye_corner = face_landmarks.landmark[33]
        right_eye_corner = face_landmarks.landmark[263]

        return {
            "face_detected": True,
            "clinical_data": {
                "left_eye_center": {"x": round(left_iris.x, 4), "y": round(left_iris.y, 4), "z": round(left_iris.z, 4)},
                "right_eye_center": {"x": round(right_iris.x, 4), "y": round(right_iris.y, 4), "z": round(right_iris.z, 4)},
                "anchor_points": {
                    "left_corner": {"x": round(left_eye_corner.x, 4), "y": round(left_eye_corner.y, 4)},
                    "right_corner": {"x": round(right_eye_corner.x, 4), "y": round(right_eye_corner.y, 4)}
                }
            },
            "system_status": "Tracking OK"
        }
