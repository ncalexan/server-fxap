.. fxap documentation master file, created by
   sphinx-quickstart on Thu Dec  6 09:31:34 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to fxap's documentation!
================================

Contents:

.. toctree::
   :maxdepth: 2

.. services::
   :modules: fxap.views

To prepare development environment and run the server:

virtualenv --no-site-packages .

./bin/python setup.py develop

./bin/paster serve fxap.ini

To generate documentation:

./bin/pip install Sphinx

make -C docs html

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

