import os

from setuptools import find_packages, setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


def requirements(fname):
    return [line.strip()
            for line in open(os.path.join(os.path.dirname(__file__), fname))]

setup(
    name='slacklogger',
    version='0.3.0',
    author='Tatsuya NAKAMURA',
    author_email='nkmrtty.com@gmail.com',
    description='A tool for logging messages on your Slack term.',
    license='MIT',
    url='https://github.com/nkmrtty/SlackLogger/',
    packages=find_packages(),
    keywords=['slack', 'logging', 'api'],
    install_requires=['slackclient']
)
