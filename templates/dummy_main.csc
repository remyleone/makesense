<?xml version="1.0" encoding="UTF-8"?>
<simconf>
  <project EXPORT="discard">[APPS_DIR]/mrm</project>
  <project EXPORT="discard">[APPS_DIR]/mspsim</project>
  <project EXPORT="discard">[APPS_DIR]/avrora</project>
  <project EXPORT="discard">[APPS_DIR]/serial_socket</project>
  <project EXPORT="discard">[APPS_DIR]/collect-view</project>
  <project EXPORT="discard">[APPS_DIR]/powertracker</project>
  <simulation>
    <title>{{ title }}</title>
    <randomseed>{{ random_seed }}</randomseed>
    <radiomedium>
      org.contikios.cooja.radiomediums.UDGM
      <transmitting_range>{{ transmitting_range }}</transmitting_range>
      <interference_range>{{ interference_range }}</interference_range>
      <success_ratio_tx>{{ success_ratio_tx }}</success_ratio_tx>
      <success_ratio_rx>{{ success_ratio_rx }}</success_ratio_rx>
    </radiomedium>
    {% for mote_type in mote_types %}
    <motetype>
      org.contikios.cooja.mspmote.WismoteMoteType
      <identifier>{{ mote_type.name }}</identifier>
      <source EXPORT="discard">{{ mote_type.source }}</source>
      <commands EXPORT="discard">{{ mote_type.commands }}</commands>
      <firmware EXPORT="copy">{{ mote_type.firmware }}</firmware>
      <moteinterface>org.contikios.cooja.interfaces.Position</moteinterface>
      <moteinterface>org.contikios.cooja.interfaces.RimeAddress</moteinterface>
      <moteinterface>org.contikios.cooja.interfaces.IPAddress</moteinterface>
      <moteinterface>org.contikios.cooja.interfaces.Mote2MoteRelations</moteinterface>
      <moteinterface>org.contikios.cooja.interfaces.MoteAttributes</moteinterface>
      <moteinterface>org.contikios.cooja.mspmote.interfaces.MspClock</moteinterface>
      <moteinterface>org.contikios.cooja.mspmote.interfaces.MspMoteID</moteinterface>
      <moteinterface>org.contikios.cooja.mspmote.interfaces.MspButton</moteinterface>
      <moteinterface>org.contikios.cooja.mspmote.interfaces.Msp802154Radio</moteinterface>
      <moteinterface>org.contikios.cooja.mspmote.interfaces.MspDefaultSerial</moteinterface>
      <moteinterface>org.contikios.cooja.mspmote.interfaces.MspLED</moteinterface>
      <moteinterface>org.contikios.cooja.mspmote.interfaces.MspDebugOutput</moteinterface>
    </motetype>
    {% endfor %}
    {% for mote in motes %}
    <mote>
      <breakpoints />
      <interface_config>
        org.contikios.cooja.interfaces.Position
        <x>{{ mote.x }}</x>
        <y>{{ mote.y }}</y>
        <z>{{ mote.z }}</z>
      </interface_config>
      <interface_config>
        org.contikios.cooja.mspmote.interfaces.MspMoteID
        <id>{{ mote.mote_id }}</id>
      </interface_config>
      <motetype_identifier>{{ mote.mote_type }}</motetype_identifier>
    </mote>
    {% endfor %}
  </simulation>
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
    org.contikios.cooja.plugins.Visualizer
    <plugin_config>
      <skin>org.contikios.cooja.plugins.skins.IDVisualizerSkin</skin>
      <skin>org.contikios.cooja.plugins.skins.GridVisualizerSkin</skin>
      <skin>org.contikios.cooja.plugins.skins.TrafficVisualizerSkin</skin>
      <skin>org.contikios.cooja.plugins.skins.UDGMVisualizerSkin</skin>
      <viewport>2.835293142444373 0.0 0.0 2.835293142444373 109.55579239049345 15.727272727272743</viewport>
    </plugin_config>
    <width>400</width>
    <z>5</z>
    <height>400</height>
    <location_x>1</location_x>
    <location_y>1</location_y>
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
    <z>0</z>
    <height>400</height>
    <location_x>1</location_x>
    <location_y>1</location_y>
  </plugin>
  <plugin>
    org.contikios.cooja.plugins.RadioLogger
    <plugin_config>
      <split>268</split>
      <analyzers name="6lowpan-pcap" />
      <pcap_file EXPORT="discard">output.pcap</pcap_file>
    </plugin_config>
    <width>945</width>
    <z>3</z>
    <height>358</height>
    <location_x>402</location_x>
    <location_y>3</location_y>
  </plugin>
  <plugin>
    org.contikios.cooja.plugins.ScriptRunner
    <plugin_config>
      <script>
      {{ script }}
      </script>
      <active>true</active>
    </plugin_config>
    <width>932</width>
    <z>1</z>
    <height>319</height>
    <location_x>427</location_x>
    <location_y>385</location_y>
  </plugin>
  <plugin>
    org.contikios.cooja.serialsocket.SerialSocketServer
    <mote_arg>0</mote_arg>
    <plugin_config>
      <port>60001</port>
      <bound>true</bound>
    </plugin_config>
    <width>362</width>
    <z>0</z>
    <height>116</height>
    <location_x>457</location_x>
    <location_y>415</location_y>
  </plugin>
</simconf>
