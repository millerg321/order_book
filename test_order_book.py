import pytest
from order_book import OrderBook


def test_add_order():
    order_stream = '1568390243|abbb11|a|AAPL|B|209.00000|100'
    book = OrderBook()
    book.process_order(order_stream)

    assert book.orders['abbb11'] == {'timestamp': 1568390243, 'id': 'abbb11', 'action': 'a',
                                     'ticker': 'AAPL', 'side': 'B', 'price': 209, 'size': 100}


def test_add_order_missing_details():
    order_stream = '1568390243|abbb11|a|AAPL|B|209.00000'
    book = OrderBook()
    book.process_order(order_stream)

    assert book.exception_queue == [['Invalid order string', '1568390243', 'abbb11', 'a', 'AAPL', 'B', '209.00000']]
    with pytest.raises(KeyError):
        book.orders['abbb11']


def test_update_order():
    order_stream1 = '1568390243|abbb11|a|AAPL|B|209.00000|100'
    order_stream2 = '1568390244|abbb11|u|101'
    book = OrderBook()
    book.process_order(order_stream1)
    book.process_order(order_stream2)

    assert book.orders['abbb11'] == {'timestamp': 1568390244, 'id': 'abbb11', 'action': 'u',
                                     'ticker': 'AAPL', 'side': 'B', 'price': 209, 'size': 101}


def test_amend_for_invalid_order():
    order_stream1 = '1568390243|abbb11|a|AAPL|B|209.00000|100'
    order_stream2 = '1568390244|ZZZZZZ|u|101'
    book = OrderBook()
    book.process_order(order_stream1)
    book.process_order(order_stream2)

    assert book.orders['abbb11'] == {'timestamp': 1568390243, 'id': 'abbb11', 'action': 'a',
                                     'ticker': 'AAPL', 'side': 'B', 'price': 209, 'size': 100}
    assert book.exception_queue == [['Amend for non existent order', '1568390244', 'ZZZZZZ', 'u', '101']]


def test_cancel_order():
    order_stream1 = '1568390243|abbb11|a|AAPL|B|209.00000|100'
    order_stream2 = '1568390244|abbb11|u|101'
    order_stream3 = '1568390245|abbb11|c'
    book = OrderBook()
    book.process_order(order_stream1)
    book.process_order(order_stream2)
    book.process_order(order_stream3)

    assert book.orders['abbb11'] == {'timestamp': 1568390245, 'id': 'abbb11', 'action': 'c',
                                     'ticker': 'AAPL', 'side': 'B', 'price': 209, 'size': 101}


def test_cancel_for_invalid_order():
    order_stream1 = '1568390243|abbb11|a|AAPL|B|209.00000|100'
    order_stream2 = '1568390244|ZZZZZZ|c'
    book = OrderBook()
    book.process_order(order_stream1)
    book.process_order(order_stream2)

    assert book.orders['abbb11'] == {'timestamp': 1568390243, 'id': 'abbb11', 'action': 'a',
                                     'ticker': 'AAPL', 'side': 'B', 'price': 209, 'size': 100}
    assert book.exception_queue == [['Cancel for non existent order', '1568390244', 'ZZZZZZ', 'c']]


def test_get_best_bid_and_ask_prices():
    book = OrderBook()
    order_stream1 = '1568390201|abbb11|a|AAPL|B|209.00000|100'
    order_stream2 = '1568390202|abbb12|a|AAPL|S|210.00000|10'
    order_stream3 = '1568390202|abbb13|a|AAPL|B|220.00000|1000'
    order_stream4 = '1568390202|abbb14|a|AAPL|S|230.00000|500'
    book.process_order(order_stream1)
    book.process_order(order_stream2)
    book.process_order(order_stream3)
    book.process_order(order_stream4)

    assert book.best_bid_and_ask('AAPL') == (209, 230)


def test_get_best_bid_price_with_no_ask():
    book = OrderBook()
    order_stream1 = '1568390201|abbb11|a|AAPL|B|209.00000|100'
    order_stream2 = '1568390202|abbb13|a|AAPL|B|220.00000|1000'
    book.process_order(order_stream1)
    book.process_order(order_stream2)

    assert book.best_bid_and_ask('AAPL') == (209, 0)


def test_get_best_bid_price_with_no_ask():
    book = OrderBook()
    order_stream1 = '1568390201|abbb11|a|AAPL|S|209.00000|100'
    order_stream2 = '1568390202|abbb13|a|AAPL|S|220.00000|1000'
    book.process_order(order_stream1)
    book.process_order(order_stream2)

    assert book.best_bid_and_ask('AAPL') == (0, 220)


def test_get_bid_and_ask_for_missing_ticker():
    book = OrderBook()
    order_stream1 = '1568390201|abbb11|a|AAPL|S|209.00000|100'
    order_stream2 = '1568390202|abbb13|a|AAPL|S|220.00000|1000'
    book.process_order(order_stream1)
    book.process_order(order_stream2)

    assert book.best_bid_and_ask('ZZZZ') == (0, 0)
