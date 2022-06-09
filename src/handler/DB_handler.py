from typing import List
import pymysql

from secure.DB_config import DB_CONFIG


# Handler used to handle the AWS RDS database.
class DBHandler:
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

    def connect(self):
        return pymysql.connect(host=self.__host,
                               port=self.__port,
                               user=self.__user,
                               passwd=self.__passwd,
                               db=self.__db_name,
                               charset=self.__charset)


DB_handler = DBHandler(**DB_CONFIG)
