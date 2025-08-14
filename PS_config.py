import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', 5432),
    'database': os.getenv('DB_NAME', 'it_asset_db'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'your_password')
}

# You can also set these values directly here if you prefer
# DB_CONFIG = {
#     'host': 'localhost',
#     'port': 5432,
#     'database': 'it_asset_db',
#     'user': 'postgres',
#     'password': 'your_password'
# }

