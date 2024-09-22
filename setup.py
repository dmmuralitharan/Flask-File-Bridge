from setuptools import setup, find_packages

setup(
    name="Flask-File-Bridge",
    version="0.1.4",
    author="Muralitharan",
    author_email="dmmuralitharan@gmail.com",
    description="A library for importing and exporting data from Excel and CSV files using Flask ORM.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/dmmuralitharan/Flask-File-Bridge",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "Flask",
        "Flask-SQLAlchemy",
        "pandas",
        "openpyxl",
    ],
)
