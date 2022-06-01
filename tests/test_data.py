#!/usr/bin/env python

import unittest
import os

from hamoco import ClassificationModel
import numpy

class Test(unittest.TestCase):

    def setUp(self):
        self.data_dir = os.path.join(os.path.dirname(__file__), 'data')
        
    def test_model_building(self):

        # Create model and read data files
        model = ClassificationModel()
        model.read_dataset(self.data_dir)
        self.assertEqual(set(model.classes), set([0,1,2,3,4,5]), 'not the expected labels')

        # Process the data
        model.process_dataset()
        
        # Train the model
        model.train(hidden_layers=(5,5,5), epochs=5)
        model.save_model(os.path.join(self.data_dir, 'phony_model.h5'))
        
if __name__ == '__main':
    unittest.main()
