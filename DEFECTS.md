# __List of defects identified:__

1. **``CheckoutService`` request ID and large order validation**
- **Where it occurs**: 
    The `checkout()` method in the `CheckoutService` performs some conditional statements which validates the request ID, and determines if the order is considered a large order.
- **What can go wrong**: 
    If the `request_id` is actually missing, the method only prints a message to the console, and continues the execution as if the `request_id` was provided. The `request_id` validation may be excluded entirely as long as the orders amount is `<= 1000`, since the method mistakenly only performs the validation whenever the amount is `> 1000`. 

    This makes the assumption that the `request_id` is independent of the order amount, and that the method should exit early without performing additional business logic whenever the `request_id` is not supplied.
- **How it was corrected**:
    The validation for the `checkout()` method is now structured like this:
    ```
    if not request_id:
        print('Missing request id')
        return False
    if len(cart.lines) == 0:
        return OrderResult(None, 'empty', 0)

    amount = cart.total()
    if amount > 1000:
        print('Large order')
    ```
    The `request_id` is now handled first, and exits early with `return False` to indicate to the validation has failed. The program also handles the large order case, but assumes that the method can continue processing the large order. This change makes the code more readable, and simplifies the conditional flow of the method.
2. **``StoreRepository`` vulnerable to SQL injection without parameterized queries**
- **Where it occurs**:
    Some methods in the ``StoreRepository`` class use direct string interpolation by directly inserting the query value into the query. This occurs in: ``get_product`` and ``get_saved_cart``. This creates a vulnerability for a SQL injection attack.
- **What can go wrong**:
    A malicious user to the system can manipulate the SQL query to perform destructive actions on the database by executing a SQL injection attack.
- **How it was corrected**:
    The updated methods now use parameterized queries:
    ```
    def get_product(self, sku):
        conn = self.connect()
        row = conn.execute("SELECT sku, name, price, stock FROM products WHERE sku = ?", (sku,)).fetchone()
        conn.close()
        return Product(*row) if row else None

    def get_saved_cart(self, user_id):
        conn = self.connect()
        rows = conn.execute("SELECT sku, quantity FROM saved_cart WHERE user_id = ?", (user_id,)).fetchall()
        conn.close()
        return rows
    ```
    This allows the values to be treated as literal strings in the SQL query, and prevents malicious SQL queries from being injected.
3. **``apply_discount`` can apply discount codes more than once**
- **Where it occurs**: The ``apply_discount()`` method in the ``ShoppingCart`` class can apply multiple discount codes. The method calls the ``total()`` method, which can return the discounted total. If the discount code has already been applied, this will further discount the shopping cart's total. This makes the assumption that only one discount code can be applied per cart.
- **What can go wrong**: A user may apply the same discount code more than once on their cart to gain a greater discount.
- **How it was corrected**: The ``apply_discount()`` method is now structured like this:
    ```
    def apply_discount(self, code):
    if self.discounted_total is not None:
        print('Coupon already applied to this cart')
        return False
    ```
    If the ``discounted_total`` is already set, it prints a message to the console, and exits the method early without perfoming the discount agan.

4. **``ShoppingCart`` negative quantity handling**
- **Where it occurs**: The ``ShoppingCart`` class allows the user to enter a negative quantity in the ``add_item()`` and ``remove_item()`` methods.
- **What can go wrong**: If the user supplies a negative quantity when adding existing an item, it decreases the quantity. When removing an item, applying a negative quantity increases the item's overall quantity. This creates unintended side effects in the program. 
- **How it was corrected**: The ``add_item()`` method now includes another validation condition:
    ```
    if quantity <= 0:
        print('Quantity must be positive')
        return False
    ```
    This enforces a positive quantity, and exits early to prevent unintended processing.
    The ``remove_item()`` also includes this validation:
    ```
    if quantity is not None and quantity <= 0:
        print('Quantity must be positive')
        return False
    ```
    This also ensures the quantity is positive (if it is provided), and returns early to prevent further processing

5. **``StoreRepository`` unused ``user_id`` parameter in ``list_orders()`` method**
- **Where it occurs**: The ``StoreRepository`` contains a ``list_orders()`` method that contains an unused ``user_id`` parameter. The SQL query excludes any filtering for the ``user_id``.
- **What can go wrong**: If a calling method expects ``list_orders()`` to return a list of orders for a single user, the repository will return a list of orders for all the users.
- **How it was corrected**: The ``list_orders()`` method is now strutured like this:
    ```
    def list_orders(self, user_id):
        conn = self.connect()
        rows = conn.execute('SELECT id, user_id, amount, status FROM orders WHERE user_id = ? ORDER BY id DESC', (user_id,)).fetchall()
        conn.close()
        return rows
    ```
    The method now includes a ``WHERE`` clause that filters against the ``user_id`` using prameterized queries to prevent SQL injection. This correctly returns the orders for a particular user.

6. **``CheckoutService`` updates stock before the payment is confirmed to be successful**
- **Where it occurs**: The ``checkout()`` method in the ``CheckoutService`` performs updates to the product's stock before confirming that the payment was successful.
- **What can go wrong**: This causes unintended side effects as the user can purposefully create declined payments in order to deplete the stock quantities.
- **How it was corrected**: The ``checkout()`` method is now structured like this:
    ```
    try:
        response = self.payment_gateway.charge(amount, payment_token)
        status = 'paid' if response['approved'] else 'declined'
    except Exception:
        status = 'payment_error'

    if status == 'paid':
        for line in cart.lines:
            self.repository.update_stock(line.sku, line.quantity)
    ```
    ``update_stock()`` is only called after the payment is successful. 

7. **``CheckoutService`` clears the cart's state on a failed payment**
- **Where it occurs**: The ``checkout()`` method in the ``CheckoutService`` clears the user's items in their cart and resets their total, even if the payment has failed.
- **What can go wrong**: If the user's payment is declined, the state of their cart is cleared and they cannot retry the payment without adding the items back into their cart.
- **How it was corrected**: The ``checkout()`` method has been modified:
    ```
    order_id = self.repository.save_order(cart.user_id, amount, status, request_id)

    if status == 'paid':
        cart.lines.clear()
        cart.discounted_total = None
    cart.save()
    return OrderResult(order_id, status, amount)
    ```
    Only if the payment is successful, the cart's items can be cleared and the total can be reset. In either case, the cart can be saved and the order result can be returned. This ensures that the user can retry their payment with their cart still saved.

8. **``CheckoutService`` prints the user's payment token to the console**
- **Where it occurs**: In the ``CheckoutService`` class, the ``checkout()`` method outputs the user's full payment token to the console.
- **What can go wrong**: This is security vulnerability, as any malicious users that gain access to the output of the program will be able to see the user's payment token, which can be used to perform unauthorized payments on the user's behalf.
- **How it was corrected**: The following line was removed from the ``checkout()`` method:
    ```
    print(f'Charging payment token: {payment_token}')
    ```
    This prevents the ``payment_token`` from being logged. If the program is required to log the user's payment token, the log message can be modified to only display the last 4 characters of the token.