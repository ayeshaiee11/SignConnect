import cv2
import mediapipe as mp
import pickle
import numpy as np

# Ask user what they want to detect
print("Choose detection mode:")
print("1 - Alphabets")
print("2 - Numbers")
print("3 - Words")

mode = input("Enter choice: ")

# Load correct model
if mode == "1":
    model = pickle.load(open("model.pkl", "rb"))
    word_mode = False
    print("Alphabet detection started...")

elif mode == "2":
    model = pickle.load(open("nmodel.pkl", "rb"))
    word_mode = False
    print("Number detection started...")

elif mode == "3":
    model = pickle.load(open("wmodel.pkl", "rb"))
    word_mode = True
    print("Word detection started...")

else:
    print("Invalid choice")
    exit()

# Mediapipe setup
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

# ✅ FIXED: Use 2 hands for word mode, 1 for others
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2 if word_mode else 1,
    min_detection_confidence=0.7
)

cap = cv2.VideoCapture(0)

while True:

    ret, frame = cap.read()

    if not ret:
        break

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    if results.multi_hand_landmarks:

        # ✅ FIXED: Draw skeleton on EVERY detected hand
        for hand in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(
                frame,
                hand,
                mp_hands.HAND_CONNECTIONS
            )

        if word_mode:
            # ✅ FIXED: Collect landmarks from all hands & pad to 126
            all_landmarks = []

            for hand in results.multi_hand_landmarks:
                for lm in hand.landmark:
                    all_landmarks.extend([lm.x, lm.y, lm.z])

            # Pad to 126 if only one hand visible
            while len(all_landmarks) < 126:
                all_landmarks.append(0.0)

            prediction = model.predict([all_landmarks[:126]])[0]

        else:
            # Single hand mode (alphabets / numbers)
            landmarks = []
            for lm in results.multi_hand_landmarks[0].landmark:
                landmarks.extend([lm.x, lm.y, lm.z])

            prediction = model.predict([landmarks])[0]

        cv2.putText(frame,
                    f"Prediction: {prediction}",
                    (10, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    2)

    cv2.imshow("Sign Detection", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()