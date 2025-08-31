
class Product:
    def __init__(self, id, name, price, stock):
        self._id = id
        self._name = name
        self._price = price
        self._stock = stock

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def price(self):
        return self._price

    @property
    def stock(self):
        return self._stock

    def update_stock(self, quantity):
        """Adds (or subtracts) quantity; prevents stock from going negative."""
        if self._stock + quantity < 0:
            return False
        self._stock += quantity
        return True

    def to_dict(self):
        return {"name": self._name, "price": self._price, "stock": self._stock}

    def __str__(self):
        return f"[{self._id}] {self._name} - ${self._price} | Stock: {self._stock}"
