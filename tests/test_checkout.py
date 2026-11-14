
from cart import ShoppingCart
from models import OrderResult


def test_checkout_invalid_details(get_repo, get_checkout, capsys):
    cart = ShoppingCart('demo-user', get_repo)
    assert get_checkout.checkout(cart, 'TEST_TOKEN', None) == False
    output = capsys.readouterr()
    assert output.out == "Missing request id\n"
    assert get_checkout.checkout(cart, 'TEST_TOKEN', '123') == OrderResult(None, 'empty', 0)

def test_checkout_large_order(get_repo, get_checkout, capsys):
    cart = ShoppingCart('demo-user', get_repo)
    cart.add_item('LAP-01', 2)
    assert get_checkout.checkout(cart, 'TEST_TOKEN', '123') == OrderResult(1, 'paid', 999.99*2)
    output = capsys.readouterr()
    assert output.out == "Large order\n"
    assert len(cart.lines) == 0
    assert get_repo.get_product('LAP-01').stock == 3

def test_failed_order(get_repo, get_failed_checkout):
    cart = ShoppingCart('demo-user', get_repo)
    cart.add_item('LAP-01', 1)
    assert get_failed_checkout.checkout(cart, 'TEST', '123') == OrderResult(1, 'declined', 999.99)
    assert len(cart.lines) == 1
    assert get_repo.get_product('LAP-01').stock == 5

def test_retry_failed_order(get_repo, get_failed_checkout, get_checkout, capsys):
    cart = ShoppingCart('demo-user', get_repo)
    cart.add_item('USB-01', 1)
    assert get_failed_checkout.checkout(cart, 'TEST', '123') == OrderResult(1, 'declined', 9.99)
    cart.add_item('LAP-01', 1)
    assert len(cart.lines) == 2
    assert get_checkout.checkout(cart, 'TEST_TOKEN', '123') == OrderResult(2, 'paid', 9.99+999.99)
    assert len(cart.lines) == 0
    output = capsys.readouterr()
    assert output.out == "Large order\n"
