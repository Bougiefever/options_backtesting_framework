"""
This module contains tests for the enums defined in the options_framework.config.settings module.
These tests ensure that the enum values do not change unexpectedly, which could cause issues in other parts of the codebase.
"""

from options_framework.config import settings


def test_the_enums():
    assert settings.OptionType.CALL == 1
    assert settings.OptionType.PUT == 2

    assert settings.TransactionType.BUY == 1
    assert settings.TransactionType.SELL == 2

    assert settings.OptionPositionType.SHORT == 1

    assert settings.OptionCombinationType.SINGLE == 1
    assert settings.OptionCombinationType.VERTICAL == 2
    assert settings.OptionCombinationType.RATIO == 3
    assert settings.OptionCombinationType.CALENDAR == 4
    assert settings.OptionCombinationType.DIAGONAL == 5
    assert settings.OptionCombinationType.STRADDLE == 6
    assert settings.OptionCombinationType.STRANGLE == 7
    assert settings.OptionCombinationType.BUTTERFLY == 8
    assert settings.OptionCombinationType.IRON_BUTTERFLY == 9
    assert settings.OptionCombinationType.CONDOR == 10
    assert settings.OptionCombinationType.IRON_CONDOR == 11
    assert settings.OptionCombinationType.COLLAR == 12
    assert settings.OptionCombinationType.CUSTOM == 100

    assert settings.OptionTradeType.CREDIT == 1
    assert settings.OptionTradeType.DEBIT == 2
