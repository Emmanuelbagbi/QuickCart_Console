
from User import User

class Admin(User):
    def __init__(self, username, password):
        super().__init__(username, password, "Admin")

    def display_menu(self):
        return """
        Admin Menu:
        1. Add Product
        2. Restock Product
        3. View All Orders
        4. Logout
        """
