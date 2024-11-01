class CustomException(Exception):
    def __init__(self):
        self.message = self.generate_message() + " Process not completed"
        super().__init__(self.message)

    def generate_message(self) -> str:
        pass


class InvalidQuantityException(CustomException):
    def __init__(self, quantity: int, item_name: str):
        self.quantity = quantity
        self.item_name = item_name
        super().__init__()

    def generate_message(self):
        return f'Invalid quantity detected of: [{self.quantity}] for item: [{self.item_name}].'


class InvalidPriceException(CustomException):
    def __init__(self, price: float, item_name: str):
        self.price = price
        self.item_name = item_name
        super().__init__()

    def generate_message(self):
        return f'Price of: {self.price} for {self.item_name} is invalid.'

class ItemNotFoundException(CustomException):
    def __init__(self, item_id: int):
        self.item_id = item_id
        super().__init__()

    def generate_message(self):
        return f'Item not found for item of id: {self.item_id}.'

class DuplicateItemException(CustomException):
    def __init__(self, item_name: str):
        self.item_name = item_name
        super().__init__()

    def generate_message(self):
        return f'Item name already exists for item: {self.item_name}.'

