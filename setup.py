from setuptools import setup, find_packages

with open('README.md') as file:
    long_description = file.read()


setup(
      name='pyants',
      version='0.1.0',
      description='Allow you to create you own custom decentralize job management system.',
      url='https://github.com/hvushg/ants',
      author='Yehoyada.s',
      author_email='hvuhsg6@gmail.com',
      license='GPLv3',
      packages=find_packages(),
      keywords=['decentralize', 'job', 'jobs', 'job management'],
      classifiers=[
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
            'Natural Language :: English',
      ],
      long_description=long_description,
      long_description_content_type='text/markdown',
)
