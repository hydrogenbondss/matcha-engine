from setuptools import setup, find_packages

setup(
    name="matcha-engine",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "typer>=0.9.0",
        "pydantic>=2.0",
        "pyyaml>=6.0",
        "pillow>=10.0",
        "gitpython>=3.1",
    ],
    entry_points={
        "console_scripts": [
            "matcha=matcha.cli:app",
        ],
    },
    python_requires=">=3.9",
)
