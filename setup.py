from setuptools import setup

requirements = ['rarfile==4.0', 'tqdm==4.56.0', 'replit==1.2.11', 'typing-extensions==3.7.4.3']

setup(name="canvasgrader",
      version="1.0.2",
      author="davidliyutong",
      keywords=("canvas", "grader"),
      author_email="davidliyutong@sjtu.edu.cn",
      description="Toolkit to grade C/C++ canvas submissions",
      license="MIT Licence",
      packages=["canvasgrader", "canvasgrader/components"],
      python_requires=">=3.6",
      install_requires=requirements,
      entrypoints={'console_scripts': ['canvasgrader = canvasgrader.app:main']})
