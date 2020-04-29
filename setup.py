from importlib.machinery import SourceFileLoader

from setuptools import find_packages, setup

version = SourceFileLoader('version', 'stpmex/version.py').load_module()

install_requires = [
    'pyopenssl>=18.0.0,<18.1.0',
    'clabe>=1.0.0,<1.1.0',
    'pydantic>=1.4,<2.0',
    'dataclasses>=0.6;python_version<"3.7"',
    'requests>=2.22.0,<3.0',
]

test_requires = [
    'pytest',
    'pytest-vcr',
    'pycodestyle',
    'pytest-cov',
    'black',
    'isort[pipfile]',
    'flake8',
    'mypy',
]

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='stpmex',
    version=version.__version__,
    author='Cuenca',
    author_email='dev@cuenca.com',
    description='Client library for stpmex.com',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/cuenca-mx/stpmex-python',
    packages=find_packages(),
    include_package_data=True,
    package_data=dict(stpmex=['py.typed']),
    python_requires='>=3.6',
    install_requires=install_requires,
    setup_requires=['pytest-runner'],
    tests_require=test_requires,
    extras_require=dict(test=test_requires),
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
