from distutils.core import setup
import py2exe

setup(
    windows=["MainWindow.py"],
    options={"py2exe":{"includes":["sip", "PyQt5.QtCore", "PyQt5.QtWidgets"]}},
    name='PropellerDynamometer',
    version='',
    packages=['UI', 'Utils', 'Models', 'Functions', 'UIControllers'],
    url='',
    license='',
    author='Piotr Gomola',
    author_email='szkodniq@gmail.com',
    description=''
)
