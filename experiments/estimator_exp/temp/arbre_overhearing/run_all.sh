#!/bin/sh

(cd arbre_high_calibration; make run)
(cd arbre_medium_calibration; make run)
(cd arbre_low_calibration; make run)
(cd arbre_high; make run)
(cd arbre_medium; make run)
(cd arbre_low; make run)
