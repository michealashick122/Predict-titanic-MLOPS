import pandas as pd
import psycopg2
from sqlalchemy import create_engine
from src.logger import get_logger
from src.custom_exception import CustomException
import os
from sklearn.model_selection import train_test_split
import sys
from config.database_config import DB_CONFIG
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.paths_config import RAW_DIR, TRAIN_PATH, TEST_PATH, RAW_DATA_PATH

logger = get_logger(__name__)

class DataIngestion:
    def __init__(self, db_params, output_dir):
        self.db_params = db_params
        self.output_dir = output_dir
        self.engine = None
        os.makedirs(self.output_dir, exist_ok=True)
        
    def connect_to_db(self):
        try:
            conn_string = f"postgresql://{self.db_params['user']}:{self.db_params['password']}@{self.db_params['host']}:{self.db_params['port']}/{self.db_params['dbname']}"
            self.engine = create_engine(conn_string)
            logger.info("Database connection engine created successfully.")
            return self.engine
        except Exception as e:
            logger.error(f"Error connecting to the database: {e}")
            raise CustomException("Database connection error", sys)
    
    def extract_data(self):
        try:
            engine = self.connect_to_db()
            query = "SELECT * FROM public.titanic"
            df = pd.read_sql_query(query, engine)
            logger.info("Data extracted successfully from the database.")
            return df
        except Exception as e:
            logger.error(f"Error extracting data: {e}")
            raise CustomException("Data extraction error", sys)
    
    def save_data(self, df):
        try:
            # Use RAW_DATA_PATH from paths_config
            df.to_csv(RAW_DATA_PATH, index=False)
            train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)
            train_df.to_csv(TRAIN_PATH, index=False)
            test_df.to_csv(TEST_PATH, index=False)
            logger.info(f"Data saved successfully to {RAW_DATA_PATH}")
            logger.info(f"Train and test data saved to {TRAIN_PATH} and {TEST_PATH} respectively.")
            
        except Exception as e:
            logger.error(f"Error saving data: {e}")
            raise CustomException("Data saving error", sys)
    
    def run(self):
        try:
            logger.info("Starting data ingestion process.")
            df = self.extract_data()
            self.save_data(df)
            logger.info("Data ingestion process completed successfully.")
        except CustomException as ce:
            logger.error(f"Error while running pipeline: {ce}")
            raise CustomException("Data pipeline error", sys)

if __name__ == "__main__":
    data_ingestion = DataIngestion(DB_CONFIG, RAW_DIR)
    data_ingestion.run()