#!/usr/bin/env python

# TODO: add an optional overlay frame with PyQt that shows the edges in real time
# TODO: add more complex actions (e.g. copy, cut, paste) with the second hand

import argparse
import json
from collections import deque

import cv2
import mediapipe as mp
import pyautogui
import keras
import numpy

from hamoco import Hand, HandyMouseController
from hamoco.models import __default_model__
from hamoco.utils import draw_hand_landmarks, draw_palm_center, draw_control_bounds, draw_scrolling_origin
from hamoco.utils import write_pose, __window_name__
from hamoco.config import __default_config__

# Mediapipe shortcuts
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

# Allow mouse to go on the border of the screen
pyautogui.FAILSAFE = False

def main():

    # Load default settings
    with open(__default_config__) as cfg:
        default_config = json.load(cfg)

    # Parser
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    description = f"""{parser.prog} activates the webcam and allows to use hand
    gestures to take control of the mouse pointer. Several basic actions can then
    be performed, such as left click, right click, drag and drop and scrolling.""".replace('\n',' ')
    parser.description = description
    parser.add_argument('-S', '--sensitivity', 
                        default=default_config['sensitivity'], 
                        type=float, 
                        help='Mouse sensitivity (between 0 and 1)')
    parser.add_argument('-M', '--margin', 
                        default=default_config['margin'], 
                        type=float, 
                        help='Detection margin at the edges of the frame (between 0 and 1)')
    parser.add_argument('--scrolling_threshold', 
                        default=default_config['scrolling_threshold'], 
                        type=float, 
                        help='Amount of change from the origin scrolling position to start scrolling (between 0 and 1)')
    parser.add_argument('--scrolling_speed', 
                        default=default_config['scrolling_speed'],
                        type=float, 
                        help='Scrolling speed')
    parser.add_argument('--min_cutoff_filter', 
                        default=default_config['min_cutoff_filter'],
                        type=float, 
                        help='Minimum cutoff frequency for motion smoothing (low values decrease jitter but increase speed lag)')
    parser.add_argument('--beta_filter', 
                        default=default_config['beta_filter'], 
                        type=float, 
                        help='Speed coefficient for motion smoothing (large values decrease speed lag but increase jitter)')
    parser.add_argument('--minimum_prediction_confidence',
                        default=default_config['minimum_prediction_confidence'], 
                        type=float, 
                        help='Minimum prediction confidence for predicting hand poses')
    parser.add_argument('-m', '--model', 
                        default=default_config['model'],
                        type=str,
                        help='Path to the Keras model to use for hand pose prediction')
    parser.add_argument('--show',
                        action='store_'+str(not default_config['show']).lower(),
                        help='Real-time display of the processed camera feed')
    parser.add_argument('--stop_sequence',
                        nargs='+',
                        type=str,
                        default=default_config['stop_sequence'],
                        help='Sequence of consecutive poses to stop the application')
    args = parser.parse_args()
    # Custom variables linked to parser
    sensitivity = args.sensitivity
    margin = args.margin
    scrolling_threshold = args.scrolling_threshold
    scrolling_speed = args.scrolling_speed
    min_cutoff_filter = args.min_cutoff_filter
    beta_filter = args.beta_filter
    minimum_prediction_confidence = args.minimum_prediction_confidence
    model = args.model
    show_feed = args.show
    stop_sequence_litteral = args.stop_sequence

    # Prepare stop sequence
    stop_sequence = []
    for pose in stop_sequence_litteral:
        stop_sequence.append(Hand.Pose[pose])
    stop_sequence = deque(stop_sequence, maxlen=len(stop_sequence))
    consecutive_poses = deque(maxlen=stop_sequence.maxlen)
    previous_pose = Hand.Pose.UNDEFINED

    # Load classification model
    path_to_model = __default_model__ if model is None else model
    trained_model = keras.models.load_model(path_to_model)

    # Hand controller
    hand_controller = HandyMouseController(sensitivity=sensitivity,
                                        margin=margin,
                                        scrolling_threshold=scrolling_threshold,
                                        scrolling_speed=scrolling_speed,
                                        min_cutoff_filter=min_cutoff_filter,
                                        beta_filter=beta_filter)

    # Webcam input
    capture = cv2.VideoCapture(0)
    with mp_hands.Hands(static_image_mode=False,
                        model_complexity=1,
                        max_num_hands=1,
                        min_detection_confidence=0.5,
                        min_tracking_confidence=0.5) as hands:

        # Detect hand movement while the video capture is on
        while capture.isOpened():
            success, image = capture.read()
            image = cv2.flip(image, 1)

            if not success:
                print('Ignoring empty camera frame.')
                # If loading a video, use 'break' instead of 'continue'.
                continue

            # A hand is detected
            results = hands.process(image)
            hand_detected = bool(results.multi_hand_landmarks)
            if hand_detected:

                # Draw the hand annotations on the image
                draw_hand_landmarks(image, results.multi_hand_landmarks[0])

                # Landmark coordinates of the detected hand
                landmarks = results.multi_hand_landmarks[0].landmark
                hand = Hand()
                raw_landmark_vector = hand.vectorize_landmarks(landmarks)
                palm_center = hand_controller.palm_center(raw_landmark_vector)

                # Predict hand pose
                processed_landmark_vector = hand.feature_process_landmarks(raw_landmark_vector)
                probabilities = trained_model.predict(processed_landmark_vector).flatten()
                prediction_confidence = numpy.max(probabilities)
                predicted_pose = numpy.argmax(probabilities)
                hand.pose = Hand.Pose(predicted_pose)

                # Update consecutive poses queue for stop sequence
                if hand.pose != previous_pose:
                    consecutive_poses.append(hand.pose)
                    previous_pose = hand.pose

                # Perform the appropriate mouse action
                hand_controller.operate_mouse(hand, 
                                            palm_center,
                                            prediction_confidence,
                                            min_confidence=minimum_prediction_confidence)

            # Stop sequence
            if consecutive_poses == stop_sequence:
                print('# hamoco: stop sequence detected. Exiting the application...')
                break

            # Show the camera feed
            if show_feed:

                # Accessible area        
                bounds = hand_controller.accessible_area(image)
                draw_control_bounds(image, bounds)

                # Show palm center
                if hand_detected:
                    draw_palm_center(image, palm_center, size=0.03)
                    write_pose(image, hand.pose.name)

                # Draw scrolling origin
                if hand_controller.current_mouse_state == HandyMouseController.MouseState.SCROLLING:
                    draw_scrolling_origin(image, hand_controller.scrolling_origin, hand_controller.scrolling_threshold)

                # Show
                cv2.imshow(__window_name__, image)
                if cv2.waitKey(5) & 0xFF == 27:
                    break
                        
    capture.release()

if __name__ == '__main__':
    main()