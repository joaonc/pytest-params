from pathlib import Path

from setuptools import setup

PROJECT_ROOT = Path(__file__).parent

with open(PROJECT_ROOT / 'README.md') as f:
    long_description = f.read()

setup(
    name='pytest-params',
    version='0.1.0',
    py_modules=['pytest_params'],
    provides=['pytest_params'],
    description='Simpler pytest test case parameters.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Joao Coelho',
    author_email='6wfon3p6d@mozmail.com',
    url='https://github.com/joaonc/pytest-params',
    keywords='pytest',
    # install_requires=REQUIREMENTS,
    license='MIT License',
    python_requires='>=3.10',
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
)
