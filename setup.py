from os import path, listdir
import setuptools

VERSION = "0.3.4"

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:

    long_description = f.read()


def __get_packages() -> list:

    ROOT_DIR = path.join(path.dirname(__file__), "REFPROPConnector")
    TEST_DIR = path.join(path.dirname(__file__), "REFPROPConnectorTest")
    packages = append_sub_dir(ROOT_DIR, list())
    packages = append_sub_dir(TEST_DIR, packages)
    return packages


def append_sub_dir(element_path, input_list: list, parent_name=None) -> list:

    if path.isdir(element_path):

        name = path.basename(element_path)

        if "__" not in name:

            if parent_name is not None:

                name = "{}.{}".format(parent_name, name)

            input_list.append(name)

            for sub_name in listdir(element_path):

                input_list = append_sub_dir(path.join(element_path, sub_name), input_list, parent_name=name)

    return input_list


setuptools.setup(

    name='REFPROP_connector',
    version=VERSION,
    license='GNU GPLv3',

    author='Pietro Ungar',
    author_email='pietro.ungar@unifi.it',

    description='Tools for launching REFPROP calculation and retrieving results from python',
    long_description=long_description,
    long_description_content_type='text/markdown',

    url='https://www.dief.unifi.it/vp-177-serg-group-english-version.html',
    download_url="https://github.com/SERGGroup/REFPROPConnector/archive/refs/tags/{}.tar.gz".format(VERSION),

    project_urls={

        'Source': 'https://github.com/SERGGroup/REFPROPConnector',
        'Tracker': 'https://github.com/SERGGroup/REFPROPConnector/issues',

    },

    packages=__get_packages(),

    install_requires=[

        'setuptools',
        'matplotlib',
        'ctREFPROP',
        'requests',
        'future',
        'tqdm',
        'sty'

    ],

    classifiers=[

        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',

      ]

)
