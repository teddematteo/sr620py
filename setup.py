from setuptools import find_packages, setup

setup(
    name='sr620py',
    packages=find_packages(include=['sr620py']),
    version='0.1.0',
    description='SR620 Universal Time Counter Python Library',
    author='Matteo Tedde (Lab3841 s.r.l.)',
    install_requires=['pyserial','tqdm']
)