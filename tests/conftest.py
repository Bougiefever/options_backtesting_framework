from datetime import datetime
from collections import namedtuple
import pytest
from options_framework.config import settings
from options_framework.option import Option

Quote = namedtuple("Quote", "quote_date spot_price bid ask price")


@pytest.fixture
def expiration():
    """Fixture for expiration date"""
    return datetime.strptime("07-16-2021", "%m-%d-%Y")


@pytest.fixture
def quote_date():
    """Fixture for quote date"""
    return datetime.strptime("2021-07-01 09:45:00.000000", "%Y-%m-%d %H:%M:%S.%f")


@pytest.fixture
def update_quote_date():
    """Fixture for update quote date"""
    return datetime.strptime("2021-07-02 09:45:00.000000", "%Y-%m-%d %H:%M:%S.%f")


@pytest.fixture
def update_quote_date2():
    """Fixture for second update quote date"""
    return datetime.strptime("2021-07-02 14:31:00.000000", "%Y-%m-%d %H:%M:%S.%f")


@pytest.fixture
def update_quote_date3():
    """Fixture for third update quote date"""
    return datetime.strptime("2021-07-16 11:31:00.000000", "%Y-%m-%d %H:%M:%S.%f")


@pytest.fixture
def at_expiration_quote_date():
    """Fixture for at expiration quote date"""
    return datetime.strptime("2021-07-16 16:15:00.000000", "%Y-%m-%d %H:%M:%S.%f")


@pytest.fixture
def standard_fee():
    """Fixture for standard fee"""
    return 0.50


@pytest.fixture
def ticker():
    """Fixture for ticker"""
    return "XYZ"


@pytest.fixture
def call_option(quote_date,ticker,expiration):
    """Fixture for call option"""
    _id, strike, spot_price, bid, ask, price = (1, 100.0, 90.0, 1.0, 2.0, 1.5)
    return Option(
        _id,
        ticker,
        strike,
        expiration,
        settings.OptionType.CALL,
        quote_date=quote_date,
        spot_price=spot_price,
        bid=bid,
        ask=ask,
        price=price,
    )


@pytest.fixture
def call_option_update_values_1(update_quote_date):
    """Fixture for first set of call option update values"""
    quote = Quote(
        quote_date=update_quote_date,
        spot_price=110.0,
        bid=9.50,
        ask=10.5,
        price=10.00,
    )  # ITM
    return quote.quote_date, quote.spot_price, quote.bid, quote.ask, quote.price


@pytest.fixture
def call_option_update_values_2(update_quote_date2):
    """Fixture for second set of call option update values"""
    quote = Quote(
        quote_date=update_quote_date2,
        spot_price=105.0,
        bid=4.50,
        ask=5.5,
        price=5.00,
    )  # ITM
    return quote.quote_date, quote.spot_price, quote.bid, quote.ask, quote.price


@pytest.fixture
def call_option_update_values_3(update_quote_date3):
    """Fixture for third set of call option update values"""
    quote = Quote(
        quote_date=update_quote_date3,
        spot_price=90.0,
        bid=0,
        ask=0.05,
        price=0.03,
    )  # OTM
    return quote.quote_date, quote.spot_price, quote.bid, quote.ask, quote.price


@pytest.fixture
def call_option_extended_properties(ticker,expiration,quote_date):
    """Fixture for call option with extended properties"""
    _id = 1
    strike = 100
    spot_price, bid, ask, price = (110.0, 1.0, 2.0, 1.5)
    delta, gamma, theta, vega, open_interest, rho, iv = (
        0.3459,
        -0.1234,
        0.0485,
        0.0935,
        100,
        0.132,
        0.3301,
    )
    return Option(
        _id,
        ticker,
        strike,
        expiration,
        settings.OptionType.CALL,
        quote_date=quote_date,
        spot_price=spot_price,
        bid=bid,
        ask=ask,
        price=price,
        delta=delta,
        gamma=gamma,
        theta=theta,
        vega=vega,
        rho=rho,
        implied_volatility=iv,
        open_interest=open_interest,
    )


@pytest.fixture
def put_option(ticker,expiration,quote_date):
    """Fixture for put option"""
    _id, strike, spot_price, bid, ask, price = (1, 100.0, 105.0, 1.0, 2.0, 1.5)
    return Option(
        _id,
        ticker,
        strike,
        expiration,
        settings.OptionType.PUT,
        quote_date=quote_date,
        spot_price=spot_price,
        bid=bid,
        ask=ask,
        price=price,
    )


@pytest.fixture
def put_option_update_values_1(update_quote_date):
    """Fixture for first set of put option update values"""
    quote = Quote(
        quote_date=update_quote_date,
        spot_price=90.0,
        bid=9.50,
        ask=10.5,
        price=10.00,
    )  # ITM
    return quote.quote_date, quote.spot_price, quote.bid, quote.ask, quote.price


@pytest.fixture
def put_option_update_values_2(update_quote_date2):
    """Fixture for second set of put option update values"""
    quote = Quote(
        quote_date=update_quote_date2,
        spot_price=95.0,
        bid=4.50,
        ask=5.5,
        price=5.00,
    )  # ITM
    return quote.quote_date, quote.spot_price, quote.bid, quote.ask, quote.price


@pytest.fixture
def put_option_update_values_3(update_quote_date3):
    """Fixture for third set of put option update values"""
    quote = Quote(
        quote_date=update_quote_date3,
        spot_price=110.0,
        bid=0,
        ask=0.05,
        price=0.03,
    )  # OTM
    return quote.quote_date, quote.spot_price, quote.bid, quote.ask, quote.price


@pytest.fixture
def put_option_with_extended_properties(ticker,expiration,quote_date):
    """Fixture for put option with extended properties"""
    _id = 1
    strike = 100
    spot_price, bid, ask, price = (105, 1.0, 2.0, 1.5)
    delta, gamma, theta, vega, open_interest, rho, iv = (
        -0.4492,
        -0.1045,
        0.0412,
        0.1143,
        900,
        0.0282,
        0.3347,
    )
    test_option = Option(
        _id,
        ticker,
        strike,
        expiration,
        settings.OptionType.PUT,
        quote_date=quote_date,
        spot_price=spot_price,
        bid=bid,
        ask=ask,
        price=price,
        delta=delta,
        gamma=gamma,
        theta=theta,
        vega=vega,
        rho=rho,
        implied_volatility=iv,
        open_interest=open_interest,
    )
    return test_option
