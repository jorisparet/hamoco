[![license](https://img.shields.io/pypi/l/partycls.svg)](https://en.wikipedia.org/wiki/GNU_General_Public_License)

# Hamoco

**hamoco** (*handy mouse controller*) is a python application that allows you to control your mouse from your webcam using various hand gestures. The classification of the various hand poses relies on the use of a small neural network.

Installation
------------

From the [code repository](https://github.com/jorisparet/hamoco):

```
git clone https://github.com/jorisparet/hamoco
cd hamoco
pip install .
```

*The package will be published on [PyPI](https://pypi.org/) at a later stage of development.*

Requirements
------------

* [PyAutoGUI](https://pypi.org/project/PyAutoGUI/)
* [numpy](https://pypi.org/project/numpy/)
* [openCV](https://pypi.org/project/opencv-python/)
* [MediaPipe](https://google.github.io/mediapipe/)
* [Keras](https://keras.io/)

Quick start
-----------

After the installation, the package should have copied three binaries in the `.local/bin/` folder of the home directory:
1. `hamoco-run`
2. `hamoco-data`
3. `hamoco-train`

(*Make sure this location is included in your `$PATH` environment variable*)

Run these applications directly in the terminal, *e.g.* `hamoco-run --sensitivity 0.5 --show`.

Access the help with the `-h` or `--help` flags to display the available options, *e.g.* `hamoco-run --help`.

### hamoco-run

*hamoco-run* is the **main application**. It activates the webcam and allows to use hand gestures to take control of the mouse pointer. Several basic actions can then be performed, such as *left click*, *right click*, *drag and drop* and *scrolling*.

Various settings can be adjusted to customize the hand controller to your liking, such as the global sensivitity and parameters for motion smoothing. Type `--help` for more information on the available options.

Examples:

- `hamoco-run --sensitivity 0.4 --scrolling_threshold 0.2` : adapts the sensitivity and set a custom threshold value to trigger scrolling motions.
- `hamoco-run --min_cutoff_filter 0.05 --show` : sets a custom value for the cutoff frequency used for motion smoothing and opens a window that shows the processed video feed in real-time.

### hamoco-data

*hamoco-data* activates the webcam and allows to record your own labeled data for hand poses in order to train a custom NN-based classification model for the main application. This model can then be used in place of the one provided by default and will be more performant, as it will be trained on your personal and natural hand poses (see *hamoco-train*). Type `--help` for more information on the available options.

The application requires two arguments:
- `pose`: a string that indicates the type of hand pose you intend to record. It should be one of {*OPEN, CLOSE, INDEX_UP, PINKY_UP, THUMB_SIDE, INDEX_MIDDLE_UP*}.
- `path_to_data`: path to the folder inside of which you want the recorded data to be saved.

Examples:
- `hamoco-data OPEN data/ --delay 1.0` : starts the recording for the *OPEN* hand pose, stores the resulting data in the `data` folder (provided it exists!), and takes a new snapshot every second.
- `hamoco-data INDEX_UP data/ --delay 0.25 --images` : starts the recording for the *INDEX_UP* hand pose, stores the resulting data in the `data` folder, takes a new snapshot every 0.25s, and saves the images in addition to the numeric data. This can be useful if you want to manually check if your hand was in a correct position when it was captured, and hence keep or remove the data accordingly.

### hamoco-train

Provided a path to a directory with relevant data, *hamoco-train* trains a customizable NN-based classification model to predict a hand pose. This classification model can then be used in the main application in place of the one provided by default. Type `--help` for more information on the available options.

The application requires two arguments:
- `path_to_model` : path to save the newly trained model.
- `path_to_data` : path to the data folder to use to train the model (see *hamoco-data*).

Examples:
- `hamoco-train my_custom_model.h5 data/ --hiden_layers 50 25 --epochs 20` : trains and save a model named `my_custom_model.h5` that contains two hidden layers (with dimensions 50 and 25 respectively) over 20 epochs, by using the formatted data in the `data` folder.
- `hamoco-train my_custom_model.h5 data/ --epochs 10 --learning_rate 0.1` : trains and save a model named `my_custom_model.h5` with default dimensions over 20 epochs and a learning rate of 0.1, by using the formatted data in the `data` folder.

Your model can then be used in the main application with the `--model` flag of *hamoco-run*, *e.g.* `hamoco-run --model <path_to_your_model> [additional options]`.

Author
------

[Joris Paret](https://www.linkedin.com/in/joris-paret/)
