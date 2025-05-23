import os

# Define base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Define directories
RAW_DIR = os.path.join(BASE_DIR, "artifacts", "raw")  # Fixed typo in ""
PROCESSED_DIR = os.path.join(BASE_DIR, "artifacts", "processed")
TEST_DIR = os.path.join(BASE_DIR, "artifacts", "test")


# Define file paths
RAW_DATA_PATH = os.path.join(RAW_DIR, "raw_data.csv")
TRAIN_PATH = os.path.join(PROCESSED_DIR, "titanic_train.csv")
TEST_PATH = os.path.join(PROCESSED_DIR, "titanic_test.csv")
# Define file paths
TEST_TRAIN_PATH = os.path.join(TEST_DIR, "test_train.csv")
TEST_TEST_PATH = os.path.join(TEST_DIR, "test_test.csv")

# Create directories if they don't exist
os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(TEST_DIR, exist_ok= True)