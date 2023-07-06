from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error
import joblib
from DataLoader import DataLoader
import numpy as np
from ModelTrain import ModelTrain
from ModelTest import ModelTest

folder_path = "/srv/sqc/volatility_exploration/featured_files"
test_folder_path = "/home/eugenechoi/Documents/backtester/local-storage"
weights_path = "/home/eugenechoi/Documents/backtester/models/volatility-models/models/model_2/model.pkl"

def train(x_train, y_train, n_estimators, learning_rate, max_depth, random_state):
    model = ModelTrain()
    weights_path = model.gradient_regressor(x_train, y_train, n_estimators, learning_rate, max_depth, random_state)
    return weights_path

def test(x_test, y_test, weights_path):
    model_tester = ModelTest(weights_path)
    accuracy = model_tester.test_regressor_scaling_error(x_test, y_test)
    print(accuracy)


def main(mode, weights_path=""):
    data = DataLoader(test_folder_path)
    x, y = data.load_volatility()
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)
    if mode == "test":
        test(x_test, y_test, weights_path)
    elif mode == "train":
        train(x_train, y_train, n_estimators=100, learning_rate=.1, max_depth=5, random_state = 42)
    elif mode=="train_test":
        weights_path = train(x_train, y_train)
    
main("test", weights_path)

