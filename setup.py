from setuptools import setup, find_packages

with open('README.md') as file:
    long_description = file.read()


setup(
    name='pyants',
    version='0.3.0',
    description='Allow you to create you own custom decentralize job management system.',
    url='https://github.com/hvuhsg/ants',
    author='Yehoyada.s',
    author_email='hvuhsg6@gmail.com',
    license='GPLv3',
    packages=find_packages(),
    keywords=['decentralize', 'job', 'jobs', 'job management'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    long_description=long_description,
    long_description_content_type='text/markdown',
)
