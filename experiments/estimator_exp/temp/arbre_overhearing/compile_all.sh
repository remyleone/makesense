#!/bin/sh

(cd arbre_high_calibration; make TARGET=sky nodes)
(cd arbre_medium_calibration; make TARGET=sky nodes)
(cd arbre_low_calibration; make TARGET=sky nodes)
(cd arbre_high; make TARGET=sky nodes)
(cd arbre_medium; make TARGET=sky nodes)
(cd arbre_low; make TARGET=sky nodes)

(cd arbre_high_calibration; make TARGET=wismote nodes)
(cd arbre_medium_calibration; make TARGET=wismote nodes)
(cd arbre_low_calibration; make TARGET=wismote nodes)
(cd arbre_high; make TARGET=wismote nodes)
(cd arbre_medium; make TARGET=wismote nodes)
(cd arbre_low; make TARGET=wismote nodes)
