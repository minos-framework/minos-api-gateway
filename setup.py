#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_namespace_packages

with open("README.md") as readme_file:
    readme = readme_file.read()

with open("HISTORY.md") as history_file:
    history = history_file.read()

requirements = []

setup_requirements = [
    "pytest-runner",
]

test_requirements = [
    "pytest>=3",
]

setup(
    author="Andrea Mucci",
    author_email="andrea@clariteia.com",
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    description="Minos Boilerplate contains all the boilerplate " "you need to create a Minos Python package.",
    install_requires=requirements,
    long_description_content_type="text/markdown",
    long_description=readme + "\n\n" + history,
    include_package_data=True,
    keywords="api_gateway",
    name="api_gateway",
    packages=find_namespace_packages(include=["minos.*"]),
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    version="0.0.1",
    zip_safe=False,
)
