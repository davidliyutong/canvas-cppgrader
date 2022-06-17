from setuptools import setup

requirements = ['rarfile==4.0', 'tqdm==4.56.0', 'replit==1.2.11', 'typing-extensions==3.7.4.3','coloredlogs==15.0.1']

setup(name="canvas-cppgrader",
      version="1.1.2",
      author="davidliyutong",
      keywords=["canvas", "grader", "cpp"],
      author_email="davidliyutong@sjtu.edu.cn",
      description="A toolkit to grade C/C++ submissions from canvas",
      long_description=open('README.rst').read(),
      license="MIT Licence",
      packages=["cppgrader", "cppgrader/components", "cppgrader/tools", "cppgrader/tools/antiplag"],
      python_requires=">=3.6",
      install_requires=requirements,
      entrypoints={'console_scripts': ['cppgrader = cppgrader.app:main']})
