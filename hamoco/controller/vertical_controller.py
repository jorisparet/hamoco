from .controller import HandyMouseController

import pyautogui

class VerticalMouseController(HandyMouseController):

    name = 'vertical'
    # Image flip
    flip = -1

    def __init__(self,
                 motion='absolute',
                 tracking_landmarks=[1,5],
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
        self.tracking_landmarks = tracking_landmarks

    def operate_mouse(self, hand, palm_center, confidence, min_confidence=0.5):
        # TODO: remove prediction confidence for this controller
        self.handle_pointer(palm_center)
        self.previous_hand_pose = hand.pose

    def handle_pointer(self, hand_center):
        screen_xy = self.to_screen_coordinates(hand_center)
        if self.motion == 'relative':
            delta = (1 + self._sensitivity) * (screen_xy - self.previous_position)
            pyautogui.move(delta[0], delta[1], _pause=False)
            self.previous_position = screen_xy
        if self.motion == 'absolute':
            pyautogui.moveTo(screen_xy[0], screen_xy[1], _pause=False)