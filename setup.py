"""
    setup file
    configures the package of Honeypot
"""

from setuptools import setup
from Honeypot.Settings.HoneypotSettings import Settings

setup(
    name="Honeypot",
    version=Settings.__version__,
    description="Python Honeypot Project",
    author="Dawid Czyrny",
    author_email="czyrny.dawid@gmail.com",
    packages=['Honeypot'],
    install_requires=["paramiko"],
    entry_points={
        'console-scripts': [
            'Honeypot = Honeypot.__main__:main'
        ]
    },
)
