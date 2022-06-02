import random

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

def draw_scrolling_origin(image, origin, threshold):
    height, width, _ = image.shape
    top = int( (origin + threshold) * height )
    bottom = int( (origin - threshold) * height )
    start_top = (0, top)
    end_top = (width, top)
    start_bottom = (0, bottom)
    end_bottom = (width, bottom)
    color = (0,255,0)
    cv2.line(image, start_top, end_top, color, 2)
    cv2.line(image, start_bottom, end_bottom, color, 2)

def write_pose(image, pose, color=(0, 0, 255), thickness=1, margin=(5,10)):
    height, width, _ = image.shape
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(image, f'Pose: {pose}', (margin[0], height-margin[1]), font, 1, color, thickness=thickness)

def train_test_split(X, y, test_size=0.0, seed=None):
    # Seed
    random.seed(seed)
    # Bounds
    n_samples = X.shape[0]
    n_samples_train = int( (1.0 - test_size) * n_samples )
    # Separate datasets
    indices_train = random.sample(range(n_samples), n_samples_train)
    indices_test = [i for i in range(n_samples) if i not in indices_train]
    X_train = X[indices_train, :]
    X_test = X[indices_test, :]
    y_train = y[indices_train]
    y_test = y[indices_test]
    return X_train, X_test, y_train, y_test