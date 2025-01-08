import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    INFURA_URL = os.getenv('INFURA_URL')
    DATABASE_URL = os.getenv('DATABASE_URL')
    ENTRYPOINT_ADDRESS = '0x0000000071727de22e5e9d8baf0edac6f37da032'
    POLLING_INTERVAL = 5  # secondes entre chaque vérification
    USER_OPERATION_EVENT_TOPIC = '0x49628fd1471006c1482da88028e9ce4dbb080b815c9b0344d39e5a8e6ec1419f' 