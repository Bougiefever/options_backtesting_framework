

def test_is_expired_returns_none_when_no_quote_data():
    test_option = Option(1, ticker, 100, test_expiration, OptionType.CALL)

    assert test_option.is_expired() is None


@pytest.mark.parametrize("expiration_date_test, quote_date, expected_result", [
    (datetime.datetime.strptime("07-16-2021", "%m-%d-%Y"),
     datetime.datetime.strptime("2021-07-01 09:45:00.000000", "%Y-%m-%d %H:%M:%S.%f"), False),
    (datetime.datetime.strptime("06-30-2021", "%m-%d-%Y"),
     datetime.datetime.strptime("2021-07-01 09:45:00.000000", "%Y-%m-%d %H:%M:%S.%f"), True),
    (datetime.datetime.strptime("07-16-2021", "%m-%d-%Y"),
     datetime.datetime.strptime("2021-07-16 09:45:00.000000", "%Y-%m-%d %H:%M:%S.%f"), False),
    (datetime.datetime.strptime("07-16-2021", "%m-%d-%Y"),
     datetime.datetime.strptime("2021-07-16 16:14:00.000000", "%Y-%m-%d %H:%M:%S.%f"), False),
    (datetime.datetime.strptime("07-16-2021", "%m-%d-%Y"),
     datetime.datetime.strptime("2021-07-16 16:15:00.000000", "%Y-%m-%d %H:%M:%S.%f"), True),
    (datetime.datetime.strptime("07-16-2021", "%m-%d-%Y"),
     datetime.datetime.strptime("2021-07-16", "%Y-%m-%d"), False),
    (datetime.datetime.strptime("07-16-2021", "%m-%d-%Y"),
     datetime.datetime.strptime("2021-07-17", "%Y-%m-%d"), True)])
def test_is_expired_returns_correct_result(expiration_date_test, quote_date, expected_result):
    test_option = get_test_call_option()

    # cheat to set data manually
    contract = option.OptionContract(1, ticker, expiration_date_test, 100.0, OptionType.CALL)
    test_option._option_contract = contract

    _, spot_price, bid, ask, price = get_test_put_option_update_values_1()
    quote = option.OptionQuote(quote_date, spot_price, bid, ask, price)
    test_option._option_quote = quote

    actual_result = test_option.is_expired()

    assert actual_result == expected_result