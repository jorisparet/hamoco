#!/usr/bin/env python

import argparse

from hamoco import ClassificationModel
from hamoco.models import __default_model__

def main():

    # Parser
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    description = f"""Provided a path to a directory with relevant data, {parser.prog} 
    trains a customizable classification model based on a standard neural network to
    predict a hand pose. This classification model can then be used in the main application
    in place of the one provided by default.""".replace('\n',' ')
    parser.description = description
    parser.add_argument('path_to_model', 
                        type=str,
                        help='Path to save the newly trained model')
    parser.add_argument('path_to_data', 
                        type=str,
                        help='Path to the directory containing the dataset to be used for training')
    parser.add_argument('-H', '--hidden_layers', 
                        nargs='+',
                        type=int,
                        help='Dimensions of the hidden layers (e.g. -H 50 25')
    parser.add_argument('-l', '--learning_rate', 
                        type=float,
                        default=0.01,
                        help='Learning rate')
    parser.add_argument('-e', '--epochs', 
                        type=int,
                        default=15,
                        help='Number of epochs for training')
    parser.add_argument('-t', '--test_size', 
                        type=float,
                        default=0.3,
                        help='Fraction of data to use for validation (between 0 and 1)')
    args = parser.parse_args()
    # Custom variables linked to parser
    path_to_model = args.path_to_model
    path_to_data = args.path_to_data
    hidden_layers = args.hidden_layers
    learning_rate = args.learning_rate
    epochs = args.epochs
    test_size = args.test_size

    # Train the model
    model = ClassificationModel()
    model.read_dataset(path_to_data)
    model.process_dataset()
    model.train(hidden_layers=hidden_layers,
                learning_rate=learning_rate,
                epochs=epochs,
                test_size=test_size)
    model.save_model(path_to_model)

if __name__ == '__main__':
    main()