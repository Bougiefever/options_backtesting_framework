import datetime
import itertools
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from ..option import Option
from ..option_types import OptionCombinationType, OptionStatus, OptionPositionType


@dataclass(repr=False, slots=True)
class OptionCombination(ABC):
    """
    OptionCombination is a base class an options trade that is constructed with one or more option types,
    quantities, and expirations.
    There are several pre-defined classes for popular options spreads, but you can create a
    custom class, or just pass a list of options that make up the trade
    """

    options: list[Option]
    option_combination_type: OptionCombinationType = field(default=None)
    option_position_type: OptionPositionType = field(default=None)
    quantity: int = field(default=None)
    position_id: int = field(init=False, default_factory=lambda counter=itertools.count(): next(counter))
    user_defined: dict = field(default_factory=lambda: {})

    def __post_init__(self):
        # The OptionCombination object should not be instantiated directly, but only through subclasses.
        raise NotImplementedError

    def __repr__(self) -> str:
        return f'<{self.option_combination_type.name}({self.position_id}) Quantity: {len(self.options)} options>'

    @property
    def current_value(self) -> float:
        current_value = sum([o.current_value for o in self.options])
        return current_value

    @property
    def trade_value(self):
        opening_value = sum([o.trade_value for o in self.options])
        return opening_value

    @abstractmethod
    def open_trade(self, *, quantity: int, **kwargs: dict) -> None:
        pass

    @abstractmethod
    def close_trade(self, *, quantity: int, **kwargs: dict) -> None:
        pass

    @property
    def max_profit(self) -> float | None:
        """
        If there is a determinate max profit, that is returned by the parent class.
        If there is an infinite max profit, as is the case for a naked option type, returns None
        :return: None or the max profit of the spread
        """
        return None

    @property
    def max_loss(self) -> float | None:
        """
        If there is a determinate max loss, that is returned by the parent class.
        If there is an infinite max loss, as is the case for a naked option type, returns None
        :return: None or the max loss of the spread
        """
        return None

    def get_profit_loss(self) -> float:
        return sum(o.get_profit_loss() for o in self.options)

    def get_unrealized_profit_loss(self) -> float:
        return sum(o.get_unrealized_profit_loss() for o in self.options)

    def get_trade_premium(self) -> float | None:
        if all((OptionStatus.TRADE_IS_OPEN & OptionStatus.TRADE_IS_CLOSED) in o.status for o in self.options):
            return sum(o.trade_open_info.premium for o in self.options)
        else:
            return None

    @abstractmethod
    def get_trade_price(self) -> float | None:
        pass

    def get_open_datetime(self) -> datetime.datetime | None:
        first_option = self.options[0]
        if (OptionStatus.TRADE_IS_OPEN & OptionStatus.TRADE_IS_CLOSED) not in first_option.status:
            return None
        open_date = first_option.trade_open_info.date
        return open_date

    def get_close_datetime(self):
        first_option = self.options[0]
        if OptionStatus.TRADE_IS_CLOSED not in first_option.status:
            return None
        return first_option.trade_close_info.date

