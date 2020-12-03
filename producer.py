"""
This module represents the Producer.

Computer Systems Architecture Course
Assignment 1
March 2020
"""

from threading import Thread
from time import sleep


class Producer(Thread):
    """
    Class that represents a producer.
    """

    def __init__(self, products, marketplace, republish_wait_time, **kwargs):
        """
        Constructor.

        @type products: List()
        @param products: a list of products that the producer will produce

        @type marketplace: Marketplace
        @param marketplace: a reference to the marketplace

        @type republish_wait_time: Time
        @param republish_wait_time: the number of seconds that a producer must
        wait until the marketplace becomes available

        @type kwargs:
        @param kwargs: other arguments that are passed to the Thread's __init__()
        """
        super(Producer, self).__init__()
        self.products = products
        self.marketplace = marketplace
        self.republish_wait_time = republish_wait_time
        self.id_prod = marketplace.register_producer()
        self.daemon = kwargs["daemon"] #oprire odata cu thread-ul principal

    def run(self):
        while True:
            for id_product, quantity, sleep_time in self.products:
                while quantity > 0:
                    sleep(sleep_time)  #astept un timp inaintea producerii unui produs

                    bool_pub = self.marketplace.publish(
                        self.id_prod, id_product)

                    if bool_pub is True:
                        quantity -= 1
                    else:
                        sleep(self.republish_wait_time)
