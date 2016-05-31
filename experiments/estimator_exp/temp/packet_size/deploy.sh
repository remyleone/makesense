#!/bin/sh

cat project-conf-contikimac.h | sed -e "\$a#define SIZE 10" > contikimac/10/project-conf.h
cat project-conf-contikimac.h | sed -e "\$a#define SIZE 20" > contikimac/20/project-conf.h
cat project-conf-contikimac.h | sed -e "\$a#define SIZE 30" > contikimac/30/project-conf.h
cat project-conf-contikimac.h | sed -e "\$a#define SIZE 40" > contikimac/40/project-conf.h
cat project-conf-contikimac.h | sed -e "\$a#define SIZE 50" > contikimac/50/project-conf.h


cat project-conf-nullmac.h | sed -e "\$a#define SIZE 10" > nullmac/10/project-conf.h
cat project-conf-nullmac.h | sed -e "\$a#define SIZE 20" > nullmac/20/project-conf.h
cat project-conf-nullmac.h | sed -e "\$a#define SIZE 30" > nullmac/30/project-conf.h
cat project-conf-nullmac.h | sed -e "\$a#define SIZE 40" > nullmac/40/project-conf.h
cat project-conf-nullmac.h | sed -e "\$a#define SIZE 50" > nullmac/50/project-conf.h