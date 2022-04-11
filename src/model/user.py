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

    def __init__(self, nickname: str,
                 gmail_id: str,
                 birthday: str,
                 identity: str,
                 is_active: bool):
        self.nickname = nickname
        self.gmail_id = gmail_id
        self.birthday = self._parse_time(birthday)
        self.identity = identity
        self.is_active = is_active
