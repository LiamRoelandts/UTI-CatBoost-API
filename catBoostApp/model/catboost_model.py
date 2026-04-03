import os
import pandas as pd
import pickle

MODEL_PATH = os.path.join(os.path.dirname(__file__), '../../model/Clf.pkl')

class CatBoostModel:
	def __init__(self):
		with open(MODEL_PATH, 'rb') as file:
			self.model = pickle.load(file)['model']

	def predict(self, df: pd.DataFrame):
		preds = self.model.predict_proba(df)
		return preds.tolist()

catboost_model = CatBoostModel()
