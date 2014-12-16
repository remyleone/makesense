
import os
import json
from os.path import join as pj

from fabric.api import task
from jinja2 import Environment, FileSystemLoader

ROOT_DIR = os.path.dirname(__file__)
EXPERIMENT_FOLDER = pj(ROOT_DIR, "experiments")
TEMPLATE_FOLDER = pj(ROOT_DIR, "templates")
TEMPLATE_ENV = Environment(loader=FileSystemLoader(TEMPLATE_FOLDER))

@task
def my_special_function(name):
    """ This function will create 42 C files. """
    path = pj(EXPERIMENT_FOLDER, name)
    if not os.path.exists(path):
        os.makedirs(path)

    c_template = TEMPLATE_ENV.get_template("dummy_template.c")
    for value in range(1, 43):
        with open(pj(path, "dummy_%d.c" % value), "w") as f:
            f.write(c_template.render(my_value=value))

    makefile_template = TEMPLATE_ENV.get_template("dummy_makefile")
    with open(pj(path, "Makefile"), "w") as f:
        f.write(makefile_template.render(contiki=CONTIKI_FOLDER,
                                             target="iotlab-m3"))

    config_template = TEMPLATE_ENV.get_template("dummy_iotlab.json")
    res = [
        {"nodes": ["m3-%d.grenoble.iot-lab.info" % num],
         "firmware_path": pj(path, "dummy_%d.iotlab-m3" % num)
       } for num in range(1, 43)]
    with open(pj(path, "iotlab.json"), "w") as f:
        f.write(json.dumps(res, sort_keys=True,
                  indent=4, separators=(',', ': ')))