Iotlab
======

Makesense can perform and deploy code to the iotlab infrastructure.


Let's suppose that you have in your .ssh/config the following

.. code-block:: bash

    Host grenoble
    HostName grenoble.iot-lab.info
    User leone


The you can use commands such as :

    fab push_iotlab:dummy # Will launch a experiment 
    fab pull_iotlab:dummy # Will fetch the results of an experiment done on iotlab