from distutils.core import setup

import sipper_setup as sipper

setup(
    name='bottle-sipper',
    packages=[
        'sipper_core',
        'static',
    ],
    version=sipper.__version__,
    license=sipper.__license__,
    description=sipper.__description__,
    author=sipper.__author__,
    author_email=sipper.__author_email__,
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
