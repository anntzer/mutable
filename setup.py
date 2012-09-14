from distutils.core import setup
import mutable

setup(
    name='mutable',
    version='0.1.1',
    author='Antony Lee',
    author_email='anntzer.lee@gmail.com',
    py_modules=['mutable'],
    url='http://github.com/anntzer/mutable',
    license='LICENSE.txt',
    description='Assignment as a Python expression through overloading of <<.',
    long_description=mutable.__doc__,
)
