makesense (Managing Reproducible WSNs Experiments)
==================================================

makesense is a high-level framework for automating scientific
experiments. Thanks for checking it out.

All documentation is in the "docs" directory and online at

-  First, read docs/installation.txt for instructions on installing
   makesense.

Installation
------------

1. Download the repository. If you have git installed type the following
   command :

   git clone git@github.com:sieben/makesense.git

2. Download Contiki from the following address to the root of the
   previously downloaded repository: https://contiki-os.org

3. Install all the system dependencies. If you are using ubuntu you can
   use the .travis.yml file as a way to help you.

4. Install the python dependencies by using:

   pip install requierements.txt

Getting started
---------------

-  Launch an experiments by using for instance:

   fab hello:run\_all

This will run the experiment hello with all the defined tasks in the
exp.json

Code status
-----------

|Requirements Status|

|Build Status|

Licence
-------

makesense is released under the `Apache
License <//choosealicense.com/licenses/apache-2.0/>`__.

.. |Requirements Status| image:: //requires.io/github/sieben/makesense/requirements.png?branch=master
   :target: //requires.io/github/sieben/makesense/requirements/?branch=master
.. |Build Status| image:: //secure.travis-ci.org/sieben/makesense.png
   :target: //travis-ci.org/sieben/makesense
