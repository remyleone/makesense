How to make a campaign of simulation?
=====================================

A campaign of simulation usually involve making a variable change through
several run or several nodes.

Makesense leverages Jinja2 to create very easily as many firmware as necessary
by using templating. Instead of writing a C code directly we will write C code
replacing the variables and function by templates variables that jinja2 will
remplace by variables existing in a python code. By doing so we can for
instance create very easily a loop iterating through a list of desired values
for a variable and let makesense handle all the trouble of creating those
files, compile them and deploy them on a testbed.


Step 1: Creating a C template
-----------------------------

First we will create a simple C code that print a message through a loop.

.. literalinclude:: example_firmware.c
   :language: c 
   :emphasize-lines: 4,22

.. code-block:: c

   static int my_value = {{ my_value }};

It's at this place that jinja2 will put the *my_value* variable. For more
information check out the Jinja2 documentation.

This makefile will compile all the nodes.

.. literalinclude:: example_makefile
   :language: Makefile
   :emphasize-lines: 5,6

Step 2: Let's loop
------------------

Suppose that you want to create firmware for 42 different values we would do
it in the fabfile:

.. literalinclude:: example_fabfile.py
   :language: python
   :emphasize-lines: 23-25

Then we would call this function like any other fabric function

.. code-block:: bash

    fab my_special_function:dummy

You should have files like:

- dummy_1.iotlab-m3
- ...
- dummy_42.iotlab-m3

created in experiments/dummy

You should also have an iotlab.json looking like:

.. code-block:: json

   [
       {
           "firmware_path": "/home/sieben/Dropbox/workspace/makesense/experiments/prout/dummy_1.iotlab-m3",
           "nodes": [
               "m3-1.grenoble.iot-lab.info"
           ]
       },
       ...
   ]

Step 3: Push to iotlab
----------------------

Then we simply have to push to iotlab:

.. code-block:: bash

    fab push_iotlab:dummy
