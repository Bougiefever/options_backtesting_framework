import pytest
from options_framework.config import settings


def test_get_profit_loss_percent_return_zero_when_no_contracts_are_open(call_option):
    test_option = call_option
    test_option.open_trade(1)
    test_option.close_trade(1)

    assert test_option.get_open_profit_loss_percent() == 0.0


@pytest.mark.parametrize(
    "option_type, quantity, price, expected_profit_loss_pct",
    [
        (settings.OptionType.CALL, 10, 2.25, 0.5),
        (settings.OptionType.CALL, 10, 1.17, -0.22),
        (settings.OptionType.CALL, 10, 1.5, 0.0),
        (settings.OptionType.CALL, -10, 2.25, -0.50),
        (settings.OptionType.CALL, -10, 1.17, 0.22),
        (settings.OptionType.CALL, -10, 1.5, 0.0),
        (settings.OptionType.PUT, 10, 2.25, 0.5),
        (settings.OptionType.PUT, 10, 1.17, -0.22),
        (settings.OptionType.PUT, 10, 1.5, 0.0),
        (settings.OptionType.PUT, -10, 2.25, -0.50),
        (settings.OptionType.PUT, -10, 1.17, 0.22),
        (settings.OptionType.PUT, -10, 1.5, 0.0),
    ],
)
def test_get_profit_loss_percent_value(
    call_option,
    put_option,
    call_option_update_values_1,
    option_type,
    quantity,
    price,
    expected_profit_loss_pct,
):
    test_option = call_option if option_type == settings.OptionType.CALL else put_option
    test_option.open_trade(quantity)
    quote_date, spot_price, bid, ask, _ = call_option_update_values_1
    test_option.update(quote_date, spot_price, bid, ask, price)

    actual_profit_loss = test_option.get_open_profit_loss_percent()
    assert actual_profit_loss == expected_profit_loss_pct
