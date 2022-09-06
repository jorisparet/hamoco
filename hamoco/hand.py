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

    # Indices of palm landmarks in mediapipe hands
    palm_landmarks = [0, 5, 9, 13, 17]

    # Dimension: only look at X and Y for landmarks (discard Z)
    # If Z must be added at some point, changes will be minor
    dimension = 2

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

    def vectorize_landmarks(self, landmarks):
        landmarks_vector = numpy.zeros(self.dimension * len(landmarks))
        for lm_i, landmark in enumerate(landmarks):
            landmarks_vector[self.dimension*lm_i] = landmark.x
            landmarks_vector[self.dimension*lm_i+1] = landmark.y
        return landmarks_vector

    def feature_process_landmarks(self, landmarks_vector):
        processed_landmarks = landmarks_vector.copy()
        for axis in range(self.dimension):
            # Translate center of mass back to origin
            processed_landmarks[axis::self.dimension] -= processed_landmarks[axis::self.dimension].mean()
            # Make scale invariant
            processed_landmarks[axis::self.dimension] /= processed_landmarks[axis::self.dimension].std()
        return processed_landmarks.reshape(1,-1)

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
            path = 'hand_snapshot'
        cv2.imwrite(f'{path}.jpg', image)

    def save_landmarks_vector(self, landmarks, path=None):
        '''Save the landmarks vector to a text file.'''
        if path is None:
            path = 'defaut_name'
        raw_landmarks_vector = self.hand.vectorize_landmarks(landmarks)
        processed_landmarks_vector = self.hand.feature_process_landmarks(raw_landmarks_vector)
        with open(f'{path}.dat', 'w') as vec_file:
            vec_file.write(f'{self.hand.pose.value}\n')
            for pos in processed_landmarks_vector.flatten():
                vec_file.write(f'{pos:.6f} ')
            vec_file.write('\n')