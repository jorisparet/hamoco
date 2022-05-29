import time
import enum

import numpy
import cv2

class Hand:

    @enum.unique
    class Pose(enum.IntEnum):
        UNDEFINED = -1
        OPEN = 0
        CLOSE = 1
        INDEX_UP = 2
        PINKY_UP = 3
        THUMB_SIDE = 4
        INDEX_MIDDLE_UP = 5

    def __init__(self, pose=None):
        if pose is None:
            self.pose = self.Pose.UNDEFINED
        else:
            if isinstance(pose, self.Pose):
                self.pose = pose
            if isinstance(pose, int):
                self.pose = self.Pose(pose)
            if isinstance(pose, str):
                self.pose = self.Pose[pose]   

    def process_landmarks(self, landmarks, keep_z=False):
        dim = 3 if keep_z else 2
        # Vectorize
        landmarks_vector = numpy.array([0.0 for i in range(dim * len(landmarks))])
        for lm_i, landmark in enumerate(landmarks):
            landmarks_vector[dim*lm_i] = landmark.x
            landmarks_vector[dim*lm_i+1] = landmark.y
            if keep_z:
                landmarks_vector[dim*lm_i+2] = landmark.z
        # Translate points back to origin based on the center of mass
        for axis in range(dim):
            landmarks_vector[axis::dim] -= landmarks_vector[axis::dim].mean()
        return landmarks_vector

class HandSnapshot:

    def __init__(self, hand=None):
        self.time = time.time()
        if hand is None:
            self.hand = Hand()
        else:
            self.hand = hand

    def save_processed_image(self, image, path=None):
        '''Save image with landmarks on them.'''
        if path is None:
            path = 'defaut_name'
        cv2.imwrite(f'{path}.jpg', image)

    def save_landmarks_vector(self, landmarks, path=None):
        '''Save the landmarks vector to a text file.'''
        if path is None:
            path = 'defaut_name'
        landmarks_vector = self.hand.process_landmarks(landmarks)
        with open(f'{path}.dat', 'w') as vec_file:
            vec_file.write(f'{self.hand.pose.value}\n')
            for pos in landmarks_vector:
                vec_file.write(f'{pos:.6f} ')