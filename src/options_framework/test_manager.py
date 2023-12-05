import datetime
from dataclasses import dataclass, field

from options_framework.data.data_loader import DataLoader
from options_framework.data.file_data_loader import FileDataLoader
from options_framework.data.sql_data_loader import SQLServerDataLoader
from options_framework.option_chain import OptionChain
from options_framework.config import settings
from options_framework.option_portfolio import OptionPortfolio
import pandas as pd
from pandas import DataFrame, Series

from options_framework.option_types import SelectFilter

@dataclass(repr=False)
class OptionTestManager:
    start_datetime: datetime.datetime
    end_datetime: datetime.datetime
    select_filter: SelectFilter
    starting_cash: float
    fields_list: list = field(default_factory=lambda: [])
    option_chain: OptionChain = field(init=False, default_factory=lambda: OptionChain())
    data_loader: DataLoader = field(init=False, default=None)
    portfolio: OptionPortfolio = field(init=False, default=None)

    def __post_init__(self):
        self.portfolio = OptionPortfolio(self.starting_cash)
        if settings.DATA_LOADER_TYPE == "FILE_DATA_LOADER":
            self.data_loader = FileDataLoader(start=self.start_datetime, end=self.end_datetime,
                                              select_filter=self.select_filter, fields_list=self.fields_list)
        elif settings.DATA_LOADER_TYPE == "SQL_DATA_LOADER":
            self.data_loader = SQLServerDataLoader(start=self.start_datetime, end=self.end_datetime,
                                                   select_filter=self.select_filter, fields_list=self.fields_list)
        self.data_loader.bind(option_chain_loaded=self.option_chain.on_option_chain_loaded)
        #self.data_loader.bind(option_chain_loaded=self.portfolio.on_options_updated)
        self.portfolio.bind(new_position_opened=self.data_loader.on_options_opened)

    def next(self, quote_datetime: datetime.datetime):
        self.portfolio.next(quote_datetime=quote_datetime)

    def next_option_chain(self, quote_datetime: datetime.datetime):
        self.data_loader.next_option_chain(quote_datetime=quote_datetime)
