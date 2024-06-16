"""python module setup"""
from setuptools import setup, find_packages
import boilr

with open('README.md', encoding="utf-8") as f:
    readme = f.read()

setup(
    name='boilr',
    version=boilr.__version__,
    description='Water boiler automation with a Fronius pv inverter on a Raspberry Pi.',
    license='MIT',
    long_description=readme,
    author='Peter Loecker',
    author_email='peter.loecker@live.at',
    url="https://github.com/PeterBrain/boilr",
    packages=find_packages(exclude=('tests', 'docs')),
    keywords="boiler,pv,photovoltaic,solar,solar-energy,fronius-solar-api,fronius,fronius-inverter,ohmpilot,waterheater,raspberry-pi,raspberrypi",
    install_requires=[
        'certifi',
        'charset-normalizer',
        'docutils',
        'idna',
        'lockfile',
        'python-daemon',
        'PyYAML',
        'requests',
        'RPi.GPIO',
        'urllib3'
    ]
)
