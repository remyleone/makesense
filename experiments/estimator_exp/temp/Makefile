CONTIKI=$(HOME)/workspace/contiki

nodes: udp-server udp-client

delete_firmware:
	find . -name "*.native" -exec rm {} \;
	find . -name "*.sky" -exec rm {} \;
	find . -name "*.wismote" -exec rm {} \;

run:
	java -mx512m -jar $(CONTIKI)/tools/cooja/dist/cooja.jar -nogui=main.csc -contiki=$(CONTIKI)

#diff_time:
#	cat serial.log| ack-grep "Client sending|Server received" | cut -d' ' -f1 > diff_time.log'

sender_tx:
	tshark -r output.pcap > pcap.log; ./sender_tx.py

compile_all:
	(cd arbre; ./compile_parallel.sh)
	(cd arbre_overhearing; ./compile_parallel.sh)
	(cd chaine; ./compile_parallel.sh)
	(cd fleur; ./compile_parallel.sh)

run_all:
	(cd arbre; ./run_parallel.sh)
	(cd arbre_overhearing; ./run_parallel.sh)
	(cd chaine; ./run_parallel.sh)
	(cd fleur; ./run_parallel.sh)

cooja:
	make TARGET=cooja main.csc

deploy_all: deploy_flower deploy_chaine deploy_arbre deploy_calibration

deploy_flower:
	@echo Deploy project-conf to flower
	cp project-conf-high-calibration.h fleur/fleur_high_calibration/project-conf.h
	cp project-conf-high.h fleur/fleur_high/project-conf.h
	cp project-conf-low-calibration.h fleur/fleur_low_calibration/project-conf.h
	cp project-conf-low.h fleur/fleur_low/project-conf.h
	cp project-conf-medium-calibration.h fleur/fleur_medium_calibration/project-conf.h
	cp project-conf-medium.h fleur/fleur_medium/project-conf.h

	cp udp-client.c udp-server.c fleur/fleur_high/
	cp udp-client.c udp-server.c fleur/fleur_high_calibration/
	cp udp-client.c udp-server.c fleur/fleur_low/
	cp udp-client.c udp-server.c fleur/fleur_low_calibration/
	cp udp-client.c udp-server.c fleur/fleur_medium/
	cp udp-client.c udp-server.c fleur/fleur_medium_calibration/

deploy_chaine:
	@echo Deploy project-conf to chaine

	cp project-conf-high-calibration.h chaine/chaine_high_calibration/project-conf.h
	cp project-conf-high.h chaine/chaine_high/project-conf.h
	cp project-conf-low-calibration.h chaine/chaine_low_calibration/project-conf.h
	cp project-conf-low.h chaine/chaine_low/project-conf.h
	cp project-conf-medium-calibration.h chaine/chaine_medium_calibration/project-conf.h
	cp project-conf-medium.h chaine/chaine_medium/project-conf.h

	cp udp-client.c udp-server.c chaine/chaine_high/
	cp udp-client.c udp-server.c chaine/chaine_high_calibration/
	cp udp-client.c udp-server.c chaine/chaine_low/
	cp udp-client.c udp-server.c chaine/chaine_low_calibration/
	cp udp-client.c udp-server.c chaine/chaine_medium/
	cp udp-client.c udp-server.c chaine/chaine_medium_calibration/

deploy_arbre:
	@echo Deploy project-conf to arbre

	cp project-conf-high-calibration.h arbre_overhearing/arbre_high_calibration/project-conf.h
	cp project-conf-high.h arbre_overhearing/arbre_high/project-conf.h
	cp project-conf-low-calibration.h arbre_overhearing/arbre_low_calibration/project-conf.h
	cp project-conf-low.h arbre_overhearing/arbre_low/project-conf.h
	cp project-conf-medium-calibration.h arbre_overhearing/arbre_medium_calibration/project-conf.h
	cp project-conf-medium.h arbre_overhearing/arbre_medium/project-conf.h

	cp udp-client.c udp-server.c arbre_overhearing/arbre_high/
	cp udp-client.c udp-server.c arbre_overhearing/arbre_high_calibration/
	cp udp-client.c udp-server.c arbre_overhearing/arbre_low/
	cp udp-client.c udp-server.c arbre_overhearing/arbre_low_calibration/
	cp udp-client.c udp-server.c arbre_overhearing/arbre_medium/
	cp udp-client.c udp-server.c arbre_overhearing/arbre_medium_calibration/

	cp project-conf-high-calibration.h arbre/arbre_high_calibration/project-conf.h
	cp project-conf-high.h arbre/arbre_high/project-conf.h
	cp project-conf-low-calibration.h arbre/arbre_low_calibration/project-conf.h
	cp project-conf-low.h arbre/arbre_low/project-conf.h
	cp project-conf-medium-calibration.h arbre/arbre_medium_calibration/project-conf.h
	cp project-conf-medium.h arbre/arbre_medium/project-conf.h

	cp udp-client.c udp-server.c arbre/arbre_high/
	cp udp-client.c udp-server.c arbre/arbre_high_calibration/
	cp udp-client.c udp-server.c arbre/arbre_low/
	cp udp-client.c udp-server.c arbre/arbre_low_calibration/
	cp udp-client.c udp-server.c arbre/arbre_medium/
	cp udp-client.c udp-server.c arbre/arbre_medium_calibration/

deploy_web:
	markdown index.md > arbre/arbre_high/index.html
	markdown index.md > arbre/arbre_high_calibration/index.html
	markdown index.md > arbre/arbre_low/index.html
	markdown index.md > arbre/arbre_low_calibration/index.html
	markdown index.md > arbre/arbre_medium/index.html
	markdown index.md > arbre/arbre_medium_calibration/index.html

	markdown index.md > arbre_overhearing/arbre_high/index.html
	markdown index.md > arbre_overhearing/arbre_high_calibration/index.html
	markdown index.md > arbre_overhearing/arbre_low/index.html
	markdown index.md > arbre_overhearing/arbre_low_calibration/index.html
	markdown index.md > arbre_overhearing/arbre_medium/index.html
	markdown index.md > arbre_overhearing/arbre_medium_calibration/index.html

	markdown index.md > fleur/fleur_high/index.html
	markdown index.md > fleur/fleur_high_calibration/index.html
	markdown index.md > fleur/fleur_low/index.html
	markdown index.md > fleur/fleur_low_calibration/index.html
	markdown index.md > fleur/fleur_medium/index.html
	markdown index.md > fleur/fleur_medium_calibration/index.html

	markdown index.md > chaine/chaine_high/index.html
	markdown index.md > chaine/chaine_high_calibration/index.html
	markdown index.md > chaine/chaine_low/index.html
	markdown index.md > chaine/chaine_low_calibration/index.html
	markdown index.md > chaine/chaine_medium/index.html
	markdown index.md > chaine/chaine_medium_calibration/index.html

fetch_results_from_enst:
	scp enst:~/results_estimators/arbre/arbre_high/serial.log ~/Dropbox/results_estimators/arbre/arbre_high/serial.log
	scp enst:~/results_estimators/arbre/arbre_high/powertracker.log ~/Dropbox/results_estimators/arbre/arbre_high/powertracker.log
	scp enst:~/results_estimators/arbre/arbre_high_calibration/serial.log ~/Dropbox/results_estimators/arbre/arbre_high_calibration/serial.log
	scp enst:~/results_estimators/arbre/arbre_high_calibration/powertracker.log ~/Dropbox/results_estimators/arbre/arbre_high_calibration/powertracker.log
	scp enst:~/results_estimators/arbre/arbre_low/serial.log ~/Dropbox/results_estimators/arbre/arbre_low/serial.log
	scp enst:~/results_estimators/arbre/arbre_low/powertracker.log ~/Dropbox/results_estimators/arbre/arbre_low/powertracker.log
	scp enst:~/results_estimators/arbre/arbre_low_calibration/serial.log ~/Dropbox/results_estimators/arbre/arbre_low_calibration/serial.log
	scp enst:~/results_estimators/arbre/arbre_low_calibration/powertracker.log ~/Dropbox/results_estimators/arbre/arbre_low_calibration/powertracker.log
	scp enst:~/results_estimators/arbre/arbre_medium/serial.log ~/Dropbox/results_estimators/arbre/arbre_medium/serial.log
	scp enst:~/results_estimators/arbre/arbre_medium/powertracker.log ~/Dropbox/results_estimators/arbre/arbre_medium/powertracker.log
	scp enst:~/results_estimators/arbre/arbre_medium_calibration/serial.log ~/Dropbox/results_estimators/arbre/arbre_medium_calibration/serial.log
	scp enst:~/results_estimators/arbre/arbre_medium_calibration/powertracker.log ~/Dropbox/results_estimators/arbre/arbre_medium_calibration/powertracker.log

	scp enst:~/results_estimators/arbre_overhearing/arbre_high/serial.log ~/Dropbox/results_estimators/arbre_overhearing/arbre_high/serial.log
	scp enst:~/results_estimators/arbre_overhearing/arbre_high/powertracker.log ~/Dropbox/results_estimators/arbre_overhearing/arbre_high/powertracker.log
	scp enst:~/results_estimators/arbre_overhearing/arbre_high_calibration/serial.log ~/Dropbox/results_estimators/arbre_overhearing/arbre_high_calibration/serial.log
	scp enst:~/results_estimators/arbre_overhearing/arbre_high_calibration/powertracker.log ~/Dropbox/results_estimators/arbre_overhearing/arbre_high_calibration/powertracker.log
	scp enst:~/results_estimators/arbre_overhearing/arbre_low/serial.log ~/Dropbox/results_estimators/arbre_overhearing/arbre_low/serial.log
	scp enst:~/results_estimators/arbre_overhearing/arbre_low/powertracker.log ~/Dropbox/results_estimators/arbre_overhearing/arbre_low/powertracker.log
	scp enst:~/results_estimators/arbre_overhearing/arbre_low_calibration/serial.log ~/Dropbox/results_estimators/arbre_overhearing/arbre_low_calibration/serial.log
	scp enst:~/results_estimators/arbre_overhearing/arbre_low_calibration/powertracker.log ~/Dropbox/results_estimators/arbre_overhearing/arbre_low_calibration/powertracker.log
	scp enst:~/results_estimators/arbre_overhearing/arbre_medium/serial.log ~/Dropbox/results_estimators/arbre_overhearing/arbre_medium/serial.log
	scp enst:~/results_estimators/arbre_overhearing/arbre_medium/powertracker.log ~/Dropbox/results_estimators/arbre_overhearing/arbre_medium/powertracker.log
	scp enst:~/results_estimators/arbre_overhearing/arbre_medium_calibration/serial.log ~/Dropbox/results_estimators/arbre_overhearing/arbre_medium_calibration/serial.log
	scp enst:~/results_estimators/arbre_overhearing/arbre_medium_calibration/powertracker.log ~/Dropbox/results_estimators/arbre_overhearing/arbre_medium_calibration/powertracker.log

	scp enst:~/results_estimators/fleur/fleur_high/serial.log ~/Dropbox/results_estimators/fleur/fleur_high/serial.log
	scp enst:~/results_estimators/fleur/fleur_high/powertracker.log ~/Dropbox/results_estimators/fleur/fleur_high/powertracker.log
	scp enst:~/results_estimators/fleur/fleur_high_calibration/serial.log ~/Dropbox/results_estimators/fleur/fleur_high_calibration/serial.log
	scp enst:~/results_estimators/fleur/fleur_high_calibration/powertracker.log ~/Dropbox/results_estimators/fleur/fleur_high_calibration/powertracker.log
	scp enst:~/results_estimators/fleur/fleur_low/serial.log ~/Dropbox/results_estimators/fleur/fleur_low/serial.log
	scp enst:~/results_estimators/fleur/fleur_low/powertracker.log ~/Dropbox/results_estimators/fleur/fleur_low/powertracker.log
	scp enst:~/results_estimators/fleur/fleur_low_calibration/serial.log ~/Dropbox/results_estimators/fleur/fleur_low_calibration/serial.log
	scp enst:~/results_estimators/fleur/fleur_low_calibration/powertracker.log ~/Dropbox/results_estimators/fleur/fleur_low_calibration/powertracker.log
	scp enst:~/results_estimators/fleur/fleur_medium/serial.log ~/Dropbox/results_estimators/fleur/fleur_medium/serial.log
	scp enst:~/results_estimators/fleur/fleur_medium/powertracker.log ~/Dropbox/results_estimators/fleur/fleur_medium/powertracker.log
	scp enst:~/results_estimators/fleur/fleur_medium_calibration/serial.log ~/Dropbox/results_estimators/fleur/fleur_medium_calibration/serial.log
	scp enst:~/results_estimators/fleur/fleur_medium_calibration/powertracker.log ~/Dropbox/results_estimators/fleur/fleur_medium_calibration/powertracker.log

	scp enst:~/results_estimators/chaine/chaine_high/serial.log ~/Dropbox/results_estimators/chaine/chaine_high/serial.log
	scp enst:~/results_estimators/chaine/chaine_high/powertracker.log ~/Dropbox/results_estimators/chaine/chaine_high/powertracker.log
	scp enst:~/results_estimators/chaine/chaine_high_calibration/serial.log ~/Dropbox/results_estimators/chaine/chaine_high_calibration/serial.log
	scp enst:~/results_estimators/chaine/chaine_high_calibration/powertracker.log ~/Dropbox/results_estimators/chaine/chaine_high_calibration/powertracker.log
	scp enst:~/results_estimators/chaine/chaine_low/serial.log ~/Dropbox/results_estimators/chaine/chaine_low/serial.log
	scp enst:~/results_estimators/chaine/chaine_low/powertracker.log ~/Dropbox/results_estimators/chaine/chaine_low/powertracker.log
	scp enst:~/results_estimators/chaine/chaine_low_calibration/serial.log ~/Dropbox/results_estimators/chaine/chaine_low_calibration/serial.log
	scp enst:~/results_estimators/chaine/chaine_low_calibration/powertracker.log ~/Dropbox/results_estimators/chaine/chaine_low_calibration/powertracker.log
	scp enst:~/results_estimators/chaine/chaine_medium/serial.log ~/Dropbox/results_estimators/chaine/chaine_medium/serial.log
	scp enst:~/results_estimators/chaine/chaine_medium/powertracker.log ~/Dropbox/results_estimators/chaine/chaine_medium/powertracker.log
	scp enst:~/results_estimators/chaine/chaine_medium_calibration/serial.log ~/Dropbox/results_estimators/chaine/chaine_medium_calibration/serial.log
	scp enst:~/results_estimators/chaine/chaine_medium_calibration/powertracker.log ~/Dropbox/results_estimators/chaine/chaine_medium_calibration/powertracker.log

fetch_results_from_nexium:
	scp nexium:~/results_estimators/arbre/arbre_high/serial.log ~/Dropbox/results_estimators/arbre/arbre_high/serial.log
	scp nexium:~/results_estimators/arbre/arbre_high/powertracker.log ~/Dropbox/results_estimators/arbre/arbre_high/powertracker.log
	scp nexium:~/results_estimators/arbre/arbre_high_calibration/serial.log ~/Dropbox/results_estimators/arbre/arbre_high_calibration/serial.log
	scp nexium:~/results_estimators/arbre/arbre_high_calibration/powertracker.log ~/Dropbox/results_estimators/arbre/arbre_high_calibration/powertracker.log
	scp nexium:~/results_estimators/arbre/arbre_low/serial.log ~/Dropbox/results_estimators/arbre/arbre_low/serial.log
	scp nexium:~/results_estimators/arbre/arbre_low/powertracker.log ~/Dropbox/results_estimators/arbre/arbre_low/powertracker.log
	scp nexium:~/results_estimators/arbre/arbre_low_calibration/serial.log ~/Dropbox/results_estimators/arbre/arbre_low_calibration/serial.log
	scp nexium:~/results_estimators/arbre/arbre_low_calibration/powertracker.log ~/Dropbox/results_estimators/arbre/arbre_low_calibration/powertracker.log
	scp nexium:~/results_estimators/arbre/arbre_medium/serial.log ~/Dropbox/results_estimators/arbre/arbre_medium/serial.log
	scp nexium:~/results_estimators/arbre/arbre_medium/powertracker.log ~/Dropbox/results_estimators/arbre/arbre_medium/powertracker.log
	scp nexium:~/results_estimators/arbre/arbre_medium_calibration/serial.log ~/Dropbox/results_estimators/arbre/arbre_medium_calibration/serial.log
	scp nexium:~/results_estimators/arbre/arbre_medium_calibration/powertracker.log ~/Dropbox/results_estimators/arbre/arbre_medium_calibration/powertracker.log

	scp nexium:~/results_estimators/arbre_overhearing/arbre_high/serial.log ~/Dropbox/results_estimators/arbre_overhearing/arbre_high/serial.log
	scp nexium:~/results_estimators/arbre_overhearing/arbre_high/powertracker.log ~/Dropbox/results_estimators/arbre_overhearing/arbre_high/powertracker.log
	scp nexium:~/results_estimators/arbre_overhearing/arbre_high_calibration/serial.log ~/Dropbox/results_estimators/arbre_overhearing/arbre_high_calibration/serial.log
	scp nexium:~/results_estimators/arbre_overhearing/arbre_high_calibration/powertracker.log ~/Dropbox/results_estimators/arbre_overhearing/arbre_high_calibration/powertracker.log
	scp nexium:~/results_estimators/arbre_overhearing/arbre_low/serial.log ~/Dropbox/results_estimators/arbre_overhearing/arbre_low/serial.log
	scp nexium:~/results_estimators/arbre_overhearing/arbre_low/powertracker.log ~/Dropbox/results_estimators/arbre_overhearing/arbre_low/powertracker.log
	scp nexium:~/results_estimators/arbre_overhearing/arbre_low_calibration/serial.log ~/Dropbox/results_estimators/arbre_overhearing/arbre_low_calibration/serial.log
	scp nexium:~/results_estimators/arbre_overhearing/arbre_low_calibration/powertracker.log ~/Dropbox/results_estimators/arbre_overhearing/arbre_low_calibration/powertracker.log
	scp nexium:~/results_estimators/arbre_overhearing/arbre_medium/serial.log ~/Dropbox/results_estimators/arbre_overhearing/arbre_medium/serial.log
	scp nexium:~/results_estimators/arbre_overhearing/arbre_medium/powertracker.log ~/Dropbox/results_estimators/arbre_overhearing/arbre_medium/powertracker.log
	scp nexium:~/results_estimators/arbre_overhearing/arbre_medium_calibration/serial.log ~/Dropbox/results_estimators/arbre_overhearing/arbre_medium_calibration/serial.log
	scp nexium:~/results_estimators/arbre_overhearing/arbre_medium_calibration/powertracker.log ~/Dropbox/results_estimators/arbre_overhearing/arbre_medium_calibration/powertracker.log

	scp nexium:~/results_estimators/fleur/fleur_high/serial.log ~/Dropbox/results_estimators/fleur/fleur_high/serial.log
	scp nexium:~/results_estimators/fleur/fleur_high/powertracker.log ~/Dropbox/results_estimators/fleur/fleur_high/powertracker.log
	scp nexium:~/results_estimators/fleur/fleur_high_calibration/serial.log ~/Dropbox/results_estimators/fleur/fleur_high_calibration/serial.log
	scp nexium:~/results_estimators/fleur/fleur_high_calibration/powertracker.log ~/Dropbox/results_estimators/fleur/fleur_high_calibration/powertracker.log
	scp nexium:~/results_estimators/fleur/fleur_low/serial.log ~/Dropbox/results_estimators/fleur/fleur_low/serial.log
	scp nexium:~/results_estimators/fleur/fleur_low/powertracker.log ~/Dropbox/results_estimators/fleur/fleur_low/powertracker.log
	scp nexium:~/results_estimators/fleur/fleur_low_calibration/serial.log ~/Dropbox/results_estimators/fleur/fleur_low_calibration/serial.log
	scp nexium:~/results_estimators/fleur/fleur_low_calibration/powertracker.log ~/Dropbox/results_estimators/fleur/fleur_low_calibration/powertracker.log
	scp nexium:~/results_estimators/fleur/fleur_medium/serial.log ~/Dropbox/results_estimators/fleur/fleur_medium/serial.log
	scp nexium:~/results_estimators/fleur/fleur_medium/powertracker.log ~/Dropbox/results_estimators/fleur/fleur_medium/powertracker.log
	scp nexium:~/results_estimators/fleur/fleur_medium_calibration/serial.log ~/Dropbox/results_estimators/fleur/fleur_medium_calibration/serial.log
	scp nexium:~/results_estimators/fleur/fleur_medium_calibration/powertracker.log ~/Dropbox/results_estimators/fleur/fleur_medium_calibration/powertracker.log

	scp nexium:~/results_estimators/chaine/chaine_high/serial.log ~/Dropbox/results_estimators/chaine/chaine_high/serial.log
	scp nexium:~/results_estimators/chaine/chaine_high/powertracker.log ~/Dropbox/results_estimators/chaine/chaine_high/powertracker.log
	scp nexium:~/results_estimators/chaine/chaine_high_calibration/serial.log ~/Dropbox/results_estimators/chaine/chaine_high_calibration/serial.log
	scp nexium:~/results_estimators/chaine/chaine_high_calibration/powertracker.log ~/Dropbox/results_estimators/chaine/chaine_high_calibration/powertracker.log
	scp nexium:~/results_estimators/chaine/chaine_low/serial.log ~/Dropbox/results_estimators/chaine/chaine_low/serial.log
	scp nexium:~/results_estimators/chaine/chaine_low/powertracker.log ~/Dropbox/results_estimators/chaine/chaine_low/powertracker.log
	scp nexium:~/results_estimators/chaine/chaine_low_calibration/serial.log ~/Dropbox/results_estimators/chaine/chaine_low_calibration/serial.log
	scp nexium:~/results_estimators/chaine/chaine_low_calibration/powertracker.log ~/Dropbox/results_estimators/chaine/chaine_low_calibration/powertracker.log
	scp nexium:~/results_estimators/chaine/chaine_medium/serial.log ~/Dropbox/results_estimators/chaine/chaine_medium/serial.log
	scp nexium:~/results_estimators/chaine/chaine_medium/powertracker.log ~/Dropbox/results_estimators/chaine/chaine_medium/powertracker.log
	scp nexium:~/results_estimators/chaine/chaine_medium_calibration/serial.log ~/Dropbox/results_estimators/chaine/chaine_medium_calibration/serial.log
	scp nexium:~/results_estimators/chaine/chaine_medium_calibration/powertracker.log ~/Dropbox/results_estimators/chaine/chaine_medium_calibration/powertracker.log

push_to_paper:
	cp ./calibration/nullmac/nullmac_calibration_receiver.pdf ~/workspace/tee/img/nullmac_calibration_receiver.pdf
	cp ./calibration/nullmac/nullmac_calibration_sender.pdf ~/workspace/tee/img/nullmac_calibration_sender.pdf

	cp ./calibration/contikimac/contikimac_calibration_receiver.pdf ~/workspace/tee/img/contikimac_calibration_receiver.pdf
	cp ./calibration/contikimac/contikimac_calibration_sender.pdf ~/workspace/tee/img/contikimac_calibration_sender.pdf

# Chaine near of gateway

	cp ./chaine/chaine_high/estimation/bin_estimation_global_noinfo.pdf ~/workspace/tee/img/chaine_global_noinfo.pdf
	cp ./chaine/chaine_high/estimation/bin_estimation_2_noinfo.pdf ~/workspace/tee/img/chaine_near_noinfo.pdf
	cp ./chaine/chaine_high/estimation/bin_estimation_2_route.pdf ~/workspace/tee/img/chaine_near_route.pdf
	cp ./chaine/chaine_high_calibration/estimation/bin_estimation_2_noinfo.pdf ~/workspace/tee/img/chaine_near_noinfo_calibration.pdf
	cp ./chaine/chaine_high_calibration/estimation/bin_estimation_2_route.pdf ~/workspace/tee/img/chaine_near_route_calibration.pdf

# Central flower

	cp ./fleur/fleur_low/estimation/bin_estimation_global_route.pdf ~/workspace/tee/img/fleur_global_route.pdf
	cp ./fleur/fleur_low/estimation/bin_estimation_8_route.pdf ~/workspace/tee/img/fleur_central_route.pdf
	cp ./fleur/fleur_low/estimation/bin_estimation_8_radio.pdf ~/workspace/tee/img/fleur_central_radio.pdf
	cp ./fleur/fleur_low_calibration/estimation/bin_estimation_8_route.pdf ~/workspace/tee/img/fleur_central_route_calibration.pdf
	cp ./fleur/fleur_low_calibration/estimation/bin_estimation_8_radio.pdf ~/workspace/tee/img/fleur_central_radio_calibration.pdf

sync:
	rsync -Pizav . enst:results_estimators

sync_tai:
	rsync -Pizav . nexium:~/results_estimators

sync_web:
	rsync -Pizav . perso:~/html/results

SHIFT=90

strip_powertracker:
	@echo Will remove the first $(SHIFT) seconds of simulation
	cat powertracker.csv | awk -F"," '$$2 > $(SHIFT)' > powertracker_stripped.log

strip_pcap:
	@echo Will remove the first $(SHIFT) seconds of simulation
	tshark -r output.pcap -Y "frame.time_relative > $(SHIFT)" -w output_stripped.pcap

deploy_calibration:
	@echo Deploy udp client and server to calibration

	cp udp-client.c udp-server.c packet_size/contikimac/10
	cp udp-client.c udp-server.c packet_size/contikimac/20
	cp udp-client.c udp-server.c packet_size/contikimac/30
	cp udp-client.c udp-server.c packet_size/contikimac/40
	cp udp-client.c udp-server.c packet_size/contikimac/50

	cp udp-client.c udp-server.c packet_size/nullmac/10
	cp udp-client.c udp-server.c packet_size/nullmac/20
	cp udp-client.c udp-server.c packet_size/nullmac/30
	cp udp-client.c udp-server.c packet_size/nullmac/40
	cp udp-client.c udp-server.c packet_size/nullmac/50


SMALL = 1

UIP_CONF_ROUTER=1
UIP_CONF_IPV6=1
WITH_COMPOWER=1


CFLAGS+= -DPROJECT_CONF_H=\"project-conf.h\"
CFLAGS+= -DUIP_CONF_IPV6_RPL
CFLAGS+= -lm
CFLAGS+= -DRPLINFO_RATE=$(RPLINFO_RATE)
CFLAGS+= -DBATTERY_RATE=$(BATTERY_RATE)
CFLAGS+= -DCBR_RATE=$(CBR_RATE)
CFLAGS+= -DPOISSON_RATE=$(POISSON_RATE)

ifdef PERIOD
CFLAGS+=-DPERIOD=$(PERIOD)
endif

ifdef WITH_COMPOWER
APPS+=powertrace
CFLAGS+= -DCONTIKIMAC_CONF_COMPOWER=1 -DWITH_COMPOWER=1
endif

ifdef SERVER_REPLY
CFLAGS+=-DSERVER_REPLY=$(SERVER_REPLY)
endif

include $(CONTIKI)/Makefile.include
