from distutils.core import setup

__author__ = 'Paul Gundarapu'
__author_email__ = 'leogps@outlook.com'
__version__ = '0.1.0'
__license__ = 'MIT'
__description__ = 'Simple, zero-configuration command-line static HTTP server.'

packages = [
    'sipper_core',
    'static'
]

setup(
    name='bottle-sipper',
    packages=packages,
    version=__version__,
    license=__license__,
    description=__description__,
    long_description=__description__,
    long_description_content_type='text/markdown',
    author=__author__,
    author_email=__author_email__,
    url='https://github.com/leogps/bottle-sipper',
    keywords=['bottle',
              'http',
              'static',
              'file',
              'server',
              'http-server'],
    install_requires=[
        'bottle>=0.12.23',
        'argparse>=1.4.0',
        'ifaddr>=0.2.0'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
)
