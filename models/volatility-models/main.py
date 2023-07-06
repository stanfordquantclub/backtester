from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error
import joblib
from DataLoader import DataLoader
import numpy as np
from ModelTrain import ModelTrain
from ModelTest import ModelTest

folder_path = "/srv/sqc/volatility_exploration/featured_files"


def test():
    

def train(x_train, y_train):
    model = ModelTrain()
    weights_path = model.gradient_regressor(x_train, y_train, n_estimators, learning_rate, max_depth)
    return 

def main(mode, weights_path=""):
    data = DataLoader(folder_path)
    x, y = data.load_volatility()
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)
    if mode == "test":
        test()
    else if mode == "train":
        train()
    else if mode=="train_test":
        weights_path = train(x_train, y_train)




regressor = GradientBoostingRegressor(n_estimators=200, learning_rate=0.1, max_depth=1, random_state=42, verbose=1)

# Fit the regressor to the training data
regressor.fit(X_train, y_train)

# Save the model to a file
joblib.dump(regressor, 'model.pkl')

# # Load the model from the file (for demonstration purposes, normally you would do this in another script)
# regressor = joblib.load('model.pkl')

# Make predictions on the test data
y_pred = regressor.predict(X_test)

# Evaluate the model
mse = mean_squared_error(y_test, y_pred)
print("The mean squared error (MSE) on test set: {:.4f}".format(mse))

# Print some sample outputs using random data points from the test set
num_samples = 50
random_indices = np.random.randint(0, len(X_test), size=num_samples)
random_test_samples = X_test[random_indices]
random_test_labels = y_test[random_indices]

random_predictions = regressor.predict(random_test_samples)
print("\nSample Predictions:")
for i in range(num_samples):
    print("Input: {}\tTrue Value: {}\tPredicted Value: {}".format(random_test_samples[i], random_test_labels[i], random_predictions[i]))
