from src.logger import get_logger
from src.custom_exception import CustomException
import pandas as pd
from src.feature_store import RedisFeatureStore
from sklearn.model_selection import train_test_split
import os
from sklearn.model_selection import RandomizedSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from config.paths_config import *
import pickle
logger = get_logger(__name__)

class ModelTraining:
    def __init__(self, feature_store: RedisFeatureStore,model_save_path = "artifacts/models/"):
        self.feature_store = feature_store
        self.model_save_path = model_save_path
        self.model = None
        os.makedirs(self.model_save_path, exist_ok=True)
        logger.info("ModelTraining class initialized.")
        
    def load_data_from_redis(self,entity_ids):
        try:
            logger.info("Loading data from Redis...")
            data = []
            for entity_id in entity_ids:
                featires = self.feature_store.get_features(entity_id)
                if featires:
                    data.append(featires)
                else:
                    logger.warning(f"No features found for entity_id: {entity_id}")
            return data
        except Exception as e:
            logger.error(f"Error loading data from Redis: {e}")
            raise CustomException("Error loading data from Redis", e)
    def prepare_data(self):
        try:
            entity_ids = self.feature_store.get_all_entity_ids()
            logger.info("Preparing data for training...")
            train_entity_ids , test_entity_ids = train_test_split(entity_ids, test_size=0.2, random_state=42)
            train_data = self.load_data_from_redis(train_entity_ids)
            test_data = self.load_data_from_redis(test_entity_ids)
            train_df = pd.DataFrame(train_data)
            test_df = pd.DataFrame(test_data)
            train_df.to_csv(TEST_TRAIN_PATH,index=False) #FOR TESTING
            test_df.to_csv(TEST_TEST_PATH,index=False) #for testttt
            x_train = train_df#.drop(columns=['Survived'],axis=1)
            x_test = test_df#.drop(columns=['Survived'],axis=1)
            y_train = train_df['Survived']
            y_test = test_df['Survived']
            # print("**************************************************")
            # print(y_test.info())
            logger.info("Data prepared successfully.")
            return x_train, x_test, y_train, y_test
        #          x_train, x_test, y_train, y_test
        except Exception as e:
            logger.error(f"Error preparing data: {e}")
            raise CustomException("Error preparing data", e)
    def hyperparameter_tuning(self,x_train, y_train):
        try:
            params_distributions = {
            'n_estimators': [100, 200, 300],  
            'max_depth': [10, 20, 30],
            'min_samples_split': [2, 5],
            'min_samples_leaf': [1, 2],       
            'max_features': ['auto', 'sqrt'],  
            'bootstrap': [True, False]         
             }
            rf = RandomForestClassifier(random_state=42)
            random_search = RandomizedSearchCV(rf,params_distributions , n_iter=10,cv=3,scoring='accuracy')
            random_search.fit(x_train,y_train)
            return random_search.best_estimator_
        except Exception as e:
            logger.error(f"Error while hyperparameter tuning data: {e}")
            raise CustomException("Error hyperparameter tuning data", e)
    def train_and_evaluate(self, x_train, x_test, y_train, y_test):
        try:
            best_rf = self.hyperparameter_tuning(x_train , y_train)
            #best_rf.fit(x_train,y_train)
            print("************for dubing***********************************")
            y_pred = best_rf.predict(x_test)
            accuracy = accuracy_score(y_test,y_pred)
            logger.info(f"Accuracy of RF is: {accuracy}")
            self.save_model(best_rf)
            return accuracy
        except Exception as e:
            logger.error(f"Error in model training and evaluation: {e}")
            raise CustomException("Model training and evaluation error", e)
    def save_model(self,model):
        try:
            model_filename = f"{self.model_save_path}random_forest_model.pkl"            
            os.makedirs(os.path.dirname(model_filename), exist_ok=True)
            with open(model_filename,'wb') as model_file:
                pickle.dump(model, model_file)
            logger.info(f"Model saved at {model_filename}")
        except Exception as e:
            logger.error(f"Error while saving model: {e}")
            raise CustomException("Error while saving model:", e)
    def run(self):
        try:
            logger.info("Starting training pipeline")
            x_train, x_test, y_train, y_test = self.prepare_data()
            accuracy = self.train_and_evaluate(x_train, x_test, y_train, y_test)
            logger.info(f"Model training pipeline is complete")
        except Exception as e:
            logger.error(f"Error while training pepeline: {e}")
            raise CustomException("Error while training pepeline:", e)
            
if __name__ == "__main__":
    featurestore = RedisFeatureStore()
    modeltrainer = ModelTraining(featurestore)
    modeltrainer.run()








