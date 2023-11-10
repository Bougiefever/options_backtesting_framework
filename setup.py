from setuptools import setup, find_packages

setup(
    name='options_framework',
    version='0.1.0.a',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    entry_points={
        'console_scripts': [
            'pcmd=options_framework.cli:main',
        ],
    },
)

