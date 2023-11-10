import pytest
from options_framework.config import settings


def test_get_total_profit_loss_raises_exception_if_not_traded(call_option):
    test_option = call_option

    with pytest.raises(Exception, match="No trade has been opened."):
        test_option.get_total_profit_loss()


@pytest.mark.parametrize(
    "option_type, qty, price, expected_value",
    [
        (settings.OptionType.CALL, 10, 2.0, 500.0),
        (settings.OptionType.CALL, -10, 2.0, -500.0),
        (settings.OptionType.PUT, 10, 2.0, 500.0),
        (settings.OptionType.PUT, -10, 2.0, -500.0),
    ],
)
def test_get_total_profit_loss_returns_unrealized_when_no_contracts_are_closed(
    call_option,
    put_option,
    call_option_update_values_1,
    option_type,
    qty,
    price,
    expected_value,
):
    test_option = call_option if option_type == settings.OptionType.CALL else put_option
    test_option.open_trade(qty)

    quote_date, spot_price, bid, ask, _ = call_option_update_values_1
    test_option.update(quote_date, spot_price, bid, ask, price)

    assert test_option.get_total_profit_loss() == expected_value


def test_get_total_profit_loss_returns_closed_pnl_when_all_contracts_are_closed(
    call_option, call_option_update_values_1
):
    test_option = call_option
    test_option.open_trade(10)
    quote_date, spot_price, bid, ask, price = call_option_update_values_1
    test_option.update(quote_date, spot_price, bid, ask, price)
    test_option.close_trade(10)

    assert test_option.get_total_profit_loss() == 8_500.0


def test_get_total_profit_loss_returns_unrealized_and_closed_pnl_when_partially_closed(
    call_option, call_option_update_values_1, call_option_update_values_2
):
    test_option = call_option
    test_option.open_trade(10)
    quote_date, spot_price, bid, ask, price = call_option_update_values_1
    test_option.update(quote_date, spot_price, bid, ask, price)
    test_option.close_trade(5)  # 4250
    quote_date, spot_price, bid, ask, price = call_option_update_values_2
    test_option.update(quote_date, spot_price, bid, ask, price)  # 1750

    assert test_option.get_total_profit_loss() == 6_000.0


def test_get_total_profit_loss_returns_unrealized_and_closed_pnl_when_multiple_close_trades(
    call_option, call_option_update_values_1, call_option_update_values_2
):
    test_option = call_option
    test_option.open_trade(10)
    quote_date, spot_price, bid, ask, price = call_option_update_values_1
    test_option.update(quote_date, spot_price, bid, ask, price)
    test_option.close_trade(3)  # 2550
    quote_date, spot_price, bid, ask, price = call_option_update_values_2
    test_option.update(quote_date, spot_price, bid, ask, price)
    test_option.close_trade(3)  # 1050
    quote_date, spot_price, bid, ask, _ = call_option_update_values_2
    test_option.update(quote_date, spot_price, bid, ask, 8.0)  # 2600

    actual_value = test_option.get_total_profit_loss()
    assert actual_value == 6_200.0
