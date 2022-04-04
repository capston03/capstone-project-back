import pymysql
import numpy as np
from flask import Flask
from pymysql import Connection


db = pymysql.connect(host='db-capstone.cbo8gwqsco77.ap-northeast-2.rds.amazonaws.com',
                     port=3306, user='dbadmin', passwd='rootroot22', db='db_capstone', charset='utf8mb4')

app = Flask(__name__)


def get_entity_list_in_table(db, table_name: str) -> list[tuple]:
    try:
        with db.cursor() as cursor:
            print("hello")
            sql = f"SELECT * FROM {table_name};"
            cursor.execute(sql)
            return cursor.fetchall()
    except Exception as e:
        print(e)
        return ("nil", "nil")


@app.route("/")
def home():
    return "Hello, World"


@app.route("/beacon")
def showBeacons():
    beacon_list = get_entity_list_in_table(db, "beacon")
    html_code = str(beacon_list)
    return html_code


@app.route("/user")
def showUsers():
    user_list = get_entity_list_in_table(db, "user")
    html_code = str(user_list)
    return html_code


@app.route("/board")
def showBoards():
    board_list = get_entity_list_in_table(db, "board")
    html_code = str(board_list)
    return html_code


if __name__ == "__main__":
    app.run(debug=True)
