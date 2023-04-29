import enum

import pyautogui
import numpy

from ..hand import Hand
from ..utils import clamp
from ..filter import OneEuroFilter

class HandyMouseController:

    flip = None
    sensitivity_range = 1.5
    min_detection_margin = 0.15
    max_detection_margin = 0.8

    @enum.unique
    class MouseState(enum.IntEnum):
        STANDARD = 0
        SCROLLING = 1
        DRAGGING = 2

    @enum.unique
    class Event(enum.IntEnum):
        MOVE = Hand.Pose.OPEN
        STOP = Hand.Pose.CLOSE
        LEFT_CLICK = Hand.Pose.INDEX_UP
        RIGHT_CLICK = Hand.Pose.PINKY_UP
        SCROLL = Hand.Pose.THUMB_SIDE
        LEFT_DOWN = Hand.Pose.INDEX_MIDDLE_UP

    def __init__(self,
                 motion='relative',
                 sensitivity=0.5,
                 margin=0.25,
                 scrolling_threshold=0.1,
                 scrolling_speed=1.0,
                 min_cutoff_filter=0.1,
                 beta_filter=0.0):
        # Motion parameters
        self.motion = motion
        self.sensitivity = sensitivity
        self.margin = margin
        self.scrolling_threshold = scrolling_threshold
        self.scrolling_speed = scrolling_speed
        self.tracking_landmarks = None
        # Motion smoothing
        self.min_cutoff_filter = min_cutoff_filter
        self.beta_filter = beta_filter
        self.frame = 0
        self.filter = [OneEuroFilter(0, 0, min_cutoff=min_cutoff_filter, beta=beta_filter) for filter in range(2)]
        # Mouse state and screen
        self.previous_hand_pose = Hand.Pose.UNDEFINED
        self.current_mouse_state = self.MouseState.STANDARD
        self.current_state_init = 0
        self.previous_position = numpy.zeros(2)
        self.scrolling_origin = 0
        self.screen_resolution = numpy.array(pyautogui.size())

    @property
    def sensitivity(self):
        # Visible sensitivity is between 0 and 1
        range_ = HandyMouseController.sensitivity_range
        return (self._sensitivity + range_ / 2) / range_

    @sensitivity.setter
    def sensitivity(self, value):
        # Internal sensitivity is between -range/2 and +range/2
        value = clamp(value, 0, 1)
        range_ = HandyMouseController.sensitivity_range
        self._sensitivity = range_ * value - (range_ / 2)

    @property
    def margin(self):
        # Visible margin is between 0 and 1
        max_margin = HandyMouseController.max_detection_margin
        min_margin = HandyMouseController.min_detection_margin
        return (self._margin - min_margin) / (max_margin - min_margin)

    @margin.setter
    def margin(self, value):
        # Internal margin is between min_margin and max_margin
        value = clamp(value, 0, 1)
        max_margin = HandyMouseController.max_detection_margin
        min_margin = HandyMouseController.min_detection_margin
        self._margin = (max_margin - min_margin) * value + min_margin    

    def palm_center(self, landmark_vector):
        self.frame += 1
        center = numpy.zeros(2)
        for axis in range(2):
            # Palm center
            center[axis] = landmark_vector[axis::2][self.tracking_landmarks].mean()
            # Smoothing
            center[axis] = self.filter[axis](self.frame, center[axis])
        return center

    def enter_state(self, state):
        self.current_mouse_state = state
        self.current_state_init = self.frame

    @property
    def pointer_position(self):
        return pyautogui.position()

    def to_screen_coordinates(self, xy):
        trim_xy = numpy.empty_like(xy)
        m = 1 / (1 - self._margin)
        for i in range(2):
            trim_xy[i] = m * (xy[i] - self._margin / 2)
            trim_xy[i] = min(max(0, trim_xy[i]), 1)
        self.origin = trim_xy * self.screen_resolution
        return trim_xy * self.screen_resolution

    def accessible_area(self, image):
        xmin = int(self._margin / 2 * image.shape[1])
        ymin = int(self._margin / 2 * image.shape[0])
        xmax = image.shape[1] - xmin
        ymax = image.shape[0] - ymin
        return [xmin, ymin, xmax, ymax]

    def left_click(self):
        pyautogui.leftClick(_pause=False)

    def right_click(self):
        pyautogui.rightClick(_pause=False)