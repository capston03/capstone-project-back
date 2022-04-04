import pymysql
import numpy as np
from flask import Flask, render_template, request
from pymysql import Connection

from model.user import User


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


@app.route("/user", methods=("POST", "GET"))
def users():
    if request.method == "POST":
        nickname = request.form.get("nickname")
        google_id = request.form.get("google_id")
        birthday = request.form.get("birthday")
        new_user = User(nickname, google_id, birthday)
        return new_user.html()
    else:
        user_list = get_entity_list_in_table(db, "user")
        html_code = str(user_list)
        return html_code


@app.route("/users")
def showUsers():
    user_list = get_entity_list_in_table(db, "user")
    html_code = str(user_list)
    return html_code


@app.route("/board")
def boards():
    board_list = get_entity_list_in_table(db, "board")
    html_code = str(board_list)
    return html_code


if __name__ == "__main__":
    app.run(debug=True)
