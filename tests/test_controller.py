#!/usr/bin/env python

import unittest
import os

from hamoco import Hand, HandyMouseController, ClassificationModel
from hamoco.utils import draw_palm_center, draw_control_bounds, write_pose
import numpy
import cv2

class Test(unittest.TestCase):

    def setUp(self):
        self.data_dir = os.path.join(os.path.dirname(__file__), 'data')
        self.vectors = os.listdir(self.data_dir)
        self.vectors = [file for file in self.vectors if file.startswith('snapshot_')]
        self.vectors.sort()
        
    def test_controller(self):

        # Controller
        controller = HandyMouseController(sensitivity=0.15)
        controller.sensitivity = 0.25
        self.assertEqual(controller.sensitivity, 0.25)

        model = ClassificationModel()
        event_sequence = ['OPEN',
                          'CLOSE',
                          'THUMB_SIDE',
                          'THUMB_SIDE',
                          'CLOSE',
                          'OPEN',
                          'PINKY_UP',
                          'CLOSE',
                          'INDEX_MIDDLE_UP',
                          'INDEX_MIDDLE_UP',
                          'CLOSE']

        phony_image = cv2.imread(os.path.join(self.data_dir, 'POSE_1_OPEN.jpg'))
        for event in event_sequence:

            # Pose name from event
            pose = Hand.Pose[event]
            vector_file = self.vectors[pose.value]
            
            # Get hand pose and palm center
            vector, _ = model.read_sample(os.path.join(self.data_dir, vector_file))
            vector = numpy.array(vector)
            palm_center = controller.palm_center(vector)
            confidence = 0.99
            
            # Operate mouse
            hand = Hand(pose=pose)
            controller.operate_mouse(hand, palm_center, confidence)

            # Drawing functions
            bounds = controller.accessible_area(phony_image)
            draw_control_bounds(phony_image, bounds)
            draw_palm_center(phony_image, palm_center, size=20)
            write_pose(phony_image, hand.pose.name)
            
if __name__ == '__main':
    unittest.main()
