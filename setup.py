from distutils.core import setup
setup(name='parsemis',
      version='1.0',
      description="A simple wrapper for ParSeMiS",
      author="Tom Dickinson",
      author_email="tomkdickinson@gmail.com",
      py_modules=['parsemis'],
      data_files=[('.', ['parsemis.jar'])]
      )
