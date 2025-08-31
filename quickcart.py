# quickcart.py
import json
import os
from Admin import Admin
from Customer import Customer
from Order import Order
from Product import Product
from Rider import Rider
from order_status import OrderStatus

USERS_FILE = "users.json"
PRODUCTS_FILE = "products.json"
ORDERS_FILE = "orders.json"

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
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, "r") as f:
                user_data = json.load(f)
                for username, data in user_data.items():
                    role = data.get("role")
                    pwd = data.get("password", "")
                    if role == "Customer":
                        self._users[username] = Customer(username, pwd)
                    elif role == "Rider":
                        self._users[username] = Rider(username, pwd)
                    elif role == "Admin":
                        self._users[username] = Admin(username, pwd)


        if os.path.exists(PRODUCTS_FILE):
            with open(PRODUCTS_FILE, "r") as f:
                product_data = json.load(f)
                for pid_str, data in product_data.items():
                    pid = int(pid_str)
                    self._products[pid] = Product(pid, data["name"], data["price"], data["stock"])
                    self._next_product_id = max(self._next_product_id, pid + 1)

        # Orders
        if os.path.exists(ORDERS_FILE):
            with open(ORDERS_FILE, "r") as f:
                order_data = json.load(f)
                max_id = 0
                for oid_str, data in order_data.items():
                    data["id"] = int(oid_str)
                    order = Order.from_dict(data, self._users, self._products)
                    if order:
                        self._orders[order.id] = order
                        max_id = max(max_id, order.id)
                self._next_order_id = max(self._next_order_id, max_id + 1)

        for order in self._orders.values():
            if isinstance(order.customer, Customer):
                order.customer.add_order(order)
            if order.rider and isinstance(order.rider, Rider):
                order.rider.assign_order(order)

    def save_data(self):
 
        user_data = {
            u.username: {"password": getattr(u, "_password", ""), "role": u.role}
            for u in self._users.values()
        }
        with open(USERS_FILE, "w") as f:
            json.dump(user_data, f, indent=2)


        product_data = {p.id: p.to_dict() for p in self._products.values()}
        with open(PRODUCTS_FILE, "w") as f:
            json.dump(product_data, f, indent=2)

        order_data = {o.id: o.to_dict() for o in self._orders.values()}
        with open(ORDERS_FILE, "w") as f:
            json.dump(order_data, f, indent=2)

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
        else:
            print("Invalid role.")
            return
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
        if stock < 0 or price < 0:
            print("Price and stock must be non-negative.")
            return
        self._products[self._next_product_id] = Product(self._next_product_id, name, price, stock)
        print(f"Product '{name}' added with ID {self._next_product_id}.")
        self._next_product_id += 1
        self.save_data()

    def restock_product(self, product_id, quantity):
        if not isinstance(self._current_user, Admin):
            print("Only admins can restock products.")
            return
        if quantity <= 0:
            print("Quantity to restock must be greater than 0.")
            return
        product = self._products.get(product_id)
        if product and product.update_stock(quantity):
            print(f"Restocked '{product.name}' by {quantity}. New stock: {product.stock}")
            self.save_data()
        else:
            print("Invalid product ID or stock update failed.")

    def view_all_orders(self):
        if not isinstance(self._current_user, Admin):
            print("Only admins can view all orders.")
            return
        if not self._orders:
            print("No orders yet.")
            return
        for order in sorted(self._orders.values(), key=lambda o: o.id):
            print(order)

    def browse_products(self):
        if not self._products:
            print("No products available.")
            return
        for product in sorted(self._products.values(), key=lambda p: p.id):
            print(product)

    def place_order(self, product_id, quantity):
        if not isinstance(self._current_user, Customer):
            print("Only customers can place orders.")
            return
        if quantity <= 0:
            print("Quantity must be greater than 0.")
            return
        product = self._products.get(product_id)
        if not product:
            print("Invalid product ID.")
            return
        if product.stock < quantity:
            print("Insufficient stock.")
            return
        if not product.update_stock(-quantity):
            print("Failed to update stock.")
            return

        order = Order(self._next_order_id, self._current_user, product, quantity)
        self._orders[self._next_order_id] = order
        self._current_user.add_order(order)
        print(f"Order placed: {order}")
        self._next_order_id += 1
        self.save_data()

    def view_order_history(self):
        if not isinstance(self._current_user, Customer):
            print("Only customers can view order history.")
            return
        history = self._current_user.view_history()
        if not history:
            print("No orders yet.")
            return
        for order in sorted(history, key=lambda o: o.id):
            print(order)


    def view_pending_orders(self):
        if not isinstance(self._current_user, Rider):
            print("Only riders can view pending orders.")
            return
        found = False
        for order in sorted(self._orders.values(), key=lambda o: o.id):
            if order.status == OrderStatus.PENDING:
                print(order)
                found = True
        if not found:
            print("No pending orders.")

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

    def update_order_status(self, order_id, status_text):
        if not isinstance(self._current_user, Rider):
            print("Only riders can update order status.")
            return
        order = self._orders.get(order_id)
        if not order:
            print("Invalid order ID.")
            return
        if order.rider != self._current_user:
            print("You are not assigned to this order.")
            return


        try:
            status_enum = OrderStatus[status_text.strip().upper()]
        except KeyError:
            print("Invalid status. Use one of: Accepted, Delivered.")
            return


        allowed_transitions = {
            OrderStatus.PENDING: {OrderStatus.ACCEPTED},
            OrderStatus.ACCEPTED: {OrderStatus.DELIVERED},
            OrderStatus.DELIVERED: set(),
        }
        if status_enum in allowed_transitions[order.status]:
            order.update_status(status_enum)
            print(f"Order {order_id} status updated to {status_enum.value}.")
            self.save_data()
        else:
            print(f"Invalid transition from {order.status.value} to {status_enum.value}.")


    def run(self):
        while True:
            if not self._current_user:
                print("""
                Main Menu:
                1. Register
                2. Login
                3. Exit
                """)
                choice = input("Enter choice: ").strip()
                try:
                    if choice == "1":
                        username = input("Username: ").strip()
                        password = input("Password: ").strip()
                        role = input("Role (Customer/Rider/Admin): ").strip()
                        self.register(username, password, role)
                    elif choice == "2":
                        username = input("Username: ").strip()
                        password = input("Password: ").strip()
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
                choice = input("Enter choice: ").strip()
                try:
                    if isinstance(self._current_user, Customer):
                        if choice == "1":
                            self.browse_products()
                        elif choice == "2":
                            product_id = int(input("Product ID: ").strip())
                            quantity = int(input("Quantity: ").strip())
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
                            order_id = int(input("Order ID: ").strip())
                            self.accept_order(order_id)
                        elif choice == "3":
                            order_id = int(input("Order ID: ").strip())
                            status = input("Status (Accepted/Delivered): ").strip()
                            self.update_order_status(order_id, status)
                        elif choice == "4":
                            self._current_user = None
                        else:
                            print("Invalid choice.")
                    elif isinstance(self._current_user, Admin):
                        if choice == "1":
                            name = input("Product Name: ").strip()
                            price = float(input("Price: ").strip())
                            stock = int(input("Stock: ").strip())
                            self.add_product(name, price, stock)
                        elif choice == "2":
                            product_id = int(input("Product ID: ").strip())
                            quantity = int(input("Quantity to restock: ").strip())
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
