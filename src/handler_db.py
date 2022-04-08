# host='db-capstone.cbo8gwqsco77.ap-northeast-2.rds.amazonaws.com',
#                      port=3306, user='dbadmin', passwd='rootroot22', db='db_capstone', charset='utf8mb4'
import pymysql


class HandlerDb:
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

    def __connect_db(self):
        return pymysql.connect(host=self.__host,
                               port=self.__port,
                               user=self.__user,
                               passwd=self.__passwd,
                               db=self.__db_name,
                               charset=self.__charset)

    def is_user_existed(self, gmail_addr: str) -> bool:
        with self.__connect_db() as db:
            try:
                with db.cursor() as cursor:
                    sql = f"SELECT EXISTS(SELECT * FROM user WHERE gmail_addr = '{gmail_addr}' LIMIT 1) AS SUCCESS"
                    cursor.execute(sql)
                    result = cursor.fetchall()
                    if list(result.values())[0]:
                        return True
                    return False
            except Exception as e:
                print(f"error : {e}")
                return False

    def get_all(self, table_name: str) -> dict[str, any]:
        with self.__connect_db() as db:
            try:
                with db.cursor() as cursor:
                    sql = f"SELECT * FROM '{table_name}';"
                    cursor.execute(sql)
                    return dict(cursor.fetchall())
            except Exception as e:
                print(f"error : {e}")
                return dict()
