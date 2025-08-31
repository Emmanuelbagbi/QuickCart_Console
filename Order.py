
from order_status import OrderStatus

class Order:
    def __init__(self, order_id, customer, product, quantity):
        self._order_id = order_id
        self._customer = customer
        self._product = product
        self._quantity = quantity
        self._status = OrderStatus.PENDING
        self._rider = None

    # ---- Properties ----
    @property
    def id(self):
        return self._order_id

    @property
    def customer(self):
        return self._customer

    @property
    def product(self):
        return self._product

    @property
    def quantity(self):
        return self._quantity

    @property
    def rider(self):
        return self._rider

    @property
    def status(self):
        return self._status

    def assign_rider(self, rider):
        self._rider = rider
        self._status = OrderStatus.ACCEPTED

    def update_status(self, status):
        if not isinstance(status, OrderStatus):
            raise ValueError("Invalid order status")
        self._status = status

    def to_dict(self):
        return {
            "id": self._order_id,
            "customer": self._customer.username if self._customer else None,
            "product_id": self._product.id if self._product else None,
            "quantity": self._quantity,
            "status": self._status.name,
            "rider": self._rider.username if self._rider else None,
        }

    @classmethod
    def from_dict(cls, data, users, products):
        """
        Rebuild an Order from dict + already-loaded users & products.
        Returns None if required references are missing.
        """
        customer = users.get(data.get("customer"))
        product = products.get(data.get("product_id"))
        if not customer or not product:
            return None

        order = cls(data["id"], customer, product, data["quantity"])
        # status
        try:
            order._status = OrderStatus[data["status"]]
        except Exception:
            order._status = OrderStatus.PENDING
        # rider
        rider_username = data.get("rider")
        if rider_username:
            order._rider = users.get(rider_username)
        return order

    def __str__(self):
        rider_name = self._rider.username if self._rider else "Unassigned"
        return (f"Order ID: {self._order_id} | Customer: {self._customer.username} | "
                f"Product: {self._product.name} | Qty: {self._quantity} | "
                f"Status: {self._status.value} | Rider: {rider_name}")
