# Importing Essential Libraries:

import pandas as pd
import numpy as np
import pickle, joblib


class PipelineTester:
  def __init__(self, pipeline_path: str, test_data: pd.DataFrame):
    self.pipeline_path = pipeline_path
    self.test_data = test_data

  def predict(self):
    with open(self.pipeline_path, 'rb') as file:
      loaded_pipeline = pickle.load(file)


    # Get the probability scores for each class
    probability_scores = loaded_pipeline.predict_proba(self.test_data)

    # Accessing the probability for Closed class
    closed_class_prob = probability_scores[:, 0]

    return closed_class_prob

 
class PipelineTesterMulticlass:
  def __init__(self, pipeline_path: str, test_data: pd.DataFrame):
    self.pipeline_path = pipeline_path
    self.test_data = test_data

  def predict(self):
    with open(self.pipeline_path, 'rb') as file:
      loaded_pipeline = pickle.load(file)

    # Get the probability scores for each class
    predicted_class = loaded_pipeline.predict(self.test_data)

    return predicted_class
