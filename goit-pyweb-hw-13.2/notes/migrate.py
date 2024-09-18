import pymongo
import psycopg2
from psycopg2.extras import DictCursor
from config import MONGO_URI, POSTGRES_DSN


# Подключение к MongoDB
mongo_client = pymongo.MongoClient(MONGO_URI)
mongo_db = mongo_client['mydatabase']
mongo_collection = mongo_db['mycollection']

# Подключение к PostgreSQL
postgres_conn = psycopg2.connect(POSTGRES_DSN)
postgres_cursor = postgres_conn.cursor()


def migrate_data():
    try:
        # Получите данные из MongoDB
        mongo_data = mongo_collection.find()
        
        # Вставьте данные в PostgreSQL
        for item in mongo_data:
            # Преобразуйте данные из MongoDB в формат, пригодный для PostgreSQL
            field1 = item.get('field1')
            field2 = item.get('field2')
            
            # Выполните вставку в PostgreSQL
            postgres_cursor.execute(
                "INSERT INTO my_table (field1, field2) VALUES (%s, %s)",
                (field1, field2)
            )
        
        # Сохраните изменения
        postgres_conn.commit()
        print("Data migration completed successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")
        postgres_conn.rollback()

# Запустите миграцию
if __name__ == '__main__':
    migrate_data()

# Закройте соединения
postgres_cursor.close()
postgres_conn.close()
mongo_client.close()
