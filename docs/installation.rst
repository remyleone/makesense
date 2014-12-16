Installation
=============

.. _git: http://git-scm.com/
.. _fabric: http://www.fabfile.org/
.. _networkx: https://networkx.github.io/
.. _pandas: http://pandas.pydata.org
.. _matplotlib: http://matplotlib.org/
.. _jinja2: http://jinja.pocoo.org/

Makesense could be set up very easily. It uses git_ to manage it source code. To get started do the following commands:


.. code-block:: bash

    git clone https://github.com/sieben/makesense.git

Dependencies installation
-------------------------

Makesense leverages several Python libraries such as :

- fabric_ for launching command from the command lines
- networkx_ for network topology graph analysis
- pandas_ for managing large datasets
- matplotlib_ for plotting
- jinja2_ for templating

Once you have all the content you should get started by installing all python dependencies.
If you have pip installer you can install of them in one hit by using this command:

.. code-block:: bash

    pip install requirements.txt

If you prefer to have your python dependencies managed by your package manager on
ubuntu for instance you can have :

.. code-block:: bash

    sudo apt-get install fabric python-networkx python-pandas python-matplotlib python-jinja2