# from flask import Flask

# app = Flask(__name__)
#
#
# @app.route('/')
# def hello():
#     return 'Hello Flask World'
#
#
# if __name__ == '__main__':
#     app.run()


import pymysql
from flask import Flask, render_template, request

from model.user import User

db = pymysql.connect(host='db-capstone.cbo8gwqsco77.ap-northeast-2.rds.amazonaws.com',
                     port=3306, user='dbadmin', passwd='rootroot22', db='db_capstone', charset='utf8mb4')

app = Flask(__name__)


def get_entity_list_in_table(_db, table_name: str):
    try:
        with _db.cursor() as cursor:
            print("hello")
            sql = f"SELECT * FROM {table_name};"
            cursor.execute(sql)
            return cursor.fetchall()
    except Exception as e:
        print(e)
        return list()


def add_user(db, user: User):
    try:
        with db.cursor() as cursor:
            sql = f"INSERT INTO user(nickname, google_id, birthday) VALUES(\"{user.nickname}\", \"{user.google_id}\", \"{user.birthday.to_string()}\");"
            print(sql)
            cursor.execute(sql)
            db.commit()
    except Exception as e:
        print(f"err : {e}")


@app.route("/")
def home():
    return "Hello, World"


@app.route("/beacon")
def show_beacons():
    beacon_list = get_entity_list_in_table(db, "beacon")
    html_code = str(beacon_list)
    return html_code


@app.route("/add_user", methods=("POST", "GET"))
def add_new_user():
    if request.method == "POST":
        nickname = request.form.get("nickname")
        google_id = request.form.get("google_id")
        birthday = request.form.get("birthday")
        new_user = User(nickname, google_id, birthday)
        add_user(db, new_user)
        return new_user.html()
    else:
        return render_template("add_new_user.html")


@app.route("/users")
def show_users():
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
