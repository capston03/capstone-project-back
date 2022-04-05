import re


class User:
    class Time:
        def __init__(self, year: int, month: int, day: int):
            self.year = year
            self.month = month
            self.day = day

        def to_string(self):
            return f"{self.year}-{self.month}-{self.day}"

    def _parse_time(self, birthday: str) -> Time:
        p = "^(\d{4})-(\d{2})-(\d{2})$"
        capture_result = re.search(p, birthday)
        group = capture_result.groups()
        if len(group) != 3:
            raise Exception("Input is invalid.")
        else:
            return User.Time(group[0], group[1], group[2])

    def __init__(self, nickname: str, google_id: str, birthday: Time):
        self.nickname = nickname
        self.google_id = google_id
        self.birthday = self._parse_time(birthday)

    def html(self) -> str:
        html_code = ""
        html_code += "<p>----<br>"
        for key, val in self.__dict__.items():
            html_code += "<p>"
            html_code += f"key : {key}<br>"
            if type(val) is User.Time:
                html_code += f"val : {val.to_string()}"
            else:
                html_code += f"val : {val}"
            html_code += "</p>"
        html_code += "</p>"
        return html_code
