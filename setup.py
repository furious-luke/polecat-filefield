import os

from setuptools import find_packages, setup

version = '0.0.0'

setup(
    name='polecat-filefield',
    version=version,
    author='Luke Hodkinson',
    author_email='furious.luke@gmail.com',
    maintainer='Luke Hodkinson',
    maintainer_email='furious.luke@gmail.com',
    description='',
    long_description=open(
        os.path.join(os.path.dirname(__file__), 'README.md')
    ).read(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: MIT License'
    ],
    packages=find_packages(exclude=['tests', 'extern']),
    include_package_data=True,
    package_data={'': ['*.txt', '*.js', '*.html', '*.*']},
    install_requires=[],
    extras_require={},
    entry_points={},
    zip_safe=True
)
