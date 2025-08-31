from User import User

class Rider(User):
    def __init__(self, username, password):
        super().__init__(username, password, "Rider")
        self._assigned_orders = []

    def display_menu(self):
        return """
        Rider Menu:
        1. View Pending Orders
        2. Accept Order
        3. Update Order Status
        4. Logout
        """

    def assign_order(self, order):
        self._assigned_orders.append(order)

    def view_assigned_orders(self):
        return self._assigned_orders