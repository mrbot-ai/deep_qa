"""
In order to create a package for pypi, you need to follow several steps.

1. Create a .pypirc in your home directory. It should look like this:

```
[distutils]
index-servers =
  pypi
  pypitest

[pypi]
repository=https://pypi.python.org/pypi
username=deep-qa
password= Get the password from LastPass.

[pypitest]
repository=https://testpypi.python.org/pypi
username=deep-qa
password= Get the password from LastPass.
```
run chmod 600 ./pypirc so only you can read/write.


2. Update the RELEASE.md with the new features, bug fixes and api changes provided in this release.

3. Change the version in docs/conf.py and setup.py.

4. Commit these changes with the message: "Release: VERSION"

5. Add a tag in git to mark the release: "git tag VERSION -m'Adds tag VERSION for pypi' "
   Push the tag to git: git push --tags origin master

6. Build both the sources and the wheel. Do not change anything in setup.py between
   creating the wheel and the source distribution (obviously).

   For the wheel, run: "python setup.py bdist_wheel" in the top level deep_qa directory.
   (this will build a wheel for the python version you use to build it - make sure you use python 3.x).

   For the sources, run: "python setup.py sdist"
   You should now have a /dist directory with both .whl and .tar.gz source versions of deep_qa.

7. Check that everything looks correct by uploading the package to the pypi test server:

   twine upload dist/* -r pypitest
   (pypi suggest using twine as other methods upload files via plaintext.)

   Check that you can install it in a virtualenv by running:
   pip install -i https://testpypi.python.org/pypi deep_qa

8. Upload the final version to actual pypi:
   twine upload dist/* -r pypi

9. Copy the release notes from RELEASE.md to the tag in github once everything is looking hunky-dory.

"""

from setuptools import setup, find_packages
try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except(IOError, ImportError):
    long_description = open('README.md').read()

setup(name='deep_qa',
      version='0.1.1',
      description='Using deep learning to answer Aristo\'s science questions',
      long_description=long_description,
      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: Apache Software License',
          'Programming Language :: Python :: 3.5',
          'Topic :: Scientific/Engineering :: Artificial Intelligence',
      ],
      keywords='deep_qa NLP deep learning machine reading',
      url='https://github.com/allenai/deep_qa',
      author='Matt Gardner',
      author_email='deep-qa@allenai.org',
      license='Apache',
      packages=find_packages(),
      install_requires=[
          'keras==2.0.3',
          'h5py',
          'scikit-learn',
          'grpcio',
          'grpcio-tools',
          'pyhocon',
          'dill',
          'typing',
          'numpy',
          'matplotlib',
          'spacy',
          'nltk',
          'overrides'
      ],
      setup_requires=['pytest-runner'],
      tests_require=['pytest'],
      include_package_data=True,
      zip_safe=False)
