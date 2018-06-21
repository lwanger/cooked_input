
"""
see https://packaging.python.org/en/latest/distributing.html
    https://github.com/pypa/sampleproject
"""


from setuptools import setup, find_packages
from os import path
# from io import open # Only needed for projects that want to support Python 2.7

here = path.abspath(path.dirname(__file__))

# load version number
version = {}
with open(path.join(here, 'cooked_input', 'version.py')) as f:
    exec(f.read(), version)

with open('README.rst', 'r', encoding='utf-8') as readme_file:
    readme = readme_file.read()

l_desc = readme + "\n\n"

setup(
    name='cooked-input',
    version=version['__version__'],
    description='Get, clean, convert and validate text-based input.',
    long_description=l_desc,
    long_description_content_type='text/x-rst',
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
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],

    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=['setuptools-git', 'future', 'dateparser', 'validus'],
    python_requires='>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*',

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
