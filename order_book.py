class OrderBook:
    def __init__(self):
        self.orders = {}
        self.exception_queue = []
        self.ticker_prices = {}

    def process_order(self, order_stream):
        order = order_stream.split('|')
        if order[2] == 'a':
            self.add(order)
        elif order[2] == 'u':
            self.amend(order)
        elif order[2] == 'c':
            self.cancel(order)

    def add(self, order_list):
        if len(order_list) == 7:
            self.orders[order_list[1]] = {'timestamp': int(order_list[0]),
                                          'id': order_list[1],
                                          'action': order_list[2],
                                          'ticker': order_list[3],
                                          'side': order_list[4],
                                          'price': float(order_list[5]),
                                          'size': int(order_list[6])}
            self.update_ticker_prices(order_list[3], order_list[4], float(order_list[5]))
        else:
            self.exception_queue.append(['Invalid order string'] + order_list)

    def amend(self, order_list):
        try:
            self.orders[order_list[1]]['timestamp'] = int(order_list[0])
            self.orders[order_list[1]]['action'] = order_list[2]
            self.orders[order_list[1]]['size'] = int(order_list[3])
        except KeyError:
            self.exception_queue.append(['Amend for non existent order'] + order_list)

    def cancel(self, order_list):
        try:
            self.orders[order_list[1]]['timestamp'] = int(order_list[0])
            self.orders[order_list[1]]['action'] = order_list[2]
        except KeyError:
            self.exception_queue.append(['Cancel for non existent order'] + order_list)

    def update_ticker_prices(self, ticker, side, price):
        '''Keeps track of the best buy or sell price seen in this ordernook for a given ticker.
            Stored in a dictionary for fast retrieval '''
        try:
            if self.ticker_prices[ticker + side]:
                if side == 'B':
                    if price < self.ticker_prices[ticker + side]:
                        self.ticker_prices[ticker + side] = price
                elif side == 'S':
                    if price > self.ticker_prices[ticker + side]:
                        self.ticker_prices[ticker + side] = price
        except KeyError:
            self.ticker_prices[ticker + side] = price

    def best_bid_and_ask(self, ticker):
        '''If no bid or ask price for a given ticker set the price to 0'''
        try:
            best_bid = self.ticker_prices[ticker + 'B']
        except KeyError:
            best_bid = 0
        try:
            best_ask = self.ticker_prices[ticker + 'S']
        except KeyError:
            best_ask = 0

        return best_bid, best_ask
