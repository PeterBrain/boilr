from setuptools import setup, find_packages
import boilr

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='boilr',
    version=boilr.__version__,
    description='Water boiler automation with a Fronius pv inverter on a raspberry pi.',
    license=license,
    long_description=readme,
    author='Peter Loecker',
    author_email='peter.loecker@live.at',
    url="https://github.com/PeterBrain/fronius-pv-boiler",
    packages=find_packages(exclude=('tests', 'docs')),
    #install_requires=[]
)
