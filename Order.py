from order_status import OrderStatus

class Order:
    def __init__(self, order_id, customer, product, quantity):
        self._order_id = order_id
        self._customer = customer
        self._product = product
        self._quantity = quantity
        self._status = OrderStatus.PENDING
        self._rider = None

    @property
    def status(self):
        return self._status

    def assign_rider(self, rider):
        self._rider = rider
        self._status = OrderStatus.ACCEPTED

    def update_status(self, status):
        self._status = status

    def __str__(self):
        return (f"Order ID: {self._order_id}, Product: {self._product._name}, "
                f"Quantity: {self._quantity}, Status: {self._status.value}")