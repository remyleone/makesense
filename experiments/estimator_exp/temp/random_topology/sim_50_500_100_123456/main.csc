<?xml version="1.0" encoding="UTF-8"?>
<simconf>
 <project EXPORT="discard">[APPS_DIR]/mrm</project>
 <project EXPORT="discard">[APPS_DIR]/mspsim</project>
 <project EXPORT="discard">[APPS_DIR]/avrora</project>
 <project EXPORT="discard">[APPS_DIR]/powertracker</project>
 <simulation>
   <title>My simulation</title>
  
   <randomseed>123456</randomseed>
  
   <motedelay_us>1000000</motedelay_us>
   <radiomedium>
    org.contikios.cooja.radiomediums.UDGM
    <transmitting_range>42</transmitting_range>
    <interference_range>42</interference_range>
    <success_ratio_tx>1.0</success_ratio_tx>
    <success_ratio_rx>1.0</success_ratio_rx>
  </radiomedium>
  <events>
    <logoutput>40000</logoutput>
  </events>
  <motetype>
    org.contikios.cooja.mspmote.SkyMoteType
    <identifier>udp_client</identifier>
    <description>Sky Mote Type #rawmac_udp_client</description>
    <firmware EXPORT="copy">udp-client_50_500_100.sky</firmware>
    <moteinterface>org.contikios.cooja.interfaces.Position</moteinterface>
    <moteinterface>org.contikios.cooja.interfaces.RimeAddress</moteinterface>
    <moteinterface>org.contikios.cooja.interfaces.IPAddress</moteinterface>
    <moteinterface>org.contikios.cooja.interfaces.Mote2MoteRelations</moteinterface>
    <moteinterface>org.contikios.cooja.interfaces.MoteAttributes</moteinterface>
    <moteinterface>org.contikios.cooja.mspmote.interfaces.MspClock</moteinterface>
    <moteinterface>org.contikios.cooja.mspmote.interfaces.MspMoteID</moteinterface>
    <moteinterface>org.contikios.cooja.mspmote.interfaces.SkyButton</moteinterface>
    <moteinterface>org.contikios.cooja.mspmote.interfaces.SkyFlash</moteinterface>
    <moteinterface>org.contikios.cooja.mspmote.interfaces.SkyCoffeeFilesystem</moteinterface>
    <moteinterface>org.contikios.cooja.mspmote.interfaces.Msp802154Radio</moteinterface>
    <moteinterface>org.contikios.cooja.mspmote.interfaces.MspSerial</moteinterface>
    <moteinterface>org.contikios.cooja.mspmote.interfaces.SkyLED</moteinterface>
    <moteinterface>org.contikios.cooja.mspmote.interfaces.MspDebugOutput</moteinterface>
    <moteinterface>org.contikios.cooja.mspmote.interfaces.SkyTemperature</moteinterface>
  </motetype>
  <motetype>
    org.contikios.cooja.mspmote.SkyMoteType
    <identifier>udp_server</identifier>
    <description>Sky Mote Type #rawmac_udp_server</description>
    <firmware EXPORT="copy">udp-server.sky</firmware>
    <moteinterface>org.contikios.cooja.interfaces.Position</moteinterface>
    <moteinterface>org.contikios.cooja.interfaces.RimeAddress</moteinterface>
    <moteinterface>org.contikios.cooja.interfaces.IPAddress</moteinterface>
    <moteinterface>org.contikios.cooja.interfaces.Mote2MoteRelations</moteinterface>
    <moteinterface>org.contikios.cooja.interfaces.MoteAttributes</moteinterface>
    <moteinterface>org.contikios.cooja.mspmote.interfaces.MspClock</moteinterface>
    <moteinterface>org.contikios.cooja.mspmote.interfaces.MspMoteID</moteinterface>
    <moteinterface>org.contikios.cooja.mspmote.interfaces.SkyButton</moteinterface>
    <moteinterface>org.contikios.cooja.mspmote.interfaces.SkyFlash</moteinterface>
    <moteinterface>org.contikios.cooja.mspmote.interfaces.SkyCoffeeFilesystem</moteinterface>
    <moteinterface>org.contikios.cooja.mspmote.interfaces.Msp802154Radio</moteinterface>
    <moteinterface>org.contikios.cooja.mspmote.interfaces.MspSerial</moteinterface>
    <moteinterface>org.contikios.cooja.mspmote.interfaces.SkyLED</moteinterface>
    <moteinterface>org.contikios.cooja.mspmote.interfaces.MspDebugOutput</moteinterface>
    <moteinterface>org.contikios.cooja.mspmote.interfaces.SkyTemperature</moteinterface>
  </motetype>
  <motetype>
    org.contikios.cooja.mspmote.SkyMoteType
    <identifier>hello-world</identifier>
    <description>Sky Mote Type #rawmac_udp_server</description>
    <firmware EXPORT="copy">hello-world.sky</firmware>
    <moteinterface>org.contikios.cooja.interfaces.Position</moteinterface>
    <moteinterface>org.contikios.cooja.interfaces.RimeAddress</moteinterface>
    <moteinterface>org.contikios.cooja.interfaces.IPAddress</moteinterface>
    <moteinterface>org.contikios.cooja.interfaces.Mote2MoteRelations</moteinterface>
    <moteinterface>org.contikios.cooja.interfaces.MoteAttributes</moteinterface>
    <moteinterface>org.contikios.cooja.mspmote.interfaces.MspClock</moteinterface>
    <moteinterface>org.contikios.cooja.mspmote.interfaces.MspMoteID</moteinterface>
    <moteinterface>org.contikios.cooja.mspmote.interfaces.SkyButton</moteinterface>
    <moteinterface>org.contikios.cooja.mspmote.interfaces.SkyFlash</moteinterface>
    <moteinterface>org.contikios.cooja.mspmote.interfaces.SkyCoffeeFilesystem</moteinterface>
    <moteinterface>org.contikios.cooja.mspmote.interfaces.Msp802154Radio</moteinterface>
    <moteinterface>org.contikios.cooja.mspmote.interfaces.MspSerial</moteinterface>
    <moteinterface>org.contikios.cooja.mspmote.interfaces.SkyLED</moteinterface>
    <moteinterface>org.contikios.cooja.mspmote.interfaces.MspDebugOutput</moteinterface>
    <moteinterface>org.contikios.cooja.mspmote.interfaces.SkyTemperature</moteinterface>
  </motetype>

  
  
  <mote>
    <interface_config>
      org.contikios.cooja.interfaces.Position
      <x>17.909517025</x>
      <y>27.3063557471</y>
    </interface_config>
    <interface_config>
      org.contikios.cooja.mspmote.interfaces.MspMoteID
      <id>1</id>
    </interface_config>
    <motetype_identifier>udp_client</motetype_identifier>
  </mote>
  
  <mote>
    <interface_config>
      org.contikios.cooja.interfaces.Position
      <x>39.7577335138</x>
      <y>28.9608968489</y>
    </interface_config>
    <interface_config>
      org.contikios.cooja.mspmote.interfaces.MspMoteID
      <id>2</id>
    </interface_config>
    <motetype_identifier>udp_client</motetype_identifier>
  </mote>
  
  <mote>
    <interface_config>
      org.contikios.cooja.interfaces.Position
      <x>7.00629476914</x>
      <y>58.0579565377</y>
    </interface_config>
    <interface_config>
      org.contikios.cooja.mspmote.interfaces.MspMoteID
      <id>3</id>
    </interface_config>
    <motetype_identifier>udp_client</motetype_identifier>
  </mote>
  
  <mote>
    <interface_config>
      org.contikios.cooja.interfaces.Position
      <x>26.7717977922</x>
      <y>79.9024598463</y>
    </interface_config>
    <interface_config>
      org.contikios.cooja.mspmote.interfaces.MspMoteID
      <id>4</id>
    </interface_config>
    <motetype_identifier>udp_client</motetype_identifier>
  </mote>
  
  <mote>
    <interface_config>
      org.contikios.cooja.interfaces.Position
      <x>66.0547766781</x>
      <y>37.041001141</y>
    </interface_config>
    <interface_config>
      org.contikios.cooja.mspmote.interfaces.MspMoteID
      <id>5</id>
    </interface_config>
    <motetype_identifier>udp_client</motetype_identifier>
  </mote>
  
  <mote>
    <interface_config>
      org.contikios.cooja.interfaces.Position
      <x>44.1924684752</x>
      <y>81.7096257514</y>
    </interface_config>
    <interface_config>
      org.contikios.cooja.mspmote.interfaces.MspMoteID
      <id>6</id>
    </interface_config>
    <motetype_identifier>udp_client</motetype_identifier>
  </mote>
  
  <mote>
    <interface_config>
      org.contikios.cooja.interfaces.Position
      <x>72.5432070736</x>
      <y>47.1869439025</y>
    </interface_config>
    <interface_config>
      org.contikios.cooja.mspmote.interfaces.MspMoteID
      <id>7</id>
    </interface_config>
    <motetype_identifier>udp_client</motetype_identifier>
  </mote>
  
  <mote>
    <interface_config>
      org.contikios.cooja.interfaces.Position
      <x>3.74662703377</x>
      <y>47.3983988801</y>
    </interface_config>
    <interface_config>
      org.contikios.cooja.mspmote.interfaces.MspMoteID
      <id>8</id>
    </interface_config>
    <motetype_identifier>udp_server</motetype_identifier>
  </mote>
  
  
</simulation>
<plugin>
  org.contikios.cooja.plugins.LogListener
  <plugin_config>
    <filter />
  </plugin_config>
  <width>937</width>
  <z>0</z>
  <height>213</height>
  <location_x>21</location_x>
  <location_y>464</location_y>
</plugin>
<plugin>
  org.contikios.cooja.plugins.SimControl
  <width>410</width>
  <z>2</z>
  <height>194</height>
  <location_x>5</location_x>
  <location_y>481</location_y>
</plugin>

<plugin>
  org.contikios.cooja.plugins.Visualizer
  <plugin_config>
    <skin>org.contikios.cooja.plugins.skins.IDVisualizerSkin</skin>
    <skin>org.contikios.cooja.plugins.skins.GridVisualizerSkin</skin>
    <skin>org.contikios.cooja.plugins.skins.TrafficVisualizerSkin</skin>
    <skin>org.contikios.cooja.plugins.skins.UDGMVisualizerSkin</skin>
    <skin>org.contikios.cooja.plugins.skins.AddressVisualizerSkin</skin>
    <skin>org.contikios.cooja.plugins.skins.MoteTypeVisualizerSkin</skin>
    <viewport>2.835293142444373 0.0 0.0 2.835293142444373 109.55579239049345 15.727272727272743</viewport>
  </plugin_config>
  <width>400</width>
  <z>6</z>
  <height>400</height>
  <location_x>1</location_x>
  <location_y>1</location_y>
</plugin>

<plugin>
  be.cetic.cooja.plugins.RadioLoggerHeadless
  <plugin_config>
    <split>268</split>
    <pcap_file>output.pcap</pcap_file>
    <analyzers name="6lowpan-pcap" />
  </plugin_config>
</plugin>

<plugin>
  PowerTracker
</plugin>

<plugin>
  org.contikios.cooja.plugins.ScriptRunner
  <plugin_config>
    <script>
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

      TIMEOUT(1000000);
      counter = 0;
      frequence = 100000;

      while(1) {

      serial_log_file.write(time + " ID:"+id.toString()+" " + msg + "\n");
      serial_log_file.flush();

      //This is the tricky part. The Script is terminated using
      // an exception. This needs to be caught.
      try{
      YIELD();
      if (counter &lt; time){
        log.log(counter);
        printStatistics();
        counter += frequence;
      }

      } catch (e) {
      //Close files.
      serial_log_file.close();
      power_tracker_file.close();
      //Rethrow exception again, to end the script.
      throw('test script killed');
      }
      }
    </script>
    <active>true</active>
  </plugin_config>
  <width>932</width>
  <z>1</z>
  <height>319</height>
  <location_x>427</location_x>
  <location_y>385</location_y>
</plugin>
</simconf>