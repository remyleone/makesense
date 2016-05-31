#!/bin/sh

(cd fleur_high_calibration; make run)
(cd fleur_medium_calibration; make run)
(cd fleur_low_calibration; make run)
(cd fleur_high; make run)
(cd fleur_medium; make run)
(cd fleur_low; make run)