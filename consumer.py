"""
This module represents the Consumer.

Computer Systems Architecture Course
Assignment 1
March 2020
"""

from threading import Thread
from time import sleep


class Consumer(Thread):
    """
    Class that represents a consumer.
    """

    def __init__(self, carts, marketplace, retry_wait_time, **kwargs):
        """
        Constructor.

        :type carts: List
        :param carts: a list of add and remove operations

        :type marketplace: Marketplace
        :param marketplace: a reference to the marketplace

        :type retry_wait_time: Time
        :param retry_wait_time: the number of seconds that a producer must wait
        until the Marketplace becomes available

        :type kwargs:
        :param kwargs: other arguments that are passed to the Thread's __init__()
        """
        super(Consumer, self).__init__()
        self.carts = carts
        self.marketplace = marketplace
        self.retry_wait_time = retry_wait_time
        self.name = kwargs["name"]

    def run(self):
        for cart in self.carts:
            cart_id = self.marketplace.new_cart()

            for cart_op in cart:
                if cart_op['type'] == 'add':
                    while cart_op['quantity'] > 0:
                        bool_add = self.marketplace.add_to_cart(
                            cart_id, cart_op['product'])

                        if bool_add is False:
                            sleep(self.retry_wait_time)
                        else:
                            cart_op['quantity'] -= 1
                elif cart_op['type'] == 'remove':
                    while cart_op['quantity'] > 0:
                        self.marketplace.remove_from_cart(
                            cart_id, cart_op['product'])
                        cart_op['quantity'] -= 1

            products = self.marketplace.place_order(cart_id)

            for product in products:
                print(self.name + " bought " + str(product))
