#!/bin/sh

(cd chaine_high_calibration; make run)
(cd chaine_medium_calibration; make run)
(cd chaine_low_calibration; make run)
(cd chaine_high; make run)
(cd chaine_medium; make run)
(cd chaine_low; make run)