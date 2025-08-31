class Product:
    def __init__(self, id, name, price, stock):  # Added id parameter
        self._id = id
        self._name = name
        self._price = price
        self._stock = stock

    @property
    def id(self):
        return self._id

    @property
    def stock(self):
        return self._stock

    def update_stock(self, quantity):  # Fixed typo "quatity"
        if self._stock + quantity >= 0:
            self._stock += quantity
            return True
        return False

    def __str__(self):
        return f"{self._name} (ID: {self._id}) - ${self._price}, Stock: {self._stock}"