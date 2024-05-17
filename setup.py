from setuptools import setup, find_packages

VERSION = "3.0"

setup(
    name="gaycore",
    version=VERSION,
    description="A tiny and smart cli player of gcore audio, based on Python package curses and mpg123 for Linux or Mac",
    long_description="gaycore listen player using cli enjoy it",
    keywords="python gcore gaycore cli terminal",
    author="yihong0618",
    author_email="zouzou0208@gmail.com",
    url="https://github.com/yihong0618/gaycore",
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,
    install_requires=["requests", "miservice-fork"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries",
    ],
    entry_points={
        "console_scripts": ["gaycore = gaycore.cli:run"],
    },
)
