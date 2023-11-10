
def test_dte_is_none_when_option_does_not_have_quote_data():
    test_option = Option(1, ticker, 100, test_expiration, OptionType.CALL)

    assert test_option.dte() is None


def test_dte_when_option_has_quote_data():
    test_option = get_test_call_option()

    expected_dte = 15
    actual_dte = test_option.dte()
    assert actual_dte == expected_dte


def test_dte_is_updated_when_quote_date_is_updated():
    test_option = get_test_call_option()
    quote_date, spot_price, bid, ask, price = get_test_put_option_update_values_1()
    test_option.update(quote_date, spot_price, bid, ask, price)

    expected_dte = 14
    assert test_option.dte() == expected_dte


@pytest.mark.parametrize("expiration_datetime",
                         [datetime.datetime.strptime("2021-07-16 09:31:00.000000", "%Y-%m-%d %H:%M:%S.%f"),
                          datetime.datetime.strptime("2021-07-16 11:00:00.000000", "%Y-%m-%d %H:%M:%S.%f"),
                          datetime.datetime.strptime("2021-07-16 16:15:00.000000", "%Y-%m-%d %H:%M:%S.%f")])
def test_dte_is_zero_on_expiration_day(expiration_datetime):
    test_option = get_test_call_option()
    _, spot_price, bid, ask, price = get_test_put_option_update_values_1()
    test_option.update(expiration_datetime, spot_price, bid, ask, price)

    expected_dte = 0
    assert test_option.dte() == expected_dte
