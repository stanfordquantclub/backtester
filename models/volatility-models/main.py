from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error
import joblib
from DataLoader import DataLoader
import numpy as np
from ModelTrain import ModelTrain
from ModelTest import ModelTest

folder_path = "/srv/sqc/volatility_exploration/featured_files"


def train(x_train, y_train, n_estimators, learning_rate, max_depth):
    model = ModelTrain()
    weights_path = model.gradient_regressor(x_train, y_train, n_estimators, learning_rate, max_depth)
    return weights_path

def main(mode, weights_path=""):
    data = DataLoader(folder_path)
    x, y = data.load_volatility()
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)
    if mode == "test":
        test()
    elif mode == "train":
        train(x_train, y_train, n_estimators=100, learning_rate=.1, max_depth=5)
    elif mode=="train_test":
        weights_path = train(x_train, y_train)
    
main("train")

