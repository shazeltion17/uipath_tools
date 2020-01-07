from setuptools import setup, find_packages, Extension

setup(name='uipath_tools',
      version='0.4',
      url='https://github.com/shazeltion17/uipath_tools',
      license='MIT',
      author='Samuel Ehrlich',
      author_email='samuel.ehrlich@fireanalytics.tech',
      description='This is a wrapper for the UiPath orchestrator API',
      packages=find_packages(exclude=['tests']),
      zip_safe=False)
