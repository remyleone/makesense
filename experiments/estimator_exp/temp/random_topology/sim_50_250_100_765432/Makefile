TARGET=sky
CONTIKI=$(HOME)/code//contiki

run:
	java -jar $(CONTIKI)/tools/cooja/dist/cooja.jar -nogui=main.csc -contiki=$(CONTIKI)

cooja:
	make TARGET=cooja main.csc


include $(CONTIKI)/Makefile.include