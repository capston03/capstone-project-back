from flask import Flask, render_template, request

from src.handler_db import HandlerDb
from src.model.user import User

app = Flask(__name__)

db_info: dict[str, any] = {
    "host": "db-capstone.cbo8gwqsco77.ap-northeast-2.rds.amazonaws.com",
    "port": 3306,
    "user": "dbadmin",
    "passwd": "rootroot22",
    "db_name": "db_capstone",
    "charset": "utf8mb4"
}

handler_db = HandlerDb(**db_info)


# def add_user(db, user: User):
#     try:
#         with db.cursor() as cursor:
#             sql = f"INSERT INTO user(nickname, google_id, birthday) VALUES(\"{user.nickname}\", \"{user.google_id}\", \"{user.birthday.to_string()}\");"
#             print(sql)
#             cursor.execute(sql)
#             db.commit()
#     except Exception as e:
#         print(f"err : {e}")


@app.route("/")
def home():
    return "Hello, World"


@app.route("/beacon")
def show_beacons():
    list_beacon = handler_db.get_all("beacon")
    return str(list_beacon)


# @app.route("/add_user", methods=("POST", "GET"))
# def add_new_user():
#     if request.method == "POST":
#         nickname = request.form.get("nickname")
#         google_id = request.form.get("google_id")
#         birthday = request.form.get("birthday")
#         new_user = User(nickname, google_id, birthday)
#         add_user(db, new_user)
#         return new_user.html()
#     else:
#         return render_template("add_new_user.html")


# def search_user(gmail_addr: str) -> bool:
#     try:
#         with _db.cursor() as cursor:
#             print("hello")
#             sql = f"SELECT * FROM {table_name};"
#             cursor.execute(sql)
#             return cursor.fetchall()
#     except Exception as e:
#         print(e)
#         return list()


@app.route("/login", methods=["POST"])
def login():
    if not request.is_json:
        return "NOT JSON"
    params: dict[str, str] = request.get_json()
    gmail_id = params.get("gmail_id")
    is_user_existed = handler_db.is_user_existed(gmail_id)
    if not is_user_existed:
        return "USER ACCOUNT IS NOT EXISTED"
    is_user_active = handler_db.is_user_already_logged_in(gmail_id)
    can_login = is_user_existed and not is_user_active
    if can_login:
        handler_db.login(gmail_id)
        return "LOGIN SUCCESS"
    else:
        return "USER IS ALREADY LOGGED IN"


@app.route("/logout", methods=["POST"])
def logout():
    if not request.is_json:
        return "NOT JSON"
    params: dict[str, str] = request.get_json()
    gmail_id = params.get("gmail_id")
    is_user_existed = handler_db.is_user_existed(gmail_id)
    if not is_user_existed:
        return "USER ACCOUNT IS NOT EXISTED"
    is_user_active = handler_db.is_user_already_logged_in(gmail_id)
    can_logout = is_user_existed and is_user_active
    if can_logout:
        handler_db.logout(gmail_id)
        return "LOGOUT SUCCESS"
    else:
        return "USER IS ALREADY LOGGED OUT"


@app.route("/users")
def show_all_user():
    list_user = handler_db.get_all("user")
    return str(list_user)


@app.route("/board")
def boards():
    list_board = handler_db.get_all("board")
    return str(list_board)


if __name__ == "__main__":
    app.run(debug=True, port=8000)
