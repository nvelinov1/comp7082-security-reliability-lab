
from cart import ShoppingCart


def test_add_multiple_items(get_repo):
    cart = ShoppingCart('demo-user', get_repo)
    assert cart.add_item('LAP-01', 2) == True
    assert cart.add_item('USB-01', 1) == True
    assert cart.add_item('LAP-01', 3) == True
    assert cart.lines[0].quantity == 5
    assert len(cart.lines) == 2
    assert cart.subtotal() == (999.99*5) + 9.99

def test_invalid_add(get_repo, capsys):
    cart = ShoppingCart('demo-user', get_repo)
    assert cart.add_item('TEST-ITEM', 3) == False
    output = capsys.readouterr()
    assert output.out == "Unknown product\n"
    assert cart.add_item('MOU-01', 1000) == False
    output = capsys.readouterr()
    assert output.out == "Not enough stock\n"
    assert cart.add_item('LAP-01', -2) == False
    output = capsys.readouterr()
    assert output.out == "Quantity must be positive\n" 

def test_add_and_remove(get_repo):
    cart = ShoppingCart('demo-user', get_repo)
    cart.add_item('MOU-01', 5)
    cart.add_item('LAP-01', 5)
    cart.add_item('USB-01', 6)
    assert cart.remove_item('MOU-01', 3) == True
    assert cart.lines[0].quantity == 2
    assert cart.remove_item('LAP-01', 5) == True
    assert len(cart.lines) == 2

def test_invalid_remove(get_repo, capsys):
    cart = ShoppingCart('demo-user', get_repo)
    assert cart.remove_item('TEST-ITEM', 5) == False
    output = capsys.readouterr()
    assert output.out == "Item not found\n"
    assert cart.remove_item('MOU-01', -3) == False
    output = capsys.readouterr()
    assert output.out == "Quantity must be positive\n"

def test_apply_discount(get_repo):
    cart = ShoppingCart('demo-user', get_repo)
    cart.add_item('USB-01', 3)
    cart.add_item('LAP-01', 2)
    before_amount = (9.99*3) + (999.99*2)
    assert cart.total() == before_amount
    assert cart.apply_discount('STUDENT20') == True
    assert cart.total() == before_amount * 0.8

def test_apply_multiple_discounts(get_repo, capsys):
    cart = ShoppingCart('demo-user', get_repo)
    cart.add_item('USB-01', 1)
    cart.add_item('MOU-01', 2)
    before_amount = (9.99*1) + (29.95*2)
    assert cart.total() == before_amount
    assert cart.apply_discount('WELCOME10') == True
    assert cart.total() == before_amount * 0.9
    assert cart.apply_discount('STUDENT20') == False
    assert cart.total() == before_amount * 0.9
    output = capsys.readouterr()
    assert output.out == "Coupon already applied to this cart\n"