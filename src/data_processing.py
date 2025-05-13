import pandas as pd
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE
from src.feature_store import RedisFeatureStore
from src.logger import get_logger
from src.custom_exception import CustomException
from config.paths_config import TRAIN_PATH, TEST_PATH
import os

logger = get_logger(__name__)

class DataProcessing:
    def __init__ (self,train_data_path , test_data_path,feature_store : RedisFeatureStore):
        self.train_data_path = train_data_path
        self.test_data_path = test_data_path
        self.data = None
        self.test_data = None
        self.x_train = None
        self.y_train = None
        self.x_test = None
        self.y_test = None
        self.x_resampled = None
        self.y_resampled = None
        self.feature_store = feature_store
        logger.info("DataProcessing class initialized.")
    
    def load_data(self):
        try:
            self.data = pd.read_csv(self.train_data_path)
            self.test_data = pd.read_csv(self.test_data_path)
            logger.info("Data loaded successfully.")
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            raise CustomException("Data loading error", str(e))
    def preprocess_data(self):
        try:
            self.data['Age'].fillna(self.data['Age'].median(), inplace=True)
            self.data['Embarked'].fillna(self.data['Embarked'].mode()[0], inplace=True)
            self.data['Sex'] = self.data['Sex'].map({'male':0 , 'female':1})
            self.data['Embarked'] = self.data['Embarked'].map({'C':0 , 'Q':1, 'S':2})
            self.data['FamilySize'] = self.data['SibSp'] + self.data['Parch'] + 1
            self.data['Isalone'] = (self.data['FamilySize'] == 1).astype(int) #This creates a Boolean Series where each value is: True-> 1, False-> 0
            self.data['HasCabin'] = self.data['Cabin'].notnull().astype(int) #This creates a Boolean Series where each value is: True-> 1, False-> 0
            self.data['Title'] = self.data['Name'].str.extract(' ([A-Za-z]+)\.', expand=False).map({
                'Mr': 0,
                'Miss': 1,
                'Mrs': 2,
                'Master': 3,
                'Rare':4
            }).fillna(4) #This creates a new column 'Title' with the extracted title from the name
            self.data['Pclass_fair'] = self.data['Pclass'] * self.data['Fare']
            self.data['Age_fair'] = self.data['Age'] * self.data['Fare']
            logger.info("Data preprocessed successfully.")
        except Exception as e:
            logger.error(f"Error preprocessing data: {e}")
            raise CustomException("Data preprocessing error", str(e))
    def handle_imbalance(self):
        try:
            smote = SMOTE(random_state=42)
            x = self.data.drop(['Survived', 'PassengerId', 'Name', 'Ticket', 'Cabin'], axis=1)
            y = self.data['Survived']
            smote = SMOTE(random_state=42)
            self.x_resampled, self.y_resampled = smote.fit_resample(x, y)
            #self.x_train, self.x_test, self.y_train, self.y_test = train_test_split(self.x_resampled, self.y_resampled, test_size=0.2, random_state=42)
        except Exception as e:
            logger.error(f"Error handling imbalance: {e}")
            raise CustomException("Imbalance handling error", str(e))
    def store_features_in_redis(self):
        try:
            batch_data = {}
            for idx , row in self.data.iterrows():
                entity_id = row['PassengerId']
                features = row.drop([ 'Name', 'Ticket', 'Cabin']).to_dict()
                batch_data[entity_id] = features
            self.feature_store.store_batch_features(batch_data)
            logger.info("Features stored in Redis successfully.")
        except Exception as e:
            logger.error(f"Error storing features in Redis: {e}")
            raise CustomException("Feature storage error", str(e))
    def run(self):
        try:
            logger.info("Starting data processing pipeline.")
            self.load_data()
            self.preprocess_data()
            self.handle_imbalance()
            self.store_features_in_redis()
            logger.info("Data processing pipeline completed successfully.")
        except CustomException as ce:
            logger.error(f"Error while running pipeline: {ce}")
            raise CustomException("Data processing pipeline error", str(ce))



if __name__ == "__main__":
    feature_store = RedisFeatureStore()
    data_processer  = DataProcessing(TRAIN_PATH, TEST_PATH, feature_store)
    data_processer.run()
    logger.info("Data processing completed.")
    
    