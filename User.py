class User:
    def __init__(self, username, password, role):
        self._username = username
        self._password = password
        self._role = role

    @property
    def username(self):
        return self._username

    @property
    def role(self):
        return self._role

    def authenticate(self, password):
        return self._password == password

    def display_menu(self):
        pass