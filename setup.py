from setuptools import setup, find_packages

setup(
    name="searchai",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "typer",
        "rich",
        "crewai",
        "crewai-tools",
        "google-generativeai",
        "sqlalchemy",
        "asyncpg",
        "python-dotenv",
        "markdown",
        "reportlab",
        "python-pptx",
        "pdfkit",
        "certifi",
        "httpx",
        "httpcore",
        "greenlet",
        "psycopg2-binary",
    ],
    entry_points={
        "console_scripts": [
            "searchai=searchai.cli.interface:app",
        ],
    },
) 