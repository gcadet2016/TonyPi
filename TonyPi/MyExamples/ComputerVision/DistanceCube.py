# DistanceCube.py
# Calculer la distance entre la caméra et un objet en utilisant la taille de l'objet dans l'image
# V 0.1
# Non testé

import cv2

# Charger la webcam
cap = cv2.VideoCapture(0)

# Paramètres de calibration (à ajuster en fonction de votre configuration)
KNOWN_WIDTH = 10.0  # Largeur réelle de l'objet en cm
FOCAL_LENGTH = 700  # Longueur focale de la caméra en pixels

def distance_to_camera(knownWidth, focalLength, perWidth):
    return (knownWidth * focalLength) / perWidth

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Détection de l'objet (par exemple, un rectangle)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        if cv2.contourArea(contour) > 1000:
            x, y, w, h = cv2.boundingRect(contour)
            distance = distance_to_camera(KNOWN_WIDTH, FOCAL_LENGTH, w)
            cv2.putText(frame, f"Distance: {distance:.2f} cm", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    cv2.imshow('Frame', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()