importPackage(java.io);

power_tracker = mote.getSimulation().getCooja().getStartedPlugin("PowerTracker");
serial_log_file = new FileWriter("serial.log");
power_tracker_file = new FileWriter("powertracker.log", false);

function time_prefix(val){
      var i= 0;

      var array1 = val.split("\n");
      for ( i = 0; i &lt; array1.length; i++) {
        array1[i] = time + array1[i];
  }
  val = array1.join("\n");
}

function printStatistics() {

      /* Extract power tracker statistics */

      if (power_tracker != null) {
            stats = power_tracker.radioStatistics();
            log.log("PowerTracker: Extracted statistics:\n" + stats + "\n");
            time_prefix(stats);
            power_tracker_file.write(stats);
            power_tracker_file.flush();
      } else {
            log.log("No PowerTracker plugin\n");
      }
}

TIMEOUT({{ timeout }}, log.log("last msg: " + msg + "\n"));
counter = 0;
powertracker_frequency = {{ powertracker_frequency }};

while(1) {

      serial_log_file.write(time + " ID:" + id.toString() + " " + msg + "\n");
      serial_log_file.flush();

      //This is the tricky part. The Script is terminated using
      // an exception. This needs to be caught.
      try{
            YIELD();
            if (counter &lt; time){
                log.log(counter);
                printStatistics();
                counter += powertracker_frequency;
          }

    } catch (e) {
      //Close files.
      serial_log_file.close();
      power_tracker_file.close();
      //Rethrow exception again, to end the script.
      throw('test script killed');
      log.testOK();
    }
}
log.testOK();