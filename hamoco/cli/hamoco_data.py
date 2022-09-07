#!/usr/bin/env python

#TODO: Add a way to stop the recording (e.g. provide the max number of snapshots)

import os
import time
import argparse

import cv2
import mediapipe as mp
from hamoco import Hand, HandSnapshot
from hamoco.utils import draw_hand_landmarks, __window_name__

# Mediapipe shortcuts
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

def main():

    # All hand poses names
    hand_poses = []
    for pose in Hand.Pose:
        hand_poses.append(pose.name)
    hand_poses.remove('UNDEFINED')
    hand_poses_listed = ', '.join([f'"{pose}"' for pose in hand_poses])

    # Parser
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    description = f"""{parser.prog} activates the webcam and allows to record labeled hand poses
    in order to train a custom classification model for the main application.""".replace('\n',' ')
    parser.description = description
    parser.add_argument('pose',
                        type=str,
                        help=f'Hand pose to record (should be one of {hand_poses_listed})')
    parser.add_argument('path_to_data',
                        type=str,
                        help='Path to the directory that will store the recorded data')
    parser.add_argument('-R', '--reset',
                        action='store_true',
                        help='Remove any previously recorded data for the specified hand pose before recording')
    parser.add_argument('-d', '--delay',
                        type=float,
                        default=0.5,
                        help='Delay between consecutives snapshots')
    parser.add_argument('-S', '--stop_after',
                        type=int,
                        default=None,
                        help='Max. number of snapshots to stop the recording')
    parser.add_argument('-i', '--images',
                        action='store_true',
                        help='Path to the directory that will store the recorded data')
    parser.add_argument('-t', '--test',
                        action='store_true',
                        help='Do not save the data and only show real-time information about hand detection')
    args = parser.parse_args()
    # Custom variables linked to parser
    pose_name = args.pose
    path_to_data = args.path_to_data
    reset = args.reset
    delay_between_snapshots = args.delay
    stop_after = args.stop_after
    save_images = args.images
    record = not(args.test)

    # Track snapshots
    last_snapshot = time.time()
    snapshot_index = 0
    training_pose = Hand.Pose[pose_name]

    # Remove previously recorded files (both data files and images)
    files = os.listdir(path_to_data)
    files = [f for f in files if f.startswith('snapshot_') and pose_name in f]
    files.sort()
    if reset:
        for file in files:
                os.remove(os.path.join(path_to_data, file))
    # Find next snapshot index to append to previous files
    else:
        files = [f for f in files if f.endswith('.dat')]
        if len(files) > 0:
            snapshot_index = int(files[-1][9:13]) + 1

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
                print("Ignoring empty camera frame.")
                # If loading a video, use 'break' instead of 'continue'.
                continue

            # Hand detection results
            results = hands.process(image)
            hand_detected = bool(results.multi_hand_landmarks)
            if hand_detected:
                    # Draw the hand annotations on the image
                    draw_hand_landmarks(image, results.multi_hand_landmarks[0])

            # Snapshot every `delay_between_snapshot` seconds
            if time.time() - last_snapshot > delay_between_snapshots:

                if hand_detected:

                    # Get the landmarks
                    landmarks = results.multi_hand_landmarks[0].landmark

                    # Save the data (an optionally the corresponding image)
                    if record:
                        hand = Hand(pose=training_pose)
                        snapshot = HandSnapshot(hand=hand)
                        current_file = f'snapshot_{snapshot_index:04}_pose-{hand.pose.value}-{hand.pose.name}'
                        output_path = os.path.join(path_to_data, current_file)
                        snapshot.save_landmarks_vector(landmarks, path=output_path)
                        if save_images:
                            snapshot.save_processed_image(image, path=output_path)
                        
                        saved_at = time.strftime('%H:%M:%S')
                        print(f'# Saved snapshot #{snapshot_index} for pose "{pose_name}" ({saved_at})')
                        last_snapshot = time.time()
                        snapshot_index += 1

                    # Only basic information about the detection
                    else:
                        which_hand = results.multi_handedness[0].classification[0].label
                        confidence = int(100 * results.multi_handedness[0].classification[0].score)
                        print('Hand detected={} | Confidence={}%'.format(which_hand, confidence))

            # Display the image (stop if ESC key is pressed)
            cv2.imshow(__window_name__, image)
            if cv2.waitKey(5) & 0xFF == 27 or  snapshot_index >= stop_after:
                break

if __name__ == '__main__':
    main()