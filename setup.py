import setuptools
from distutils.core import setup

setup(name='pyflwor',
      version='1.1',
      description=(
        'A object query system for arbitrary python objects..'
      ),
      author='Tim Henderson',
      author_email='tim.tadh@gmail.com',
      url='https://www.github.com/timtadh/pyflwor',
      license='BSD',
      packages=['pyflwor'],
      install_requires=['ply',
                        'future']
)

