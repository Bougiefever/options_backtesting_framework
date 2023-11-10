from datetime import datetime
import pytest
from options_framework.option import Option
from options_framework.config import settings

# Test initialization
def test_option_init_with_only_option_contract_parameters(ticker,expiration):
    _id = 1
    strike = 100
    test_option = Option(_id, ticker, strike, expiration, settings.OptionType.CALL)

    option_contract = test_option.option_contract
    option_quote = test_option.option_quote
    greeks = test_option.greeks

    assert option_contract.option_id == _id
    assert option_contract.symbol == ticker
    assert option_contract.strike == strike
    assert option_contract.expiration == expiration

    assert option_quote is None
    assert test_option.extended_properties is None
    assert greeks is None
    assert test_option.quantity == 0


def test_option_init_with_quote_data(ticker,expiration,quote_date):
    _id = 1
    strike = 100
    spot_price, bid, ask, price = (95, 1.0, 2.0, 1.5)
    test_option = Option(
        _id,
        ticker,
        strike,
        expiration,
        settings.OptionType.CALL,
        quote_date,
        spot_price,
        bid,
        ask,
        price,
    )

    option_quote = test_option.option_quote

    assert option_quote.bid == bid
    assert option_quote.ask == ask
    assert option_quote.price == price
    assert option_quote.quote_date == quote_date


def test_option_init_with_extended_properties(ticker,expiration,quote_date):
    spot_price, bid, ask, price, delta, gamma, theta, vega, open_interest, rho, iv = (
        95,
        1.0,
        2.0,
        1.5,
        0.3459,
        -0.1234,
        0.0485,
        0.0935,
        100,
        0.132,
        0.3301,
    )
    _id = 1
    strike = 100
    fee = 0.5

    test_option = Option(
        _id,
        ticker,
        strike,
        expiration,
        settings.OptionType.CALL,
        quote_date,
        spot_price,
        bid,
        ask,
        price,
        open_interest=open_interest,
        implied_volatility=iv,
        delta=delta,
        gamma=gamma,
        theta=theta,
        vega=vega,
        rho=rho,
        fee=fee,
    )

    option_contract = test_option.option_contract
    option_quote = test_option.option_quote
    greeks = test_option.greeks
    extended_properties = test_option.extended_properties

    assert option_contract.option_id == _id
    assert option_contract.symbol == ticker
    assert option_contract.strike == strike
    assert option_contract.expiration == expiration
    assert option_quote.bid == bid
    assert option_quote.ask == ask
    assert option_quote.price == price
    assert option_quote.quote_date == quote_date

    assert greeks.delta == delta
    assert greeks.gamma == gamma
    assert greeks.theta == theta
    assert greeks.vega == vega
    assert greeks.rho == rho

    assert extended_properties.implied_volatility == iv
    assert extended_properties.open_interest == open_interest

    assert test_option._fee == fee


@pytest.mark.xfail(reason="Option does not have a 'user_defined' member")
def test_option_init_with_user_defined_attributes(ticker,expiration,quote_date):
    _id = 1
    strike = 100
    test_value = "test value"

    spot_price, bid, ask, price, delta, gamma, theta, vega, open_interest, rho, iv = (
        95,
        1.0,
        2.0,
        1.5,
        0.3459,
        -0.1234,
        0.0485,
        0.0935,
        100,
        0.132,
        0.3301,
    )

    test_option = Option(
        _id,
        ticker,
        strike,
        expiration,
        settings.OptionType.CALL,
        quote_date,
        spot_price,
        bid,
        ask,
        price,
        open_interest=open_interest,
        iv=iv,
        delta=delta,
        gamma=gamma,
        theta=theta,
        vega=vega,
        rho=rho,
        user_defined=test_value,
    )

    # 'Option' has no 'user_defined' member
    # assert test_option.user_defined == test_value
    assert False


def test_option_init_raises_exception_if_missing_required_fields(ticker,expiration):
    # missing id
    _id = None
    with pytest.raises(ValueError, match="option_id is required"):
        Option(
            option_id=_id,
            symbol=ticker,
            strike=100,
            expiration=expiration,
            option_type=settings.OptionType.CALL,
        )

    # missing ticker symbol
    _id = 1
    none_symbol = None
    with pytest.raises(ValueError, match="symbol is required"):
        Option(
            option_id=_id,
            symbol=none_symbol,
            strike=100,
            expiration=expiration,
            option_type=settings.OptionType.CALL,
        )

    # missing strike
    none_strike = None
    with pytest.raises(ValueError, match="strike is required"):
        Option(
            option_id=_id,
            symbol=ticker,
            strike=none_strike,
            expiration=expiration,
            option_type=settings.OptionType.CALL,
        )

    # missing expiration
    none_expiration = None
    with pytest.raises(ValueError, match="expiration is required"):
        Option(
            option_id=_id,
            symbol=ticker,
            strike=100,
            expiration=none_expiration,
            option_type=settings.OptionType.CALL,
        )

    # missing option type
    none_option_type = None
    with pytest.raises(ValueError, match="option_type is required"):
        Option(
            option_id=_id,
            symbol=ticker,
            strike=100,
            expiration=expiration,
            option_type=none_option_type,
        )


def test_option_init_raises_exception_if_quote_date_is_greater_than_expiration(ticker,expiration):
    bad_open_date = datetime.strptime(
        "2021-07-17 09:45:00.000000", "%Y-%m-%d %H:%M:%S.%f"
    )
    strike = 100
    spot_price, bid, ask, price = (95, 1.0, 2.0, 1.5)
    with pytest.raises(
        Exception,
        match="Cannot create an option with a quote date past its expiration date",
    ):
        Option(
            id,
            ticker,
            strike,
            expiration,
            settings.OptionType.CALL,
            quote_date=bad_open_date,
            spot_price=spot_price,
            bid=bid,
            ask=ask,
            price=price,
        )
