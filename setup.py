from setuptools import setup, find_packages

setup(
    name="yaml-changelog",
    version="0.1.1",
    author="PolicyEngine",
    license="http://www.fsf.org/licensing/licenses/agpl-3.0.html",
    url="https://github.com/policyengine/policyengine",
    install_requires=[
        "argparse",
        "datetime",
        "pathlib",
        "pyyaml",
        "requests",
        "black",
        "autopep8",
        "wheel",
    ],
    entry_points={
        "console_scripts": [
            "build-changelog = build:main",
        ],
    },
    packages=find_packages(),
)
