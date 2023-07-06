import os
import json
from sklearn.ensemble import GradientBoostingRegressor
import joblib

class ModelTrain():

    def gradient_regressor(self, x_train, y_train, n_estimators, learning_rate, max_depth, random_state):
        print("------------ Starting Training -----------")
        regressor = GradientBoostingRegressor(n_estimators=n_estimators, learning_rate=learning_rate, max_depth=max_depth, random_state=random_state, verbose=1)
        regressor.fit(x_train, y_train)
        configs = {
            'n_estimators': n_estimators,
            'learning_rate': learning_rate,
            'max_depth': max_depth,
            'random_state': random_state,
        }
        return self.make_dir(regressor, configs)
    
    def make_dir(self, regressor, configs):
        if not os.path.isdir('weights'):
            os.makedirs('weights')
        model_num = len(os.listdir('models')) + 1
        new_model_dir = os.path.join('models', f'model_{model_num}')
        os.makedirs(new_model_dir)
        joblib.dump(regressor, os.path.join(new_model_dir, 'model.pkl'))
        with open(os.path.join(new_model_dir, 'configs.json'), 'w') as f:
            json.dump(configs, f)
        return os.path.join(new_model_dir, 'model.pkl')
    
    