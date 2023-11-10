from datetime import datetime
import pytest
from options_framework import option
from options_framework.option import Option
from options_framework.config import settings

def test_is_expired_returns_none_when_no_quote_data(ticker,expiration):
    test_option = Option(1, ticker, 100, expiration, settings.OptionType.CALL)

    assert test_option.is_expired() is None


@pytest.mark.xfail(raises=(TypeError,ValueError),reason="raises value or type error")
@pytest.mark.parametrize(
    "expiration_date_test, quote_date, expected_result",
    [
        (
            datetime.strptime("07-16-2021", "%m-%d-%Y"),
            datetime.strptime(
                "2021-07-01 09:45:00.000000", "%Y-%m-%d %H:%M:%S.%f"
            ),
            False,
        ),
        (
            datetime.strptime("06-30-2021", "%m-%d-%Y"),
            datetime.strptime(
                "2021-07-01 09:45:00.000000", "%Y-%m-%d %H:%M:%S.%f"
            ),
            True,
        ),
        (
            datetime.strptime("07-16-2021", "%m-%d-%Y"),
            datetime.strptime(
                "2021-07-16 09:45:00.000000", "%Y-%m-%d %H:%M:%S.%f"
            ),
            False,
        ),
        (
            datetime.strptime("07-16-2021", "%m-%d-%Y"),
            datetime.strptime(
                "2021-07-16 16:14:00.000000", "%Y-%m-%d %H:%M:%S.%f"
            ),
            False,
        ),
        (
            datetime.strptime("07-16-2021", "%m-%d-%Y"),
            datetime.strptime(
                "2021-07-16 16:15:00.000000", "%Y-%m-%d %H:%M:%S.%f"
            ),
            True,
        ),
        (
            datetime.strptime("07-16-2021", "%m-%d-%Y"),
            datetime.strptime("2021-07-16", "%Y-%m-%d"),
            False,
        ),
        (
            datetime.strptime("07-16-2021", "%m-%d-%Y"),
            datetime.strptime("2021-07-17", "%Y-%m-%d"),
            True,
        ),
    ],
)
def test_is_expired_returns_correct_result(call_option,ticker, put_option,    expiration_date_test, quote_date, expected_result):
    test_option = call_option

    # cheat to set data manually
    contract = option.OptionContract(
        1, ticker, expiration_date_test, 100.0, settings.OptionType.CALL
    )
    test_option._option_contract = contract

    _, spot_price, bid, ask, price = put_option
    quote = option.OptionQuote(quote_date, spot_price, bid, ask, price)
    test_option._option_quote = quote

    actual_result = test_option.is_expired()

    assert actual_result == expected_result
