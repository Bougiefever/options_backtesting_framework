

# open trade
def test_open_trade_sets_correct_trade_open_info_values():
    test_option = get_test_call_option()
    quantity = 10

    trade_open_info = test_option.open_trade(quantity, comment="my super insightful comment")
    assert trade_open_info.date == test_quote_date
    assert trade_open_info.quantity == 10
    assert trade_open_info.price == 1.5
    assert trade_open_info.premium == 1_500.0
    assert test_option.quantity == 10

    # kwargs were set as attributes
    assert test_option.comment == "my super insightful comment"


def test_option_that_is_not_open_has_none_position_type():
    test_option = get_test_call_option()
    assert test_option.position_type is None


@pytest.mark.parametrize("quantity, position_type", [(10, OptionPositionType.LONG), (-10, OptionPositionType.SHORT)])
def test_open_trade_has_correct_position_type(quantity, position_type):
    test_option = get_test_call_option()
    test_option.open_trade(quantity)

    assert test_option.position_type == position_type


@pytest.mark.parametrize("test_option, quantity, expected_premium", [
    (get_test_call_option(), 10, 1_500.0),
    (get_test_call_option(), 5, 750.0),
    (get_test_call_option(), -10, -1_500.0),
    (get_test_put_option(), 10, 1_500.0),
    (get_test_put_option(), -10, -1_500.0),
    (get_test_put_option(), 5, 750.0),
    ])
def test_open_trade_returns_correct_premium_value(test_option, quantity, expected_premium):
    trade_open_info = test_option.open_trade(quantity)
    assert trade_open_info.premium == expected_premium


@pytest.mark.parametrize("quantity, incur_fees_flag, expected_fees", [(10, True, 5.0), (2, True, 1.0), (-3, True, 1.5),
                                                                      (10, False, 0.0), (2, False, 0.0),
                                                                      (-3, False, 0.0)])
def test_open_trade_sets_total_fees_when_incur_fees_flag_is_true(quantity, incur_fees_flag, expected_fees):
    test_option = get_test_call_option()
    test_option.fee_per_contract = standard_fee
    test_option.open_trade(quantity=quantity, incur_fees=incur_fees_flag)

    assert test_option.total_fees == expected_fees


def test_open_trade_when_there_is_no_quote_data_raises_exception():
    test_option = Option(1, ticker, 100, test_expiration, OptionType.CALL)
    with pytest.raises(ValueError, match="Cannot open a position that does not have price data"):
        test_option.open_trade(1)

@pytest.mark.parametrize("quantity", [None, 1.5, 0, -1.5, "abc"])
def test_open_trade_with_invalid_quantity_raises_exception(quantity):
    test_option = get_test_call_option()

    with pytest.raises(ValueError, match="Quantity must be a non-zero integer."):
        test_option.open_trade(quantity)


def test_open_trade_when_trade_is_already_open_raises_exception():
    test_option = get_test_call_option()
    quantity = 10
    test_option.open_trade(quantity)

    with pytest.raises(ValueError, match="Cannot open position. A position is already open."):
        test_option.open_trade(quantity)

