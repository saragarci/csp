from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='CSP',
    version='0.1.0',
    description='Solving Constraint Satisfaction Problems',
    long_description=readme,
    author='Sara Garci',
    author_email='s@saragarci.com',
    url='https://github.com/saragarci/csp',
    license=license,
    packages=find_packages(exclude=('tests'))
)
