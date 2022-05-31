import numpy

import cv2
import mediapipe as mp

# Mediapipe shortcuts
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

def draw_hand_landmarks(image, hand_landmark):
    mp_drawing.draw_landmarks(image, 
        hand_landmark,
        mp_hands.HAND_CONNECTIONS,
        mp_drawing_styles.get_default_hand_landmarks_style(),
        mp_drawing_styles.get_default_hand_connections_style())

def draw_palm_center(image, palm_center, size=20):
    height, width, _ = image.shape
    size = size // 2
    cursor_xy = (palm_center * numpy.array([width, height])).astype(int)
    cv2.rectangle(image, tuple(cursor_xy - size), 
                        tuple(cursor_xy + size),
                        (255,255,255), 3)

def draw_control_bounds(image, bounds):
    # Bounds
    height, width, _ = image.shape
    xmin, ymin, xmax, ymax = bounds

    # Draw the accessible area
    hidden = numpy.zeros_like(image, numpy.uint8)
    alpha = 0.25
    color = (1,1,1)
    cv2.rectangle(hidden, (0, 0), (xmin, height), color, -1)
    cv2.rectangle(hidden, (xmin, 0), (xmax, ymin), color, -1)
    cv2.rectangle(hidden, (xmax, 0), (width, height), color, -1)
    cv2.rectangle(hidden, (xmin, ymax), (xmax, height), color, -1)
    mask = hidden.astype(bool)
    image[mask] = cv2.addWeighted(image, alpha, hidden, 1-alpha, 0)[mask]

def write_pose(image, pose, color=(0, 0, 255), thickness=1, margin=(5,10)):
    height, width, _ = image.shape
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(image, f'Pose: {pose}', (margin[0], height-margin[1]), font, 1, color, thickness=thickness)