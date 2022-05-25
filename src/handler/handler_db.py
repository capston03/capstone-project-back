from typing import Dict, List
import pymysql

from config.DB_config import DB_CONFIG


# Handler used to handle the AWS RDS database.
class HandlerDB:
    def __init__(self,
                 host: str,
                 port: int,
                 user: str,
                 passwd: str,
                 db_name: str,
                 charset: str):
        self.__host = host
        self.__port = port
        self.__user = user
        self.__passwd = passwd
        self.__db_name = db_name
        self.__charset = charset

    def connect_db(self):
        """
        Connect the database (AWS RDS)
        :return: DB connection
        """
        return pymysql.connect(host=self.__host,
                               port=self.__port,
                               user=self.__user,
                               passwd=self.__passwd,
                               db=self.__db_name,
                               charset=self.__charset)

    def get_all(self, table_name: str) -> List[str]:
        """
        Get all records in table.
        :param table_name: Table name
        :return:
        """
        with self.connect_db() as db:
            try:
                with db.cursor() as cursor:
                    sql = f"SELECT * FROM {table_name};"
                    cursor.execute(sql)
                    test = cursor.fetchall()
                    return list(cursor.fetchall())
            except Exception as e:
                print(f"error : {e}")
                return list()


handler_db = HandlerDB(**DB_CONFIG)
