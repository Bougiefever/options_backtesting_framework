# Change log

## 2023-11-09 - v0.1.0.a

- Update README.md with pytest example
- Added `pytest.ini`
  - pointed default test dir to `tests` so the tests archive doesn't get run
  - added options by default that show STDOUT, increase test verbosity, and show short tracebacks 
- Added `tests/test_silly.py`
  - a silly test to make sure pytest is working
- Added `tests_archive/` directory
  - Archived `tests/options_test_helper.py`
  - Archived `tests/test_data/L2_options_20230301.csv` and similar files
  - Archived `tests/test_data/spx_11_01_2021.csv` and similar files
  - Archived `tests/test_option.py`
  - Archived `tests/test_option_chain.py`
  - Archived `tests/test_option_combo.py`
  - Archived `tests/test_single_option.py`
  - Archived `tests/test_test.py`
  - Archived `tests/test_vertical_spread.py`

## 2023-11-09 - v0.1.0

- update README.md with CLI examples
- create change log file
- added pipenv support
- added black formatter
- added pylint
- added dynaconf to simplify configuration management
- added a basic CLI
- created a `src` directory and a `setup.py` so the project is installable using `pip install -e .`
- modified .gitignore to include dynaconf secrets file
- created a `template.secrets.toml` file for to document dynaconf secrets