Remote server
=============

There is several tricks and nice features to know when dealing
with ssh and remote servers.

Let's suppose that you want to access the grenoble server through ssh.
It would be really easy to type just ssh grenoble for instance and get
it working. Good news, ssh can do that! Just write in your ~/.ssh/config
the following snippet:

.. code-block:: bash

    Host grenoble
    HostName grenoble.iot-lab.info
    User leone

Don't forget to replace leone with your real user name ;-)
Then simply do a ssh-copy-id grenoble enter your password and
you are all set!

Next you can connect to the server in Grenoble by simply typing
ssh grenoble.

An other feature is that it allows to simplify the fabric file. For instance
let's suppose that you want to download all the content of a precise folder on
your local machine. You can use snippet in your fabric file such as:

.. code-block:: python

    from fabric.api import env
    env.use_ssh_config = True

    @task
    @hosts("grenoble")
    def push(name):
        path = pj(EXPERIMENT_FOLDER, name)
        put(path,
            remote_path="~/html/results/")

For more information just check the  `fabric documentation
<http://docs.fabfile.org/en/latest/api/core/operations.html/>`_
