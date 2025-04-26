import os
from dotenv import load_dotenv

def load_env():
    load_dotenv()
    return {
        "INPUT_PATH": os.getenv("FEATURE_ENGINEERING_INPUT_PATH", "./data/filtered/"),
        "OUTPUT_PATH": os.getenv("FEATURE_ENGINEERING_OUTPUT_PATH", "./data/features/"),
        "LOG_LEVEL": os.getenv("LOG_LEVEL", "INFO"),
    }
