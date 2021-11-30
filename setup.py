from setuptools import setup, find_packages
from os import path

with open("README.md", "r") as fh:
    long_description = fh.read()

install_requires = [
    'PyYAML', 'SQLAlchemy', 'numpy', 'pandas', 'plotly'
]

setup(
    name="custmaker",
    version="1.0.1.0",
    author="Jihyun Kim",
    author_email="bibbidi0917@naver.com",
    description="create customer data in local database",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    py_modules=['custmaker'],
    url="https://github.com/bibbidi0917/custmaker",
    packages=find_packages(),
    classifier=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8"
    ],
    python_requires='>=3.8',
    install_requires=install_requires
)