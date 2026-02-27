from setuptools import setup, find_packages

setup(
    name="scorecard_generator",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "plotly>=5.0.0",  # For interactive charts in HTML reports
    ],
)
