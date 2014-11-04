#coding: utf-8

"""
Report module
"""

import logging

from .settings import TEMPLATE_ENV, PJ
from . import Step


class Report(Step):
    """
    Creating HTML report from all data gathered
    """

    def __init__(self, name):
        log = logging.getLogger("report")
        Step.__init__(self, name)
        self.load_settings()
        for result_folder in self.result_folders:
            log.info(self.settings["title"])

            html_template = TEMPLATE_ENV.get_template("report.html")
            reports_metadata = {
                "title": self.settings["title"]
            }
            rendered_report = html_template.render(reports_metadata)
            html_report = PJ(result_folder, "index.html")
            with open(html_report, "w") as report_file:
                report_file.write(rendered_report)
            log.info("[COOJA mote log] " + PJ(
                result_folder, "COOJA.testlog"))
            log.info("[COOJA log] " + PJ(
                result_folder, "COOJA.log"))
