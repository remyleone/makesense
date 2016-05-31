#!/bin/sh

(cd chaine_high_calibration; make TARGET=sky clean)
(cd chaine_medium_calibration; make TARGET=sky clean)
(cd chaine_low_calibration; make TARGET=sky clean)
(cd chaine_high; make TARGET=sky clean)
(cd chaine_medium; make TARGET=sky clean)
(cd chaine_low; make TARGET=sky clean)

(cd chaine_high_calibration; make TARGET=wismote clean)
(cd chaine_medium_calibration; make TARGET=wismote clean)
(cd chaine_low_calibration; make TARGET=wismote clean)
(cd chaine_high; make TARGET=wismote clean)
(cd chaine_medium; make TARGET=wismote clean)
(cd chaine_low; make TARGET=wismote clean)

(cd chaine_high_calibration; make TARGET=native clean)
(cd chaine_medium_calibration; make TARGET=native clean)
(cd chaine_low_calibration; make TARGET=native clean)
(cd chaine_high; make TARGET=native clean)
(cd chaine_medium; make TARGET=native clean)
(cd chaine_low; make TARGET=native clean)
