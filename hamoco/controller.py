#TODO: Add a config file that maps a hand pose to an event

import enum

import pyautogui
import numpy

from .hand import Hand
from .filter import OneEuroFilter

class HandyMouseController:

    min_detection_margin = 0.15
    max_detection_margin = 0.85

    @enum.unique
    class MouseState(enum.IntEnum):
        STANDARD = 0
        SCROLLING = 1
        DRAGGING = 2
        STILL = 4

    @enum.unique
    class Event(enum.IntEnum):
        MOVE = Hand.Pose.OPEN
        STOP = Hand.Pose.CLOSE
        LEFT_CLICK = Hand.Pose.INDEX_UP
        RIGHT_CLICK = Hand.Pose.PINKY_UP
        SCROLL = Hand.Pose.THUMB_SIDE
        LEFT_DOWN = Hand.Pose.INDEX_MIDDLE_UP

    def __init__(self, sensitivity=0.5, scrolling_threshold=0.1, scrolling_speed=1.0, min_cutoff_filter=0.1, beta_filter=0.0):
        self._set_sensitivity(sensitivity)
        self.scrolling_threshold = scrolling_threshold
        self.scrolling_speed = scrolling_speed
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
        return self._sensitivity

    @sensitivity.setter
    def sensitivity(self, value):
        self._set_sensitivity(value)
        
    def _set_sensitivity(self, value):
        self._sensitivity = value
        max_margin = HandyMouseController.max_detection_margin
        min_margin = HandyMouseController.min_detection_margin
        self._detection_margin = (max_margin - min_margin) * value + min_margin

    def palm_center(self, landmark_vector):
        self.frame += 1
        center = numpy.zeros(2)
        for axis in range(2):
            # Palm center
            center[axis] = landmark_vector[axis::2][Hand.palm_landmarks].mean()
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
        m = 1 / (1 - self._detection_margin)
        for i in range(2):
            trim_xy[i] = m * (xy[i] - self._detection_margin / 2)
            trim_xy[i] = min(max(0, trim_xy[i]), 1)
        self.origin = trim_xy * self.screen_resolution
        return trim_xy * self.screen_resolution

    def handle_pointer(self, hand_center, hand_pose):
        screen_xy = self.to_screen_coordinates(hand_center)
        if hand_pose == HandyMouseController.Event.MOVE or hand_pose == HandyMouseController.Event.LEFT_DOWN:
            delta = screen_xy - self.previous_position
            pyautogui.move(delta[0], delta[1], _pause=False)
        self.previous_position = screen_xy

    def accessible_area(self, image):
        xmin = int(self._detection_margin / 2 * image.shape[1])
        ymin = int(self._detection_margin / 2 * image.shape[0])
        xmax = image.shape[1] - xmin
        ymax = image.shape[0] - ymin
        return [xmin, ymin, xmax, ymax]

    def _on_pose_change(self, new_hand_pose):
        if self.current_mouse_state == HandyMouseController.MouseState.STANDARD:
            self._on_pose_change_standard(new_hand_pose)
        if self.current_mouse_state == HandyMouseController.MouseState.SCROLLING:
            self._on_pause_change_other(new_hand_pose, HandyMouseController.Event.SCROLL, HandyMouseController.MouseState.STANDARD)
        if self.current_mouse_state == HandyMouseController.MouseState.DRAGGING:
            self._on_pause_change_other(new_hand_pose, HandyMouseController.Event.LEFT_DOWN, HandyMouseController.MouseState.STANDARD)

    def _on_pose_change_standard(self, new_hand_pose):
        if new_hand_pose == self.Event.MOVE:
            pass
        elif new_hand_pose == Hand.Pose.CLOSE:
            pass
        elif new_hand_pose == self.Event.LEFT_CLICK:
            self.left_click()
        elif new_hand_pose == self.Event.RIGHT_CLICK:
            self.right_click()
        elif new_hand_pose == self.Event.LEFT_DOWN:
            self.enter_state(HandyMouseController.MouseState.DRAGGING)
        elif new_hand_pose == self.Event.SCROLL:
            self.enter_state(HandyMouseController.MouseState.SCROLLING)

    def _on_pause_change_other(self, new_hand_pose, reference_hand_pose, target_state):
        if new_hand_pose != reference_hand_pose:
            self.enter_state(target_state)

    def left_click(self):
        pyautogui.leftClick(_pause=False)

    def right_click(self):
        pyautogui.rightClick(_pause=False)

    def operate_mouse(self, hand, palm_center, confidence, min_confidence=0.5):

        # Mouse in STANDARD mode
        if self.current_mouse_state == HandyMouseController.MouseState.STANDARD:

            # Move the pointer or make it still
            if hand.pose == HandyMouseController.Event.MOVE or hand.pose == HandyMouseController.Event.STOP:
                self.handle_pointer(palm_center, hand.pose)
                self.previous_hand_pose = hand.pose

            # Hand pose changed: perform the appropriate action
            elif hand.pose != self.previous_hand_pose and confidence > min_confidence:
                self._on_pose_change(hand.pose)
                self.previous_hand_pose = hand.pose

        # Mouse in SCROLLING mode
        elif self.current_mouse_state == HandyMouseController.MouseState.SCROLLING:

            # Scroll up or down
            if hand.pose == HandyMouseController.Event.SCROLL:

                # Get the reference position (origin) when scrolling begins (first frame)
                if self.current_state_init == self.frame - 1:
                    self.scrolling_origin = palm_center[1]
                # Scroll up/down if above/below a certain distance threshold with
                #  respect to the scrolling origin point (next frames)
                else:
                    diff_to_origin_y = self.scrolling_origin - palm_center[1]
                    if abs(diff_to_origin_y) > self.scrolling_threshold:
                        pyautogui.scroll(int(numpy.sign(diff_to_origin_y) * self.scrolling_speed), _pause=False)

            # Hand pose changed: perform the appropriate action
            elif hand.pose != self.previous_hand_pose and confidence > min_confidence:
                self._on_pose_change(hand.pose)
                self.previous_hand_pose = hand.pose

        # Mouse in DRAGGING mode
        elif self.current_mouse_state == HandyMouseController.MouseState.DRAGGING:

            # Begin dragging
            if self.current_state_init == self.frame - 1:
                pyautogui.mouseDown(_pause=False)
            
            # Stop dragging if hand pose changed
            elif hand.pose != self.previous_hand_pose and confidence > min_confidence:
                pyautogui.mouseUp(_pause=False)
                self._on_pose_change(hand.pose)
                self.previous_hand_pose = hand.pose
            
            # Move the pointer like in standard mode with dragging enabled
            else:
                self.handle_pointer(palm_center, hand.pose)
                self.previous_hand_pose = hand.pose