import math
import numpy as np
import joblib

class ModelTest():

    def __init__(self, weights_path):
        self.regressor = joblib.load(weights_path)
    
    def error_bounds(self, x):
        return 0.1 * 3 ** (math.log2(x))

    def test_regressor_scaling_error(self, input_data, output_labels):
        y_pred = regressor.predict(input_data)
        bounds = self.error_bounds(output_labels)
        lower_bounds = output_labels - bounds
        upper_bounds = output_labels + bounds
        correct_preds = np.logical_and(y_pred >= lower_bounds, y_pred <= upper_bounds)
        accuracy = np.sum(correct_preds) / len(output_labels)
        return accuracy

    def series_testing(self, x_test, y_test):
        num_samples = 50
        random_indices = np.random.randint(0, len(X_test), size=num_samples)
        random_test_samples = x_test[random_indices]
        random_test_labels = y_test[random_indices]
        random_predictions = regressor.predict(random_test_samples)
        print("\nSample Predictions:")
        for i in range(num_samples):
            print("Input: {}\tTrue Value: {}\tPredicted Value: {}".format(random_test_samples[i], random_test_labels[i], random_predictions[i]))

