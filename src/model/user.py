import re


class User:
    class Time:
        def __init__(self, year: int, month: int, day: int):
            self.year = year
            self.month = month
            self.day = day

    def _parse_time(self, birthday: str) -> Time:
        p = "^datetime\.date\((\d+), (\d+), (\d+)\)$"
        capture_result = re.search(p, birthday)
        if len(capture_result) != 4:
            raise Exception("Input is invalid.")
        else:
            return User.Time(capture_result[1], capture_result[2], capture_result[3])

    def __init__(self, nickname: str, google_id: str, birthday: Time):
        self.nickname = nickname
        self.google_id = google_id
        self.birthday = self._parse_time(birthday)

    def convert_to_html(self) -> str:
        html_code = ""
        for key, val in range(self.__dict__):
            html_code += "----"
            html_code += f"key:{key}\nval:{val}"
        return html_code
