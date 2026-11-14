"""Two simple smoke tests"""
from cart import ShoppingCart


def test_seed_product(get_repo):
    assert get_repo.get_product('MOU-01').name == 'Wireless mouse'


def test_cart_adds_valid_item(get_repo):
    cart = ShoppingCart('student', get_repo)
    assert cart.add_item('USB-01', 2)
    assert len(cart.lines) == 1
