.. makesense documentation master file, created by
   sphinx-quickstart on Mon Sep  2 16:08:11 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to makesense's documentation!
=====================================

Makesense is a tool that can create, run and analyze WSN experiment. It's
designed to be modular.


.. code-block:: bash

    fab new:foobar  # Will create a foobar experiment
    fab make:foobar  # Will compile all nodes and simulations tools
    fab launch:foobar  # Will run the experiment
    fab analyze:foobar  # Will launch all analysis scripts
    fab plot:foobar   # Will plot all the graphes


User Guide
----------

This part of the documentation, which is mostly prose, begins with some
background information about makesense, then focuses on step-by-step
instructions for getting the most out of it.

.. toctree::
   :maxdepth: 2

   installation
   quickstart
   folder
   iotlab
   remote
   campaign


.. toctree::
   :maxdepth: 2



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
