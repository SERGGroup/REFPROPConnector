from setuptools import setup
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(

    name='REFPROP_connector',
    version='0.0.5',
    license='GNU GPLv3',

    author='Pietro Ungar',
    author_email='pietro.ungar@unifi.it',

    description='Tools for launching REFPROP calculation and retrieving results from python',
    long_description=long_description,
    long_description_content_type='text/markdown',

    url='https://www.dief.unifi.it/vp-177-serg-group-english-version.html',
    download_url='https://github.com/SERGGroup/REFPROPConnector/archive/refs/tags/0.0.5.tar.gz',

    project_urls={

        'Source': 'https://github.com/SERGGroup/REFPROPConnector',
        'Tracker': 'https://github.com/SERGGroup/REFPROPConnector/issues',

    },

    packages=[

        'REFPROPConnector'

    ],

    install_requires=[

        'pyrebase4',
        'ctREFPROP',
        'setuptools',
        'requests',
        'future'

    ],

    classifiers=[

        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',

      ]

)
