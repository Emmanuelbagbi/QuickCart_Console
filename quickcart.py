# quickcart.py
import json
import os
from Admin import Admin
from Customer import Customer
from Order import Order
from Product import Product  # Fixed case
from Rider import Rider
from order_status import OrderStatus

class QuickCart:
    def __init__(self):
        self._users = {}
        self._products = {}
        self._orders = {}
        self._current_user = None
        self._next_product_id = 1
        self._next_order_id = 1
        self.load_data()

    def load_data(self):
        if os.path.exists("users.json"):
            with open("users.json", "r") as f:
                user_data = json.load(f)  # Fixed _json to json
                for username, data in user_data.items():
                    role = data["role"]
                    if role == "Customer":
                        self._users[username] = Customer(username, data["password"])
                    elif role == "Rider":
                        self._users[username] = Rider(username, data["password"])
                    elif role == "Admin":
                        self._users[username] = Admin(username, data["password"])

        if os.path.exists("products.json"):
            with open("products.json", "r") as f:
                product_data = json.load(f)  # Fixed _json to json
                for pid, data in product_data.items():
                    self._products[int(pid)] = Product(int(pid), data["name"], data["price"], data["stock"])
                    self._next_product_id = max(self._next_product_id, int(pid) + 1)

    def save_data(self):
        user_data = {u.username: {"password": u._password, "role": u._role} for u in self._users.values()}
        product_data = {p.id: {"name": p._name, "price": p._price, "stock": p._stock} for p in self._products.values()}
        with open("users.json", "w") as f:
            json.dump(user_data, f)  # Fixed _json to json
        with open("products.json", "w") as f:
            json.dump(product_data, f)  # Fixed _json to json

    def register(self, username, password, role):
        if username in self._users:
            print("Username already exists.")
            return
        if role == "Customer":
            self._users[username] = Customer(username, password)
        elif role == "Rider":
            self._users[username] = Rider(username, password)
        elif role == "Admin":
            self._users[username] = Admin(username, password)
        print(f"{role} registered successfully.")
        self.save_data()

    def login(self, username, password):
        user = self._users.get(username)
        if user and user.authenticate(password):
            self._current_user = user
            print(f"Logged in as {username} ({user.role}).")
            return True
        print("Invalid credentials.")
        return False

    def add_product(self, name, price, stock):
        if not isinstance(self._current_user, Admin):
            print("Only admins can add products.")
            return
        self._products[self._next_product_id] = Product(self._next_product_id, name, price, stock)
        print(f"Product {name} added.")
        self._next_product_id += 1
        self.save_data()

    def restock_product(self, product_id, quantity):
        if not isinstance(self._current_user, Admin):
            print("Only admins can restock products.")
            return
        product = self._products.get(product_id)
        if product and product.update_stock(quantity):
            print(f"Restocked {product._name} by {quantity}.")
            self.save_data()
        else:
            print("Invalid product ID or stock update.")

    def browse_products(self):
        for product in self._products.values():
            print(product)

    def place_order(self, product_id, quantity):
        if not isinstance(self._current_user, Customer):
            print("Only customers can place orders.")
            return
        product = self._products.get(product_id)
        if product and product.stock >= quantity:
            order = Order(self._next_order_id, self._current_user, product, quantity)
            self._orders[self._next_order_id] = order
            product.update_stock(-quantity)
            self._current_user.add_order(order)
            print(f"Order placed: {order}")
            self._next_order_id += 1
            self.save_data()
        else:
            print("Invalid product ID or insufficient stock.")

    def view_pending_orders(self):
        if not isinstance(self._current_user, Rider):
            print("Only riders can view pending orders.")
            return
        for order in self._orders.values():
            if order.status == OrderStatus.PENDING:
                print(order)

    def accept_order(self, order_id):
        if not isinstance(self._current_user, Rider):
            print("Only riders can accept orders.")
            return
        order = self._orders.get(order_id)
        if order and order.status == OrderStatus.PENDING:
            order.assign_rider(self._current_user)
            self._current_user.assign_order(order)
            print(f"Order {order_id} accepted.")
            self.save_data()
        else:
            print("Invalid order ID or order not pending.")

    def update_order_status(self, order_id, status):
        if not isinstance(self._current_user, Rider):
            print("Only riders can update order status.")
            return
        order = self._orders.get(order_id)
        if order and order._rider == self._current_user and status in [s.value for s in OrderStatus]:
            order.update_status(OrderStatus(status))
            print(f"Order {order_id} status updated to {status}.")
            self.save_data()
        else:
            print("Invalid order ID, not assigned to you, or invalid status.")

    def view_all_orders(self):
        if not isinstance(self._current_user, Admin):
            print("Only admins can view all orders.")
            return
        for order in self._orders.values():
            print(order)

    def view_order_history(self):
        if not isinstance(self._current_user, Customer):
            print("Only customers can view order history.")
            return
        for order in self._current_user.view_history():
            print(order)

    def run(self):
        while True:
            if not self._current_user:
                print("""
                Main Menu:
                1. Register
                2. Login
                3. Exit
                """)
                choice = input("Enter choice: ")
                try:
                    if choice == "1":
                        username = input("Username: ")
                        password = input("Password: ")
                        role = input("Role (Customer/Rider/Admin): ")
                        if role in ["Customer", "Rider", "Admin"]:
                            self.register(username, password, role)
                        else:
                            print("Invalid role.")
                    elif choice == "2":
                        username = input("Username: ")
                        password = input("Password: ")
                        self.login(username, password)
                    elif choice == "3":
                        print("Exiting...")
                        break
                    else:
                        print("Invalid choice.")
                except Exception as e:
                    print(f"Error: {e}")
            else:
                print(self._current_user.display_menu())
                choice = input("Enter choice: ")
                try:
                    if isinstance(self._current_user, Customer):
                        if choice == "1":
                            self.browse_products()
                        elif choice == "2":
                            product_id = int(input("Product ID: "))
                            quantity = int(input("Quantity: "))
                            self.place_order(product_id, quantity)
                        elif choice == "3":
                            self.view_order_history()
                        elif choice == "4":
                            self._current_user = None
                        else:
                            print("Invalid choice.")
                    elif isinstance(self._current_user, Rider):
                        if choice == "1":
                            self.view_pending_orders()
                        elif choice == "2":
                            order_id = int(input("Order ID: "))
                            self.accept_order(order_id)
                        elif choice == "3":
                            order_id = int(input("Order ID: "))
                            status = input("Status (Accepted/Delivered): ")
                            self.update_order_status(order_id, status)
                        elif choice == "4":
                            self._current_user = None
                        else:
                            print("Invalid choice.")
                    elif isinstance(self._current_user, Admin):
                        if choice == "1":
                            name = input("Product Name: ")
                            price = float(input("Price: "))
                            stock = int(input("Stock: "))
                            self.add_product(name, price, stock)
                        elif choice == "2":
                            product_id = int(input("Product ID: "))
                            quantity = int(input("Quantity to restock: "))
                            self.restock_product(product_id, quantity)
                        elif choice == "3":
                            self.view_all_orders()
                        elif choice == "4":
                            self._current_user = None
                        else:
                            print("Invalid choice.")
                except ValueError:
                    print("Invalid input. Please enter valid numbers where required.")
                except Exception as e:
                    print(f"Error: {e}")

if __name__ == "__main__":
    print("QuickCart...")
    app = QuickCart()
    app.run()