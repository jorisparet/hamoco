from .controller import HandyMouseController
from ..hand import Hand

import numpy
import pyautogui

class FrontMouseController(HandyMouseController):

    # Image flip
    flip = 1

    def __init__(self,
                 motion='relative',
                 sensitivity=0.5,
                 margin=0.25,
                 scrolling_threshold=0.1,
                 scrolling_speed=1.0,
                 min_cutoff_filter=0.1,
                 beta_filter=0.0):
        HandyMouseController.__init__(self,
                                      motion=motion,
                                      sensitivity=sensitivity,
                                      margin=margin, 
                                      scrolling_threshold=scrolling_threshold,
                                      scrolling_speed=scrolling_speed,
                                      min_cutoff_filter=min_cutoff_filter,
                                      beta_filter=beta_filter)
        
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

    def handle_pointer(self, tracking_point, hand_pose):
        screen_xy = self.to_screen_coordinates(tracking_point)
        if hand_pose == HandyMouseController.Event.MOVE or hand_pose == HandyMouseController.Event.LEFT_DOWN:
            if self.motion == 'relative':
                delta = (1 + self._sensitivity) * (screen_xy - self.previous_position)
                pyautogui.move(delta[0], delta[1], _pause=False)
            if self.motion == 'absolute':
                pyautogui.moveTo(screen_xy[0], screen_xy[1], _pause=False)
        self.previous_position = screen_xy

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