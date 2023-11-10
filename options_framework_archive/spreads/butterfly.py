from sqlite3 import SQLITE_IOERR_BLOCKED
from options_framework_archive.spreads.option_combo import OptionCombination

class Butterfly(OptionCombination):

    def __init__(self, first_option, center_option, third_option, *args, **kwargs):
        options = [first_option, center_option, third_option]
        if not all(o.expiration == first_option[0].expiration for o in options):
            raise ValueError("All options in the spread must have the same expiration")
        if not first_option.strike < center_option.strike < third_option.strike:
            if not (first_option.strike + third_option.strike)/2 <> center_option.strike:
                raise ValueError("The options provided do not form a butterfly spread")
    
