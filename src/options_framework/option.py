import datetime
import math
from options_framework.config import settings
from options_framework.utils.helpers import decimalize_0, decimalize_2, decimalize_4
from collections import namedtuple

optional_fields = [
    "open_interest",
    "implied_volatility",
    "delta",
    "gamma",
    "theta",
    "vega",
    "rho",
    "fee",
]
OptionContract = namedtuple(
    "OptionContract", "option_id symbol expiration strike option_type"
)
OptionQuote = namedtuple("OptionQuote", "quote_date spot_price bid ask price")
Greeks = namedtuple("Greeks", "delta gamma theta vega rho")
ExtendedProperties = namedtuple(
    "AdditionalOptionFields", "implied_volatility open_interest"
)
TradeOpen = namedtuple("TradeOpen", "date quantity price premium fees")
TradeClose = namedtuple(
    "TradeClose", "date quantity price profit_loss profit_loss_percent fees"
)


class Option:
    """
    The Option class holds all the values that pertain to a single option. The option can have just basic option information
    without any price or other current values. These values are id, symbol, strike, expiration and option type.
    Quote information can be set when the option is created and also using the update method.
    The trade_open and trade_close methods are used to capture open/close price and dates.
    """

    def __init__(
        self,
        option_id,
        symbol,
        strike,
        expiration,
        option_type,
        quote_date=None,
        spot_price=None,
        bid=None,
        ask=None,
        price=None,
        *args,
        **kwargs,
    ):
        """
        Creates an option object. An option must have an id, symbol, strike, expiration and type at a minimum.
        Price information can be included or can be set using the update method.

        :rtype: object
        :param option_id: unique identifier for the option *required*
        :type option_id: Any
        :param symbol: ticker symbol for underlying asset *required*
        :type symbol: string
        :param strike: the strike price for the option *required*
        :type strike: float
        :param expiration: the expiration date for the option *required*
        :type expiration: datetime.datetime
        :param option_type: Put or Call option *required*
        :type option: OptionType
        :param quote_date: data date for price information
        :type quote_date: datetime.datetime
        :param spot_price: price of underlying on quote_date
        :type spot_price: float
        :param bid: bid price
        :type bid: float
        :param ask: ask price
        :type ask: float
        :param price: calculated price based on mid-point between bid and ask
        :type price: float
        :param args: arguments
        :type: list
        :param kwargs: keyword arguments
        :type: dictionary

        optional parameters: delta, theta, vega, gamma, implied_volatility, open_interest, rho, fee
        If the fee is not specified it will be set to zero
        additional user-defined parameters passed as keyword arguments will be defined as attributes

        """
        # check for required fields
        if option_id is None:
            raise ValueError("option_id is required")
        if symbol is None:
            raise ValueError("symbol is required")
        if strike is None:
            raise ValueError("strike is required")
        if expiration is None:
            raise ValueError("expiration is required")
        if option_type is None:
            raise ValueError("option_type is required")
        if quote_date is not None and quote_date.date() > expiration.date():
            raise ValueError(
                "Cannot create an option with a quote date past its expiration date"
            )

        self._option_contract = OptionContract(
            option_id=option_id,
            symbol=symbol,
            expiration=expiration,
            strike=strike,
            option_type=option_type,
        )

        if any(
            [
                quote_date,
                spot_price,
                bid is not None,
                ask is not None,
                price is not None,
            ]
        ) and not all(
            [
                quote_date,
                spot_price,
                bid is not None,
                ask is not None,
                price is not None,
            ]
        ):
            raise ValueError(
                "All the required option quote values must be passed to set any quote values: quote date, spot price, bid, ask, price."
            )
        elif not any(
            [
                quote_date,
                spot_price,
                bid is not None,
                ask is not None,
                price is not None,
            ]
        ):
            self._option_quote = None
        elif all(
            [
                quote_date,
                spot_price,
                bid is not None,
                ask is not None,
                price is not None,
            ]
        ):
            self._option_quote = OptionQuote(
                quote_date=quote_date,
                spot_price=spot_price,
                bid=bid,
                ask=ask,
                price=price,
            )

        # The optional attributes are set using keyword arguments
        open_interest = (
            None
            if kwargs is None
            else kwargs["open_interest"]
            if "open_interest" in kwargs
            else None
        )
        iv = (
            None
            if kwargs is None
            else kwargs["implied_volatility"]
            if "implied_volatility" in kwargs
            else None
        )
        if open_interest is None and iv is None:
            self._extended_properties = None
        else:
            self._extended_properties = ExtendedProperties(
                implied_volatility=iv, open_interest=open_interest
            )

        delta = (
            None if kwargs is None else kwargs["delta"] if "delta" in kwargs else None
        )
        gamma = (
            None if kwargs is None else kwargs["gamma"] if "gamma" in kwargs else None
        )
        theta = (
            None if kwargs is None else kwargs["theta"] if "theta" in kwargs else None
        )
        vega = None if kwargs is None else kwargs["vega"] if "vega" in kwargs else None
        rho = None if kwargs is None else kwargs["rho"] if "rho" in kwargs else None
        if (
            delta is None
            and gamma is None
            and theta is None
            and vega is None
            and rho is None
        ):
            self._greeks = None
        else:
            self._greeks = Greeks(
                delta=delta, gamma=gamma, theta=theta, vega=vega, rho=rho
            )

        self._fee = 0 if kwargs is None else kwargs["fee"] if "fee" in kwargs else 0
        self._total_fees = 0

        self._trade_open = None
        self._trade_close_records = []
        self._position_type = None
        self._quantity = 0

        self._set_additional_attributes(kwargs)

    def __repr__(self) -> str:
        return (
            f"<{self._option_contract.option_type.name} {self._option_contract.symbol} {self._option_contract.strike} "
            + f'{datetime.datetime.strftime(self._option_contract.expiration, "%Y-%m-%d")}>'
        )

    def _set_additional_attributes(self, kwargs):
        """
        An internal method to set keyword arguments as attributes on the option object
        :param kwargs:
        :type: dict
        """
        additional_fields = {
            key: kwargs[key] for key in kwargs.keys() if key not in optional_fields
        }
        for key, value in additional_fields.items():
            setattr(self, key, value)

    def _incur_fees(self, quantity):
        """
        Calculates fees for a transaction and adds to the total fees
        :return: fees that were added to the option
        :rtype: float
        """
        fee = decimalize_2(self._fee)
        qty = decimalize_0(quantity)
        fees = fee * abs(qty)
        total_fees = decimalize_2(self._total_fees) + fees
        self._total_fees = float(total_fees)
        return float(fees)

    def update(self, quote_date, spot_price, bid, ask, price, *args, **kwargs):
        """
        Updates price and underlying asset information for a given data date and/or time

        :param quote_date: data date for price information
        :type quote_date: datetime.datetime
        :param spot_price: price of underlying on quote_date
        :type spot_price: float
        :param bid: bid price
        :type bid: float
        :param ask: ask price
        :type ask: float
        :param price: calculated price based on mid-point between bid and ask
        :type price: float

        optional parameters: delta, theta, vega, gamma, implied_volatility, open_interest, rho, fee
        additional user-defined parameters passed as keyword arguments will be defined as attributes
        """
        if quote_date is None:
            raise ValueError("quote_date is required")
        if spot_price is None:
            raise ValueError("spot_price is required")
        if bid is None:
            raise ValueError("bid is required")
        if ask is None:
            raise ValueError("ask is required")
        if price is None:
            raise ValueError("price is required")
        if quote_date.date() > self._option_contract.expiration.date():
            raise ValueError("Cannot update to a date past the option expiration")

        self._option_quote = OptionQuote(
            quote_date=quote_date, spot_price=spot_price, bid=bid, ask=ask, price=price
        )

        open_interest = (
            None
            if kwargs is None
            else kwargs["open_interest"]
            if "open_interest" in kwargs
            else None
        )
        implied_volatility = (
            None
            if kwargs is None
            else kwargs["implied_volatility"]
            if ("implied_volatility" in kwargs)
            else None
        )
        if open_interest is None and implied_volatility is None:
            self._extended_properties = None
        else:
            self._extended_properties = ExtendedProperties(
                implied_volatility=implied_volatility, open_interest=open_interest
            )

        delta = (
            None if kwargs is None else kwargs["delta"] if "delta" in kwargs else None
        )
        gamma = (
            None if kwargs is None else kwargs["gamma"] if "gamma" in kwargs else None
        )
        theta = (
            None if kwargs is None else kwargs["theta"] if "theta" in kwargs else None
        )
        vega = None if kwargs is None else kwargs["vega"] if "vega" in kwargs else None
        rho = None if kwargs is None else kwargs["rho"] if "rho" in kwargs else None
        if (
            delta is None
            and gamma is None
            and theta is None
            and vega is None
            and rho is None
        ):
            self._greeks = None
        else:
            self._greeks = Greeks(
                delta=delta, gamma=gamma, theta=theta, vega=vega, rho=rho
            )

        self._set_additional_attributes(kwargs)

    def open_trade(self, quantity, incur_fees=True, *args, **kwargs):
        """
        Opens a trade with a given quantity. Returns the premium amount of the trade.
        The premium is the cost to open the trade.
        A positive number for quantity opens a long position, which returns a positive
        amount for the premium. If the quantity is negative, a short position is
        opened, and premium amount is negative.

        :param quantity: quantity to open. Positive quantity will open long option.
            Negative quantity will open short option
        :type quantity: integer
        :param incur_fees: if True, fees will be incurred using the fee amount when option was created
        :type incur_fees: boolean
        :param args: arguments
        :type: list
        :param kwargs: keyword arguments
        :type: dictionary
        :return: The premium amount to open the trade.
        :rtype: float

        additional user-defined parameters passed as keyword arguments will be defined as attributes
        """
        if self._option_quote is None:
            raise ValueError("Cannot open a position that does not have price data")
        if self._trade_open is not None:
            raise ValueError("Cannot open position. A position is already open.")
        if (quantity is None) or not (isinstance(quantity, int)) or (quantity == 0):
            raise ValueError("Quantity must be a non-zero integer.")
        fees = 0
        if incur_fees:
            fees = self._incur_fees(quantity)

        # calculate premium debit or credit. If this is a long position, the premium is a positive number.
        # If it is a short position, the premium is a negative number.
        premium = float(
            decimalize_2(self._option_quote.price) * 100 * decimalize_0(quantity)
        )

        trade_open = TradeOpen(
            date=self._option_quote.quote_date,
            quantity=quantity,
            price=self._option_quote.price,
            premium=premium,
            fees=fees,
        )
        self._trade_open = trade_open
        self._position_type = (
            settings.OptionPositionType.LONG
            if quantity > 0
            else settings.OptionPositionType.SHORT
        )
        self._quantity = quantity

        self._set_additional_attributes(kwargs)

        return trade_open

    def close_trade(self, quantity=None, incur_fees=True, *args, **kwargs):
        """
        Calculates the closing price and sets the close date, price and profit/loss info for the
        quantity closed.
        :param quantity: If a quantity is provided, only that quantity will be closed.
        :param incur_fees: if True, calculates the fees for the closing transaction
            and adds that to the total fees
        :return: the profit/loss of the closed quantity of the trade
        :rtype: float
        """
        if self._trade_open.date is None:
            raise ValueError("Cannot close an option that is not open.")

        if quantity is None:
            quantity = decimalize_0(self._quantity) * -1
        elif not (isinstance(quantity, int)) or (quantity == 0):
            raise ValueError("Must supply a non-zero quantity.")
        # elif self._position_type == OptionPositionType.LONG and quantity + self._quantity - closed_quantity:
        #     raise ValueError("Quantity to close is greater than the current open quantity.")
        elif quantity < 0 and self._position_type == settings.OptionPositionType.LONG:
            raise ValueError(
                "This is a long option position. The quantity to close should be a positive number."
            )
        elif quantity > 0 and self._position_type == settings.OptionPositionType.SHORT:
            raise ValueError(
                "This is a short option position. The quantity should be a negative number."
            )
        elif (
            (self._position_type == settings.OptionPositionType.LONG)
            and quantity > self._quantity
        ) or (
            (self._position_type == settings.OptionPositionType.SHORT)
            and quantity < self._quantity
        ):
            raise ValueError(
                "Quantity to close is greater than the current open quantity."
            )
        else:
            quantity = decimalize_0(quantity) * -1

        close_price = decimalize_2(self.get_closing_price())
        open_price = decimalize_2(self._trade_open.price)
        profit_loss = (open_price * 100 * quantity) - (close_price * 100 * quantity)
        profit_loss_percent = decimalize_4((close_price - open_price) / open_price) * (
            quantity * -1 / abs(quantity)
        )

        fees = 0
        if incur_fees:
            fees = self._incur_fees(abs(quantity))

        # date quantity price premium profit_loss fees
        trade_close_record = TradeClose(
            date=self._option_quote.quote_date,
            quantity=int(quantity),
            price=float(close_price),
            profit_loss=float(profit_loss),
            profit_loss_percent=float(profit_loss_percent),
            fees=fees,
        )
        self._trade_close_records.append(trade_close_record)
        self._quantity = self._quantity + int(quantity)

        self._set_additional_attributes(kwargs)

        return trade_close_record

    def get_closing_price(self):
        """
        :return: Determines the appropriate closing price for an option. If an option
        is expired, appropriate ITM and OTM prices will be calculated.
        If the bid is zero, the value it can be bought or sold, depending on whether the
        option is short or long, will be returned.

        The option will not be closed until the close_trade method is called.

        Closing price can only be calculated on an option that has an open trade
        :rtype: float
        """
        if self._trade_open is None:
            raise ValueError(
                "Cannot determine closing price on option that does not have an opening trade"
            )
        price = decimalize_2(self._option_quote.price)
        spot_price = decimalize_2(self._option_quote.spot_price)
        close_price = None
        # check if option is expired (assume PM settled)
        # If an option is expired, the price in the data may not match what the actual
        # settlement price of the option. An expired option's value is always
        # its intrinsic value. An out-of-the-money has no intrinsic value,
        # therefore its expiry price is zero.
        # If an option expires in the money, its value is equal to its intrinsic value.
        # Just calculate the intrinsic value and return that price.
        if self.is_expired():
            if self.otm:  # OTM options have no value at expiration
                close_price = 0

            # ITM options value is the difference between the spot price and the strike price
            elif self.itm:  # ITM options only have intrinsic value at expiration
                if self._option_contract.option_type == settings.OptionType.CALL:
                    close_price = spot_price - self._option_contract.strike
                elif self._option_contract.option_type == settings.OptionType.PUT:
                    close_price = self._option_contract.strike - spot_price

        # Normally, the option price is assumed to be halfway between the bid and ask
        # When the bid is zero, it implies that there are no buyers, and only sellers at the ask price
        # Therefore, the option can only be bought at the ask and cannot be sold at any price
        # LONG options must be sold to close. Therefore, if the bid is zero,
        # the option is worthless since it cannot be sold.
        # SHORT options must be bought to close. If the bid is zero,
        # the option can only be bought to close for the ask price
        #
        # If the bid is not zero, then the price is the mid-point between the bid and ask
        else:  # option is not expired
            if self._option_quote.bid == 0:
                # bid is zero, option is long. Cannot be sold to close, therefore it is worthless
                if self._position_type == settings.OptionPositionType.LONG:
                    close_price = 0
                # bid is zero, option is short. The other side of this transaction holds a long option,
                # which is worthless. People will always take free money for something that is worthless,
                # so the option can be bought to close for the ask price.
                elif self._position_type == settings.OptionPositionType.SHORT:
                    close_price = self._option_quote.ask
            else:
                close_price = price
        return float(close_price)

    def get_trade_open_info(self):
        """
        The trade_open_info returns all the values captured when a trade is opened.
        This contains the following properties:
        date: The trade open date
        spot_price: The spot price of the underlying asset when the trade was opened
        quantity: The number of contracts that were opened. A positive number is a long position, and a negative number
                    is a short position
        price: The price the option was bought or sold at
        open_value: The total credit or debit premium when opening the trade

        :return: A named tuple with the following properties: date, spot_price, quantity, price, open_value
        :rtype: A TradeOpen named tuple
        """
        return self._trade_open

    def get_trade_close_info(self):
        """
        The
        :return:
        """
        if not self._trade_close_records:
            return None
        # date quantity price premium profit_loss fees
        records = self._trade_close_records
        date = records[-1].date
        quantity = sum(decimalize_0(x.quantity) for x in records)
        trade_open_premium = decimalize_2(self._trade_open.premium)
        price = decimalize_2(
            sum(
                (decimalize_2(x.price) * decimalize_0(x.quantity)) / quantity
                for x in records
            )
        )

        profit_loss = sum(decimalize_2(x.profit_loss) for x in records)
        profit_loss_percent = decimalize_4(profit_loss / trade_open_premium) * (
            quantity * -1 / abs(quantity)
        )
        fees = sum(x.fees for x in records)

        trade_close = TradeClose(
            date=date,
            quantity=int(quantity),
            price=float(price),
            profit_loss=float(profit_loss),
            profit_loss_percent=float(profit_loss_percent),
            fees=fees,
        )

        return trade_close

    def dte(self):
        """
        DTE is "days to expiration"
        :return: The number of days to the expiration for the current quote
        :rtype: int
        """
        if self._option_quote is None:
            return None
        dt_date = self._option_quote.quote_date.date()
        time_delta = self._option_contract.expiration.date() - dt_date
        return time_delta.days

    def is_expired(self):
        """
        Assumes the option is PM settled. If there is no quote data, the expiration status has
        no meaning, so None is returned.
        :return: True if option quote is at or exceeds the expiration date
        :rtype: bool
        """
        if self._option_quote is None:
            return None
        quote_date, expiration_date = (
            self._option_quote.quote_date.date(),
            self._option_contract.expiration.date(),
        )
        quote_time, exp_time = self._option_quote.quote_date.time(), datetime.time(
            16, 15
        )
        if (quote_date == expiration_date and quote_time >= exp_time) or (
            quote_date > expiration_date
        ):
            return True
        else:
            return False

    def is_trade_open(self):
        """
        Returns boolean indicating whether a trade has any open contracts.
        :return: True if there are open contracts, False if a trade was never opened, or was opened
                    and then fully closed.
        :rtype: bool
        """
        return self._quantity != 0

    def get_open_profit_loss(self):
        """
        Returns the current unrealized profit/loss. This is the difference in value between
        the trade open and the current quote.
        The value is determined by multiplying the price difference by the quantity and number
        of underlying units the option represents (100).
        This method uses the current price of the option. This may be different than the closing
        price which considers other factors such as expiration and intrinsic value.
        :return: the current value of the trade
        :rtype: float
        """
        if self._trade_open is None:
            raise Exception("No trade has been opened.")

        trade_price = decimalize_2(self._trade_open.price)
        price = decimalize_2(self._option_quote.price)
        quantity = decimalize_0(self._quantity)
        trade_premium = trade_price * 100 * quantity
        current_premium = price * 100 * quantity
        value = current_premium - trade_premium
        return float(value)

        # price_diff = price - trade_price
        # value = price_diff * 100 * quantity
        # return float(value)

    def get_total_profit_loss(self):
        """
        Returns the total realized and unrealized profit/loss.
        :return: Returns the total profit/loss for both open and closed contracts.
        :rtype: float
        """
        if self._trade_open is None:
            raise Exception("No trade has been opened.")

        unrealized_pnl = self.get_open_profit_loss()
        # if no contracts were closed, this is just the open pnl
        if not self._trade_close_records:
            return unrealized_pnl
        realized_pnl = sum(
            x.profit_loss for x in self._trade_close_records
        )  # self._trade_close.profit_loss

        total_profit_loss = unrealized_pnl + realized_pnl
        return total_profit_loss

    def get_open_profit_loss_percent(self):
        """
        Returns the unrealized profit/loss percent.
        The percentage gain or loss based on the current price compared to the trade price of an option.
        :return: the percentage gain or loss
        :rtype: float
        """
        if self._trade_open is None:
            raise Exception("No trade has been opened.")
        if self._quantity == 0:
            return 0.0
        trade_price = decimalize_4(self._trade_open.price)
        price = decimalize_4(self._option_quote.price)
        quantity = decimalize_0(self._quantity)
        percent = ((price - trade_price) / trade_price) * (quantity / abs(quantity))
        return float(decimalize_4(percent))

    def get_total_profit_loss_percent(self):
        if self._trade_open is None:
            raise Exception("No trade has been opened.")

        price = decimalize_2(self._option_quote.price)
        quantity = decimalize_0(self._quantity)
        opening_trade_value = decimalize_2(self._trade_open.premium)
        closed_contracts_value = sum(
            decimalize_2(x.price) * 100 * decimalize_0(x.quantity) * -1
            for x in self._trade_close_records
        )
        open_contracts_value = price * 100 * quantity
        value_of_trade = open_contracts_value + closed_contracts_value
        profit_loss_percent = decimalize_4(
            (value_of_trade - opening_trade_value) / opening_trade_value
        )
        if self._position_type == settings.OptionPositionType.SHORT:
            profit_loss_percent *= -1

        return float(profit_loss_percent)

    def get_days_in_trade(self):
        if self._trade_open is None:
            raise Exception("No trade has been opened.")

        # if the trade has any open contracts, use current quote date.
        # if the trade is closed, then use the latest close date.
        if self._quantity > 0:
            dt_date = self._option_quote.quote_date.date()
        else:
            dt_date = self._trade_close_records[-1].date.date()

        time_delta = dt_date - self._trade_open.date.date()
        return time_delta.days

    def itm(self):
        """
        In the Money
        A call option is in the money when the current price is higher than or equal to the strike price
        A put option is in the money when the current price is lower than or equal to the strike price
        Returns a boolean value indicating whether the option is currently in the money.
        :return: Returns a boolean value indicating whether the option is currently in the money.
        :rtype: bool
        """
        if self._option_quote is None:
            return None

        if self._option_contract.option_type == settings.OptionType.CALL:
            return (
                True
                if self._option_quote.spot_price >= self._option_contract.strike
                else False
            )
        elif self._option_contract.option_type == settings.OptionType.PUT:
            return (
                True
                if self._option_quote.spot_price <= self._option_contract.strike
                else False
            )

    def otm(self):
        """
        Out of the Money
        A call option is out of the money when the current price is lower than the spot price.
        A put option is out of the money when the current price is greater than the spot price.
        :return: Returns a boolean value indicating whether the option is currently out of the money.
        :rtype: bool
        """
        if self._option_quote is None:
            return None

        if self._option_contract.option_type == settings.OptionType.CALL:
            return (
                True
                if self._option_quote.spot_price < self._option_contract.strike
                else False
            )
        elif self._option_contract.option_type == settings.OptionType.PUT:
            return (
                True
                if self._option_quote.spot_price > self._option_contract.strike
                else False
            )

    @property
    def option_contract(self):
        """
        The option contains all the properties of a contract that do not change:

        id: A unique identifier for the option
        symbol: The ticker symbol of the underlying asset
        expiration: The option expiration date
        strike: The option strike price
        option_type: OptionType.PUT or OptionType.CALL
        :return: A named tuple with the following properties: id, symbol, expiration, strike, option_type
        :rtype: OptionContract named tuple
        """
        return self._option_contract

    @property
    def option_id(self):
        return self._option_contract.option_id

    @property
    def symbol(self):
        return self._option_contract.symbol

    @property
    def strike(self):
        return self._option_contract.strike

    @property
    def expiration(self):
        return self._option_contract.expiration

    @property
    def option_type(self):
        return self._option_contract.option_type

    @property
    def option_quote(self):
        """
        The option quote contains all the information that will change throughout it's lifetime, such as the price
        The option quote has the following properties:

        quote_date: The data date
        spot_price: The price of the underlying as of the data date
        bid: The bid price of the option as of the data date
        ask: The ask price of the option as of the data date
        price: The mid-point of the bid and ask price of the option as of the data date

        These may be set to None if the option contract data is not populated

        :return: A named tuple with the following properties: quote_date, spot_price, bid, ask, price
        :rtype: OptionQuote named tuple
        """
        return self._option_quote

    @property
    def quote_date(self):
        return None if self._option_quote is None else self._option_quote.quote_date

    @property
    def spot_price(self):
        return None if self._option_quote is None else self._option_quote.spot_price

    @property
    def bid(self):
        return None if self._option_quote is None else self._option_quote.bid

    @property
    def ask(self):
        return None if self._option_quote is None else self._option_quote.ask

    @property
    def price(self):
        return None if self._option_quote is None else self._option_quote.price

    @property
    def extended_properties(self):
        """
        The extended properties are optional properties that can be set and updated on an option.
        The extended properties contain the following: implied volatility, open interest,
            the standard fee for trading 1 contract
        :return: A named tuple with the following properties: implied_volatility, open_interest
        :rtype: ExtendedProperties named tuple containing: implied_volatility, open_interest
        """
        return self._extended_properties

    @property
    def implied_volatility(self):
        return (
            None
            if self._extended_properties is None
            else self._extended_properties.implied_volatility
        )

    @property
    def open_interest(self):
        return (
            None
            if self._extended_properties is None
            else self._extended_properties.open_interest
        )

    @property
    def greeks(self):
        """
        The option greeks contains the current values as of the data date of the option_contract property
        The greeks property contains the following attributes: delta, gamma, theta, vega, rho
        These may be set to None if they are not populated

        :return: A named tuple with the following properties: delta, gamma, theta, vega, rho
        :rtype: A Greeks named tuple containing: delta, gamma, theta, vega, rho
        """
        return self._greeks

    @property
    def delta(self):
        return None if self._greeks is None else self._greeks.delta

    @property
    def gamma(self):
        return None if self._greeks is None else self._greeks.gamma

    @property
    def theta(self):
        return None if self._greeks is None else self._greeks.theta

    @property
    def vega(self):
        return None if self._greeks is None else self._greeks.vega

    @property
    def rho(self):
        return None if self._greeks is None else self._greeks.rho

    @property
    def trade_close_records(self):
        """
        When a trade is closed, either fully or partially, a trade close record is created and added to the
        close records. This methon will return all the trade close transaction records.
        :return: The array containing all the closing trade records
        :rtype: TradeClose, a numed tuple containing: date, quantity, price, premium, profit_loss, fees
        """
        return self._trade_close_records

    @property
    def total_fees(self):
        """
        All the fees that have been incurred for this option.
        A fee per contract amount can be set when the option is created. When the option is traded,
        the fee will be applied for the number of contracts traded and added to the total fees.
        :return: current fees
        :rtype: float
        """
        return self._total_fees

    @property
    def position_type(self):
        """
        The position type is determined when the option is opened. It is either long or short.
            An option is long if the quantity is positive. It is bought to open and sold to close.
            An option is short if the quantity is negative. It is sold to open and bought to close
        :return: OptionPositionType of LONG or SHORT
        :rtype: OptionPositionType
        """
        return self._position_type

    @property
    def quantity(self):
        """
        A positive quantity indicates a long position, and a negative quantity indicates a short position
        :return: quantity
        :rtype: integer
        """
        return self._quantity

    @property
    def fee_per_contract(self):
        return self._fee

    @fee_per_contract.setter
    def fee_per_contract(self, value):
        if math.isnan(value) or value < 0:
            raise ValueError("Fee per contract must be zero or a positive number")
        self._fee = value
