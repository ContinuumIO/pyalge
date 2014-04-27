from distutils.core import setup, Extension

ext_alge = Extension(name="_alge",
                     sources=["_alge.c"])

setup(name='pyalge',
      description="Pattern matching and Algebraic data types",
      version="0.1",
      classifiers=[
          "Development Status :: 2 - Pre-Alpha",
          "Intended Audience :: Developers",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.6",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3.3",
          "Topic :: Utilities",
      ],
      author="Continuum Analytics, Inc.",
      ext_modules=[ext_alge],
      py_modules=['alge', "_alge"],
      license="BSD", )
