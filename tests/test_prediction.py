#!/usr/bin/env python

import unittest
import os

import cv2
import mediapipe
from hamoco import Hand
from hamoco.models import __default_model__
import keras
import numpy

mp_hands = mediapipe.solutions.hands

class Test(unittest.TestCase):

    def setUp(self):
        # Load images
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        self.files = os.listdir(data_dir)
        self.files = [file for file in self.files if file.startswith('POSE_')]
        self.files.sort()
        self.images = []
        for file in self.files:
            image = cv2.imread(os.path.join(data_dir, file))
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image = cv2.flip(image, 1)
            self.images.append(image)
        # Load classification model
        self.model = keras.models.load_model(__default_model__)
            
    def test_hand_pose_prediction(self):
        poses = ['OPEN', 'CLOSE', 'INDEX_UP',
                 'PINKY_UP', 'INDEX_MIDDLE_UP', 'THUMB_SIDE']
        # Mediapipe hands
        with mp_hands.Hands(static_image_mode=True) as hands:

            # Evaluate each image
            n_images = len(self.images)
            for index, image in enumerate(self.images):

                # Expected pose
                expected_pose = Hand.Pose[poses[index]]

                # Process image
                results = hands.process(image)
                hand_detected = bool(results.multi_hand_landmarks)
                self.assertTrue(hand_detected)
                
                if hand_detected:

                    print(f'# TESTING FILE: {self.files[index]} ({index+1}/{n_images})')
                    detection_confidence = int(100 * results.multi_handedness[0].classification[0].score)
                    print(f'# ... MediaPipe detection confidence: {detection_confidence}%')
                    
                    # Get hand landmarks
                    hand = Hand()
                    landmarks = results.multi_hand_landmarks[0].landmark
                    raw_landmark_vector = hand.vectorize_landmarks(landmarks)
                    processed_landmark_vector = hand.feature_process_landmarks(raw_landmark_vector)
                    
                    # Predict hand pose
                    probabilities = self.model.predict(processed_landmark_vector).flatten()
                    prediction_confidence = int(100 * numpy.max(probabilities))
                    predicted_pose = Hand.Pose(numpy.argmax(probabilities))

                    # Test
                    print(f'# ... Prediction={predicted_pose.name} | Expected={expected_pose.name}')
                    print(f'# ... Prediction confidence: {prediction_confidence}%')
                    self.assertEqual(predicted_pose, expected_pose)
            
if __name__ == '__main':
    unittest.main()
