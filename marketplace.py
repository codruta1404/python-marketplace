"""
This module represents the Marketplace.

Computer Systems Architecture Course
Assignment 1
March 2020
"""
from threading import Lock


class Marketplace:
    """
    Class that represents the Marketplace. It's the central part of the implementation.
    The producers and consumers use its methods concurrently.
    """

    def __init__(self, queue_size_per_producer):
        """
        Constructor

        :type queue_size_per_producer: Int
        :param queue_size_per_producer: the maximum size of a queue associated with each producer
        """
        self.queue_size_per_producer = queue_size_per_producer

        self.id_prod_lock = Lock()
        self.id_prod = 0
        self.cart_id_lock = Lock()
        self.cart_id = 0

        # dictionar (producator, contor nr produse)
        self.producer_dict = {}
        self.producer_dict_lock = Lock()

        # dictionar (product_id, [quantity, producer_id])
        self.products_dict = {}
        self.products_dict_lock = Lock()

        # dictionar de dictionare->cart_dict[cart_id] = {product_id : quantity}
        self.cart_dict = {}

    def register_producer(self):
        """
        Returns an id for the producer that calls this.
        """
        with self.id_prod_lock:  # fac lock pe id_prod
            self.id_prod += 1
            self.producer_dict[self.id_prod] = 0  # producatorul nu va avea niciun produs

            return self.id_prod

    def publish(self, producer_id, product):
        """
        Adds the product provided by the producer to the marketplace

        :type producer_id: String
        :param producer_id: producer id

        :type product: Product
        :param product: the Product that will be published in the Marketplace

        :returns True or False. If the caller receives False, it should wait and then try again.
        """
        # public produse cat timp nu am ajuns la val max
        if self.producer_dict[producer_id] != self.queue_size_per_producer:

            # pun lock pe produse pentru a nu modifica si prod si cons in acelasi timp
            with self.products_dict_lock:
                if product in self.products_dict:
                    # daca produsul exista, ii cresc cant
                    self.products_dict[product][0] += 1
                else:
                    self.products_dict[product] = [None] * 2
                    # produsul nu exista, il adaug
                    self.products_dict[product][0] = 1
                self.products_dict[product][1] = producer_id

            # la variabila de publicare a producatorului pot actiona mai multi prod/ cons
            with self.producer_dict_lock:
                self.producer_dict[producer_id] += 1
            return True

        return False

    def new_cart(self):
        """
        Creates a new cart for the consumer

        :returns an int representing the cart_id
        """
        with self.cart_id_lock:
            self.cart_id += 1
            self.cart_dict[self.cart_id] = {}  # in cos initial nu am nimic

            return self.cart_id

    def add_to_cart(self, cart_id, product):
        """
        Adds a product to the given cart. The method returns

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to add to cart

        :returns True or False. If the caller receives False, it should wait and then try again
        """
        with self.products_dict_lock:
            if product not in self.products_dict:  # daca prod nu este in market
                return False
            # daca prod este in market, dar are quantity=0
            if self.products_dict[product][0] == 0:
                return False
            self.products_dict[product][0] -= 1  # scad cantitatea din market

            producer_id = self.products_dict[product][1]

        with self.producer_dict_lock:  # mai multi cons cumpara de la un prod
            # scad cant din contorul producatorului
            self.producer_dict[producer_id] -= 1

        # daca am prod in cos ii cresc cantitatea
        if product in self.cart_dict[cart_id]:
            self.cart_dict[cart_id][product] += 1
        else:
            # daca nu am prod in cos, il adaug
            self.cart_dict[cart_id][product] = 1
        return True

    def remove_from_cart(self, cart_id, product):
        """
        Removes a product from cart.

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to remove from cart
        """

        if product in self.cart_dict[cart_id]:
            self.cart_dict[cart_id][product] -= 1
            # daca cant e 0, sterg produsul
            if self.cart_dict[cart_id][product] == 0:
                del self.cart_dict[cart_id][product]

            with self.products_dict_lock:
                self.products_dict[product][0] += 1
                producer_id = self.products_dict[product][1]

            # add cant la contorul producatorului
            with self.producer_dict_lock:
                self.producer_dict[producer_id] += 1

    def place_order(self, cart_id):  # nu pun lock deoarece e per cons
        """
        Return a list with all the products in the cart.

        :type cart_id: Int
        :param cart_id: id cart
        """
        order = []

        for product, quantity in self.cart_dict[cart_id].items():
            while quantity > 0:
                order.append(product)
                quantity -= 1

        order.reverse()

        return order
