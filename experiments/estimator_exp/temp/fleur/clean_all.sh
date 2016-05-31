#!/bin/sh

(cd fleur_high_calibration; make TARGET=sky clean)
(cd fleur_medium_calibration; make TARGET=sky clean)
(cd fleur_low_calibration; make TARGET=sky clean)
(cd fleur_high; make TARGET=sky clean)
(cd fleur_medium; make TARGET=sky clean)
(cd fleur_low; make TARGET=sky clean)

(cd fleur_high_calibration; make TARGET=wismote clean)
(cd fleur_medium_calibration; make TARGET=wismote clean)
(cd fleur_low_calibration; make TARGET=wismote clean)
(cd fleur_high; make TARGET=wismote clean)
(cd fleur_medium; make TARGET=wismote clean)
(cd fleur_low; make TARGET=wismote clean)

(cd fleur_high_calibration; make TARGET=native clean)
(cd fleur_medium_calibration; make TARGET=native clean)
(cd fleur_low_calibration; make TARGET=native clean)
(cd fleur_high; make TARGET=native clean)
(cd fleur_medium; make TARGET=native clean)
(cd fleur_low; make TARGET=native clean)
