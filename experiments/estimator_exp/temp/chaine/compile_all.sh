#!/bin/sh

(cd chaine_high_calibration; make TARGET=sky nodes)
(cd chaine_medium_calibration; make TARGET=sky nodes)
(cd chaine_low_calibration; make TARGET=sky nodes)
(cd chaine_high; make TARGET=sky nodes)
(cd chaine_medium; make TARGET=sky nodes)
(cd chaine_low; make TARGET=sky nodes)

(cd chaine_high_calibration; make TARGET=wismote nodes)
(cd chaine_medium_calibration; make TARGET=wismote nodes)
(cd chaine_low_calibration; make TARGET=wismote nodes)
(cd chaine_high; make TARGET=wismote nodes)
(cd chaine_medium; make TARGET=wismote nodes)
(cd chaine_low; make TARGET=wismote nodes)
