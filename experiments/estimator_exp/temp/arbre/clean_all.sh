#!/bin/sh

(cd arbre_high_calibration; make TARGET=sky clean)
(cd arbre_medium_calibration; make TARGET=sky clean)
(cd arbre_low_calibration; make TARGET=sky clean)
(cd arbre_high; make TARGET=sky clean)
(cd arbre_medium; make TARGET=sky clean)
(cd arbre_low; make TARGET=sky clean)

(cd arbre_high_calibration; make TARGET=wismote clean)
(cd arbre_medium_calibration; make TARGET=wismote clean)
(cd arbre_low_calibration; make TARGET=wismote clean)
(cd arbre_high; make TARGET=wismote clean)
(cd arbre_medium; make TARGET=wismote clean)
(cd arbre_low; make TARGET=wismote clean)

(cd arbre_high_calibration; make TARGET=native clean)
(cd arbre_medium_calibration; make TARGET=native clean)
(cd arbre_low_calibration; make TARGET=native clean)
(cd arbre_high; make TARGET=native clean)
(cd arbre_medium; make TARGET=native clean)
(cd arbre_low; make TARGET=native clean)
