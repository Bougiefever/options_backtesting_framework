import datetime
import pandas as pd
from pathlib import Path

from options_framework.data.data_loader import DataLoader
from options_framework.config import settings
from pydispatch import Dispatcher

from options_framework.option_types import SelectFilter
from test_data.spx_test_options import *


class MockPortfolio(Dispatcher):
    _events_ = ['new_position_opened', 'next']

    def open_position(self, position):
        position.open_trade(quantity=1)
        for o in position.options:
            self.bind(next=o.next_update)
        self.emit('new_position_opened', self, position.options)

    def next(self, quote_datetime: datetime.datetime, *args):
        self.emit('next', quote_datetime)


class MockSPXOptionChain:
    quote_datetime: datetime.datetime = datetime.datetime(2016, 3, 1, 9, 31)
    option_chain: list = t1_options
    expirations: list = expirations
    expiration_strikes: dict = expiration_strikes


class MockSPXDataLoader(DataLoader):

    def load_option_chain_data(self, symbol: str, start: datetime.datetime):
        if start == datetime.datetime(2016, 3, 1, 9, 31):
            return t1_options
        elif start == datetime.datetime(2016, 3, 1, 9, 32):
            return t2_options
        else:
            return None

    def get_expirations(self, symbol: str) -> list:
        return expirations

    def on_options_opened(self, portfolio, options: list[Option]) -> None:
        for option in options:
            data_file_name = Path(settings.TEST_DATA_DIR, f'option_{option.option_id}.csv')
            cache = pd.read_csv(data_file_name.absolute(), parse_dates=True, index_col='quote_datetime')
            option.update_cache = cache
