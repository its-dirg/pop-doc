from setuptools import setup
from setuptools import find_packages

setup(
    name='pop',
    version='0.1',
    packages=find_packages("src"),
    package_dir={'': 'src'},
    url='https://github.com/its-dirg/proof-of-possession',
    license="Apache 2.0",
    author='DIRG',
    author_email='dirg@its.umu.se',
    description='Implementation of Proof of possesion for OpenID Connect.',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    install_requires=[
        "six",
        "signed-http-req"
    ]
)
