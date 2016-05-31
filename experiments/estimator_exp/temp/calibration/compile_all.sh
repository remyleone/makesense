#!/bin/sh

(cd contikimac; make TARGET=sky nodes)
(cd nullmac; make TARGET=sky nodes)
(cd contikimac; make TARGET=wismote nodes)
(cd nullmac; make TARGET=wismote nodes)
