Makesense organization
======================

This page is a little description of the organization of makesense.

- docs/ is where all the documentation is stored
- fabfile.py is the fabric command file. This is were the command line tool fab is going to 
  fetch the code it needs
- makesense/ is the folder countaining most of the function doing the work. It's organized as a python
  package to be able to share variables easily
- templates/ this is where all the templates used during the making of source code are stored.

.. code-block:: shell

   makesense
   ├── AUTHORS.rst
   ├── CONTRIBUTING.rst
   ├── docs
   │   ├── campaign.rst
   │   ├── conf.py
   │   ├── example_fabfile.py
   │   ├── example_firmware.c
   │   ├── example_makefile
   │   ├── index.rst
   │   ├── installation.rst
   │   ├── iotlab.rst
   │   ├── Makefile
   │   ├── quickstart.rst
   │   ├── README
   │   └── remote.rst
   ├── fabfile.py
   ├── LICENSE
   ├── makesense
   │   ├── analyze.py
   │   ├── bootstrap.py
   │   ├── graph.py
   │   ├── __init__.py
   │   ├── make.py
   │   ├── parser.py
   │   ├── plot.py
   │   ├── report.py
   │   ├── run.py
   │   ├── sampling.py
   │   ├── traffic.py
   │   └── utils.py
   ├── README.md
   ├── requirements.txt
   └── templates
       ├── dummy_client.c
       ├── dummy_main.csc
       ├── dummy_makefile
       ├── dummy_script.js
       ├── dummy_server.c
       ├── exp.json
       ├── lambda_bootstrap.js
       ├── readme.md
       └── report.html
