"""
Setup configuration for AnimatedWidgetsPack
"""

from setuptools import setup, find_packages
import os

# Read README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="animated-widgets-pack",
    version="1.0.0",
    author="AnimatedWidgetsPack Team",
    author_email="team@animatedwidgetspack.com",
    description="Animated GUI widgets library for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/animated-widgets-pack",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/animated-widgets-pack/issues",
        "Documentation": "https://animated-widgets-pack.readthedocs.io/",
        "Source Code": "https://github.com/yourusername/animated-widgets-pack",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: User Interfaces",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.812",
            "sphinx>=4.0",
            "sphinx-rtd-theme>=0.5",
        ],
        "gui": [
            "PyQt5>=5.15.0",
            "PyQt6>=6.0.0",
        ],
        "examples": [
            "Pillow>=8.0.0",
            "matplotlib>=3.3.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "animated-widgets-demo=animated_widgets_pack.examples.demo:main",
        ],
    },
    include_package_data=True,
    package_data={
        "animated_widgets_pack": [
            "assets/*.png",
            "assets/*.ico",
            "themes/*.json",
        ],
    },
    keywords="gui widgets animation tkinter pyqt5 pyqt6 ui interface",
    zip_safe=False,
)