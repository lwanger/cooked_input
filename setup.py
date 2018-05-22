
"""
see https://packaging.python.org/en/latest/distributing.html
    https://github.com/pypa/sampleproject
"""


from setuptools import setup, find_packages
from codecs import open
from os import path
from distutils.core import setup


here = path.abspath(path.dirname(__file__))

# load version number
version = {}
with open(path.join(here, 'cooked_input', 'version.py')) as f:
    exec(f.read(), version)

with open('README.rst', 'r', encoding='utf-8') as readme_file:
# with open('README.md', 'r', encoding='utf-8') as readme_file:
    readme = readme_file.read()

l_desc = readme + "\n\n"
# print('l_desc={}'.format(l_desc))

setup(
    name='cooked-input',
    version=version['__version__'],
    description='Get, clean, convert and validate input.',
    # long_description=l_desc,
    long_description=readme,
    # long_description_content_type='text/markdown',
    long_description_content_type='text/x-rst',
    # long_description_content_type='text/rst',
    author='Len Wanger',
    author_email='len_wanger@hotmail.com',
    url='https://github.com/lwanger/cooked_input',
    license='MIT',
    keywords='command line tool development input raw_input',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Database :: Front-Ends',
        'Topic :: Software Development',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=['setuptools-git', 'future', 'veryprettytable', 'dateparser', 'validus'],

    #python_required='>=2.7, >=3.3',

    #extras_require={
    #    'dev': ['check-manifest'],
    #    'test': ['coverage'],
    #},

    #package_data={
    #    # 'sample': ['package_data.dat'],
    #},

    include_package_data=True,

    #data_files=[],

    #entry_points={
    #    'console_scripts': [
    #        #'sample=sample:main',
    #    ],
    #},
)
