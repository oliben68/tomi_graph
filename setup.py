from setuptools import setup

setup(
    name='hopla',
    version='0.0.1',
    packages=['hopla',
              'hopla.core',
              'hopla.core.events',
              'hopla.documents',
              'hopla.documents.schema_based',
              'hopla.logging'],
    url='',
    license='',
    author='Olivier Steck',
    author_email='osteck@gmail.com',
    description='Headless CMS', install_requires=['ujson', 'chardet', 'jsonschema', 'PyDispatcher']
)
