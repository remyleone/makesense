#!/bin/sh

(cd fleur_high_calibration; make TARGET=sky nodes)
(cd fleur_medium_calibration; make TARGET=sky nodes)
(cd fleur_low_calibration; make TARGET=sky nodes)
(cd fleur_high; make TARGET=sky nodes)
(cd fleur_medium; make TARGET=sky nodes)
(cd fleur_low; make TARGET=sky nodes)

(cd fleur_high_calibration; make TARGET=wismote nodes)
(cd fleur_medium_calibration; make TARGET=wismote nodes)
(cd fleur_low_calibration; make TARGET=wismote nodes)
(cd fleur_high; make TARGET=wismote nodes)
(cd fleur_medium; make TARGET=wismote nodes)
(cd fleur_low; make TARGET=wismote nodes)
