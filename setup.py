from setuptools import find_packages, setup

setup(
    name="hyprparser",
    version="0.0.1",
    author="T0kyoB0y",
    description="A Pythonic parser for Hyprland configuration files.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/T0kyoB0y/hyprparser-py",
    project_urls={
        "Homepage": "https://github.com/T0kyoB0y/hyprparser-py",
        "Bug Tracker": "https://github.com/T0kyoB0y/hyprparser-py/issues",
    },
    packages=find_packages(),
    python_requires=">=3.10",
)
