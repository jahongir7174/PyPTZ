import os
import re

import setuptools


def read(filename):
    path = os.path.join(os.path.abspath(os.path.dirname(__file__)), filename)
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    return content


def get_version(text):
    match = re.search(r"^__version__\s*=\s*['\"](.*)['\"]\s*$", text, re.MULTILINE)
    return match.group(1)


setuptools.setup(name='pyptz',
                 version=get_version(read('pyptz/__init__.py')),
                 author='Jahongir Yunusov',
                 license='MIT',
                 description='PTZ Camera Control using Python',
                 long_description=read('README.md'),
                 long_description_content_type="text/markdown",
                 packages=setuptools.find_packages(),
                 url="https://github.com/jahongir7174/PyPTZ",
                 classifiers=["Programming Language :: Python :: 3",
                              "License :: OSI Approved :: MIT License",
                              "Operating System :: OS Independent", ],
                 keywords=['ONVIF', 'VAPIX', 'SUNAPI'],
                 python_requires='>=3.6',
                 install_requires=['urllib3==1.26.18',
                                   'requests==2.31.0',
                                   'onvif-zeep==0.2.12',
                                   'beautifulsoup4==4.12.3'])
