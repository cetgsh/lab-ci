from unittest.mock import Mock

import pytest

from shop.cart import Cart


# 1. Тест додавання товару
def test_add_item() -> None:
    cart = Cart()
    cart.add("apple", price=10.0, qty=3)
    assert cart.items_count() == 3


# 2. Тест додавання існуючого товару (збільшення кількості)
def test_add_existing_item_increases_qty(filled_cart: Cart) -> None:
    filled_cart.add("book", price=200.0, qty=1)
    assert filled_cart.items_count() == 7


# 3. Підказка з методички: повторне додавання товару з іншою ціною зберігає початкову ціну
def test_add_existing_item_with_different_price_keeps_original_price(filled_cart: Cart) -> None:
    filled_cart.add("book", price=300.0, qty=1)
    # Початкова ціна 200.0 за 3 шт = 600.0 + 4 ручки по 15.0 (60.0) = 660.0
    assert filled_cart.total() == 660.0


# 4-7. Параметризований тест знижки з граничними значеннями (0, 10, 50, 100%)
@pytest.mark.parametrize(
    ("discount", "expected_total"),
    [
        (0, 460.0),  # Граничне значення: min discount
        (10, 414.0),
        (50, 230.0),
        (100, 0.0),  # Граничне значення: max discount
    ],
)
def test_total_with_discounts(filled_cart: Cart, discount: float, expected_total: float) -> None:
    assert filled_cart.total(discount_percent=discount) == expected_total


# 8. Тест видалення товару
def test_remove_item(filled_cart: Cart) -> None:
    filled_cart.remove("pen")
    assert filled_cart.items_count() == 2


# 9. Виняток: видалення відсутнього товару
def test_remove_non_existent_item_raises() -> None:
    cart = Cart()
    with pytest.raises(KeyError):
        cart.remove("laptop")


# 10. Виняток: від'ємна ціна
def test_add_negative_price_raises() -> None:
    cart = Cart()
    with pytest.raises(ValueError, match="price must be non-negative"):
        cart.add("item", price=-10.0)


# 11. Виняток: некоректна кількість (<=0)
def test_add_invalid_qty_raises() -> None:
    cart = Cart()
    with pytest.raises(ValueError, match="qty must be positive"):
        cart.add("item", price=10.0, qty=0)


# 12-13. Виняток: некоректна знижка (<0 або >100)
@pytest.mark.parametrize("invalid_discount", [-1.0, 101.0])
def test_invalid_discount_raises(filled_cart: Cart, invalid_discount: float) -> None:
    with pytest.raises(ValueError, match="discount_percent must be in \\[0, 100\\]"):
        filled_cart.total(discount_percent=invalid_discount)


# 14. Тест методу total_in з тестовим дублером Mock (без мережевих запитів)
def test_total_in_currency_with_mock(filled_cart: Cart) -> None:
    rates_mock = Mock()
    rates_mock.get_rate.return_value = 40.0  # 1 USD = 40 UAH

    total_usd = filled_cart.total_in("USD", rates_mock)
    assert total_usd == 11.5
    rates_mock.get_rate.assert_called_once_with("USD")


# 15. Виняток: некоректний курс (<=0)
def test_total_in_invalid_rate_raises(filled_cart: Cart) -> None:
    rates_mock = Mock()
    rates_mock.get_rate.return_value = 0.0
    with pytest.raises(ValueError, match="rate must be positive"):
        filled_cart.total_in("USD", rates_mock)


# --- TDD (Test-Driven Development) для нового методу most_expensive() ---


# 16. Перевірка найдорожчого товару (для порожнього кошика й заповненого)
def test_most_expensive_empty_cart() -> None:
    cart = Cart()
    assert cart.most_expensive() is None


def test_most_expensive_item(filled_cart: Cart) -> None:
    item = filled_cart.most_expensive()
    assert item is not None
    assert item.name == "book"
    assert item.price == 200.0
