from distutils.core import setup

setup(
    name='Apache Open Climate Workbench',
    version='0.3-incubating-dev',
    url='http://climate.incubator.apache.org/index.html',
    author='Apache Open Climate Workbench',
    author_email='dev@climate.incubator.apache.org',
    packages=['ocw', 'ocw.data_source', 'ocw.tests'],
    license='Apache License, Version 2.0',
    long_description='The Apache Open Climate Workbench provides tools for the evaluation and analysis of climate models.'
)
