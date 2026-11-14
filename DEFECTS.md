# __List of defects identified:__

1. ``CheckoutService`` missed request ID and large order validation
2. ``StoreRepository`` vulnerable to SQL injection without parameterized queries
3. ``apply_discount`` can apply discount codes twice
4. ``ShoppingCart`` negative quantity handling
5. ``StoreRepository`` unused ``user_id`` parameter in ``list_orders()`` method
6. ``CheckoutService`` updates stock before the payment is confirmed to be successful
7. ``CheckoutService`` clears the cart's state on a failed payment
8. ``CheckoutService`` prints the user's payment token to the console