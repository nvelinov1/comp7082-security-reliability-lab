from cart import ShoppingCart


def test_save_get_cart(get_repo):
    cart = ShoppingCart('demo-user', get_repo)
    cart.add_item('LAP-01', 1)
    cart.add_item('USB-01', 3)
    cart.add_item('MOU-01', 2)
    get_repo.save_cart('demo-user', cart.lines)
    saved_cart = get_repo.get_saved_cart('demo-user')
    assert len(saved_cart) == 3
    for name, quantity in saved_cart:
        if name == 'LAP-01':
            assert quantity == 1
        if name == 'USB-01':
            assert quantity == 3
        if name == 'MOU-01':
            assert quantity == 2

def test_list_user_orders(get_repo, get_checkout, get_failed_checkout):
    cart = ShoppingCart('demo-user', get_repo)
    cart.add_item('USB-01', 3)
    get_failed_checkout.checkout(cart, 'TEST', '123')
    cart.add_item('LAP-01', 1)
    get_checkout.checkout(cart, 'TEST_TOKEN', '123')
    orders = get_repo.list_orders('demo-user')
    assert len(orders) == 2
        