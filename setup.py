from setuptools import setup, find_packages

setup(
    name="yaml-changelog",
    version="0.1.5",
    author="PolicyEngine",
    license="http://www.fsf.org/licensing/licenses/agpl-3.0.html",
    url="https://github.com/policyengine/policyengine",
    install_requires=[
        "argparse",
        "datetime",
        "pathlib",
        "pyyaml",
        "requests",
    ],
    entry_points={
        "console_scripts": [
            "build-changelog = yaml_changelog.build:main",
            "bump-version = yaml_changelog.bump:main",
        ],
    },
    packages=find_packages(),
)
