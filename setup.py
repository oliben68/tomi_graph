from setuptools import setup

setup(
    name='hopla',
    version='0.0.1',
    packages=['hopla',
              'hopla.documents',
              'hopla.documents.core',
              'hopla.documents.schema_based',
              'hopla.events',
              'hopla.logging',
              'hopla.model',
              'hopla.model.config',
              'hopla.model.core', ],
    url='',
    license='',
    author='Olivier Steck',
    author_email='osteck@gmail.com',
    description='Headless CMS',
    install_requires=['PyDispatcher',
                      'chardet',
                      'jsonschema',
                      'neo4j',
                      'ujson', ]
)
