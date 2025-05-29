import mysql.connector
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get MySQL connection
_mysql_conn = None
def get_mysql_connection():
    global _mysql_conn
    if _mysql_conn is None or not _mysql_conn.is_connected():
        _mysql_conn = mysql.connector.connect(
            host=settings.MYSQL_HOST,
            user=settings.MYSQL_USER,
            password=settings.MYSQL_PASSWORD,
            database=settings.MYSQL_DATABASE,
        )
    logger.info("MySQL connection established")
    print(settings.MYSQL_HOST, settings.MYSQL_USER, settings.MYSQL_DATABASE, settings.MYSQL_PASSWORD, settings.BASE_URL)
    return _mysql_conn