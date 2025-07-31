from setuptools import setup, find_packages

setup(
    name="yaml-changelog",
    version="0.3.0",
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
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black",
            "flake8",
            "mypy",
            "types-PyYAML",
            "types-requests",
        ]
    },
    entry_points={
        "console_scripts": [
            "build-changelog = yaml_changelog.build:main",
            "yaml-changelog = yaml_changelog.build:main",
            "bump-version = yaml_changelog.bump:main",
            "yaml-changelog-init = yaml_changelog.init:init_changelog",
        ],
    },
    packages=find_packages(),
)
