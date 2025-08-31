
from User import User

class Customer(User):
    def __init__(self, username, password):
        super().__init__(username, password, "Customer")
        self._order_history = []

    def display_menu(self):
        return """
        Customer Menu:
        1. Browse Products
        2. Place Order
        3. View Order History
        4. Logout
        """

    def add_order(self, order):
        self._order_history.append(order)

    def view_history(self):
        return list(self._order_history)
