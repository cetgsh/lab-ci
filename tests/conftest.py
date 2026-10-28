import pytest
from shop.cart import Cart


@pytest.fixture
def filled_cart() -> Cart:
    """Фікстура готового кошика з двома товарами."""
    cart = Cart()
    cart.add("book", price=200.0, qty=2)
    cart.add("pen", price=15.0, qty=4)
    return cart