// Simple lambda bootstrap In every log that this script will create, we will
// add the time of the simulation, the time of the  nodes, and of course the
// id of the node. By doing so we will have accurate log to analyze.

// Timeout of the whole simulation milliseconds.
TIMEOUT({{ simulation_time }});

// Set to real time
//sim.setSpeedLimit(1.0);

//////////////////////////////////////////////////////////////////////////////
// RANDOM CHOICES
//////////////////////////////////////////////////////////////////////////////

function choice(set){
  index = Math.floor(Math.random() * set.length);
  return set[index];
}

// If the first item of my array got a prob property, this property is
// assumed on all item of the array. It's taken in account to decide what
// item will be used.
// BEWARE &lt; means less than
function choice_prob(set) {
  var rand = Math.random();
  var prob_marker = set[0]["prob"];
  for(index = 0; index &lt; set.length; index++){
    if (rand &lt; prob_marker) {
      return set[index]["function"];
    }
    else {
      prob_marker += set[index]["prob"];
    }
  }
}

//////////////////////////////////////////////////////////////////////////////
// TRAFIC CLASSES
//////////////////////////////////////////////////////////////////////////////

// Function for sending traffic from a node towards a the root of a precise
// instance.
function upstream(mote_id){
  log.log("[" + time + "] [upstream] from " + mote_id + "\n");
  exp_wait(lambda);
}

// Function generating traffic from the root to a node following a precise
// instance.
function downstream(mote_id){
  chosen_node = Math.floor(Math.random() * all_motes.length);
  log.log("[" + time + "] [downstream] Chosen node :" + chosen_node + "\n");
  exp_wait(lambda);
  write(sim.getMoteWithID(chosen_node), chosen_node);
}

//////////////////////////////////////////////////////////////////////////////
// VARIABLES
//////////////////////////////////////////////////////////////////////////////

// lambda
lambda = 1.0;

all_motes = sim.getMotes();

traffic_class_probability = [
  {% for trafic_class in trafic_classes %}
  {
  "trafic_id": "{{ trafic_class.trafic_id }}",
  "prob": {{ trafic_class.prob }},
  "function": {{ trafic_class.trafic_id }}
},
{% endfor %}
];

// Exponential wait in order to obtain a Poisson law
function exp_wait(lambda){
  waiting_time = - Math.log(1.0 - Math.random()) / lambda;
  log.log("[" + time + "] [exp_wait] Waiting time " + waiting_time + "\n");
  GENERATE_MSG(waiting_time, "sleep");
  YIELD_THEN_WAIT_UNTIL(msg.equals("sleep"));
}

//////////////////////////////////////////////////////////////////////////////
// ADMIN / BOOTSTRAPING
//////////////////////////////////////////////////////////////////////////////

// Sending the order to a mote (mote_id) to print the rplinfo results for
// routes and parents function
function rplinfo(node_id){
  log.log("[" + time + "] [rplinfo] [node " + node_id + "]\n");
  write(sim.getMoteWithID(node_id), "routes");
  write(sim.getMoteWithID(node_id), "parents");
}

// Bootstrapping a precise node.
function bootstrap(mote_id, lambda){
  log.log("[" + time + "] [bootstrap] [node " + mote_id + "] lambda: " + lambda + "\n");
  write(sim.getMoteWithID(mote_id), "bootstrap");
}
//////////////////////////////////////////////////////////////////////////////
// SIMULATION SCRIPT START
//////////////////////////////////////////////////////////////////////////////

log.log("###################################################################\n");
log.log("# WAITING FOR THE NETWORK TO FINISHED CONVERGING\n");
log.log("###################################################################\n");

// Timer used to wait for the network stack to be up and running.
GENERATE_MSG({{ waiting_time_before_start_processes }}, "sleep");
YIELD_THEN_WAIT_UNTIL(msg.equals("sleep"));

log.log("###################################################################\n");
log.log("# BOOTSTRAPING THE NODES\n");
log.log("###################################################################\n");

// Bootstrapping of our motes.
// {% for mote in motes %}
//   bootstrap({{ mote.mote_id }}, 1);
// {% endfor %}

log.log("###################################################################\n");
log.log("# STARTING GENERATING TRAFFIC\n");
log.log("###################################################################\n");

msg_to_send = [
  {
  "time": 400,
  "id": 5,
  "command": "parents"
},
{
  "time": 234,
  "id": 8,
  "command": "bootstrap"
},
{
  "time": 345,
  "id": 2,
  "command": "routes"
},
{
  "time": 1000,
  "id": 2,
  "command": "parents"
},
{
  "time": 2000,
  "id": 2,
  "command": "parents"
},
{
  "time": 244758504,
  "id": 4,
  "command": "pwet"
}
];

msg_to_send.sort(function(a, b){ return b["time"] - a["time"] });

// Loop sending orders to the motes.
while(true){
  // if(msg_to_send.length){
  //   event_to_do = msg_to_send.pop();
  //   log.log(event_to_do["time"] + "\n");
  //   log.log(event_to_do["id"] + "\n");
  //   log.log(event_to_do["command"] + "\n");
  // }
  // else{
  rplinfo(choice(all_motes).getID());
  // }
  GENERATE_MSG(2000, "sleep"); //Wait for two sec
  YIELD_THEN_WAIT_UNTIL(msg.equals("sleep"));
  // log.log(time + "We pass the YIELD keyword\n");
  //log.log(msg); // We print by default everything
}

log.testOK();
