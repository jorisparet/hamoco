#!/usr/bin/env python

import unittest
import os

import cv2
import mediapipe
from hamoco import Hand, HandSnapshot
from hamoco.utils import draw_hand_landmarks

mp_hands = mediapipe.solutions.hands

class Test(unittest.TestCase):

    def setUp(self):
        self.data_dir = os.path.join(os.path.dirname(__file__), 'data')
        # Images
        self.images = os.listdir(self.data_dir)
        self.images = [file for file in self.images if file.startswith('POSE_')]
        self.images.sort()
        
    def test_hand_instantiation(self):
        hand_0 = Hand(pose=Hand.Pose.OPEN)
        hand_1 = Hand(pose=0)
        hand_2 = Hand(pose='OPEN')
        self.assertEqual(hand_0.pose, hand_1.pose)
        self.assertEqual(hand_1.pose, hand_2.pose)

    def test_snapshot(self):

        hands = mp_hands.Hands(static_image_mode=True)
        for index, image_file in enumerate(self.images):

            # Snapshot
            phony_hand = Hand(Hand.Pose(index))
            snapshot = HandSnapshot(hand=phony_hand)
            
            # Process with MediaPipe first to get raw landmarks
            image = cv2.imread(os.path.join(self.data_dir, image_file))
            image = cv2.flip(image, 1)
            mediapipe_results = hands.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            draw_hand_landmarks(image, mediapipe_results.multi_hand_landmarks[0])
            landmarks = mediapipe_results.multi_hand_landmarks[0].landmark
            
            # Image
            image_path = os.path.join(self.data_dir, f'test-snapshot_{phony_hand.pose.name}')
            snapshot.save_processed_image(image, path=image_path)

            # Vector
            vector_path = os.path.join(self.data_dir, f'test-vector_{phony_hand.pose.name}')
            snapshot.save_landmarks_vector(landmarks, path=vector_path)
            
if __name__ == '__main':
    unittest.main()
