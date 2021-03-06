"""Distribution script for Pedlar client API."""
import setuptools


with open("README.md", 'r') as fh:
  long_description = fh.read()

setuptools.setup(
  name="icalgosocdemo",
  version='0.0.11',
  author="thomas",
  author_email="thomaswong2022@users.noreply.github.com",
  description="Imperial Algorithmic Trading Soceity Demo",
  long_description=long_description,
  long_description_content_type="text/markdown",
  url="https://github.com/ThomasWong2022/pedlar_demo/",
  packages=["icalgodemo"],
  include_package_data=True,
  classifiers=[
    "Development Status :: 3 - Alpha",
    "License :: OSI Approved :: Apache Software License",
    "Natural Language :: English",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3 :: Only",
    "Topic :: Office/Business :: Financial",
  ],
  install_requires=[
    'requests',
    'pandas',
    'matplotlib',
    'zeromq',
    'protobuf',
    'websocket',
    'socketIO_client_nexus'
  ]
)
