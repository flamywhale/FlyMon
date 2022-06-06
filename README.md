<h1 align="center">
  <br>
  FlyMon
  <br>
</h1>

<h4 align="center">A reference implementation of SIGCOMM'22 Paper <a href="www.google.com" target="_blank">FlyMon</a>.</h4>

<p align="center">
  <a href="#🎯-key-features">Key Features</a> •
  <a href="#🚄-hardware-implementation">Hardware Implementation</a> •
  <a href="#simulation-framework">Simulation Framework</a> •
  <a href="#license">License</a> •
  <a href="#links">Links</a>
</p>

## 🎯 Key Features

* P4-16 based hardware implementation.
* Jinja2 templates used to generate P4 codes according to variable configurations (e.g., CMU-Groups, Memory Size, Candidate Key Set).
* Several built-in algorithms used to measure various flow attributes.
* A reference control plane framework realizing task reconfiguration, resource management, data collection, and task query.
* A simulation framework to fast explore built-in algorithms' accuracy.

> 🔔 We are improving the richness and reliability of this repository. Please submit an issue (or a pull request) if you find (or solve) any bugs/problems.

> ⚠️ This repository serves as an early exploration for academics purpose. We do not provide production-level quality assurance.

## 🚄 Hardware Implementation

### 🕶️ Overview

As shown in the figure below, the FlyMon hardware implementation is based on the Tofino hardware platform, including the SDE, runtime interfaces, etc.

<div align="center">
<img src="docs/controlplane.svg" width=80% />
</div>

To better test and use FlyMon, we did some engineering efforts for the implementation of the data plane and the control plane.

For the data plane, our P4 codes are generated by using the [Jinja2](https://jinja.palletsprojects.com/en/3.1.x/) template (we need to thank the author of [BeauCoup](https://github.com/Princeton-Cabernet/BeauCoup) that inspired us to do so). The Jinja2 templates (located in [p4_templates](./p4_templates/)) allow us to flexibly and quickly extend our data plane codes to avoid various bugs. For example, when deploying 9 CMU-Groups, the P4 codes reache over 5000 LOC, which is difficult to maintain manually. More importantly, we can easily modify the configuration of the data plane, such as the number of CMU-Groups, the set of candidate keys, the size of the static memory of a single CMU, etc.

For the control plane, we provide user-friendly, interactive interfaces to dynamically configure tasks (i.e., add and delete tasks). We performe layers of abstraction, gradually shielding the underlying hardware details. When compiling the data plane code, the [FlyMon compiler](./flymon_compiler.py) also generates [a configuration file](./control_plane/cmu_groups.json) for the control plane, which is used to adjust the control plane's interfaces to adapt to various underlayer data plane configurations.

Below we show how to use these codes.

### ⚙️ Requirements

This repository has strict hardware and software requirements.

**Hardware Requirements**

* Tofino-based Hardware Switch (e.g., Wdege-100BF-XX).
* At least one Server with QSFP28 connectors and wires.

**Software Requirements**

* Switch OS: OpenNetworkLinux 4.14.151
* Python: 3.8.10 
* SDE: Version 9.7.0+ (the same is best)

> 🔔 In this document, all 'python' and 'pip' refer to the python version of 3.8.10.

There are some dependencies for control plane functions. To install them.
```bash
git clone "https://github.com/NASA-NJU/FlyMon.git"
cd FlyMon
pip install -r ./requirements.txt
```

### 🔨 Build Data Plane

In order to generate your custom data plane code, use the Jinja2 code generator we provide.

```bash
python flymon_compiler.py -n 9 -m memory_level_min
```

The above command means that 9 CMU-Groups are generated in the data plane, and each CMU has a static (maximum) memory type of 'memory_level_mini'.  

> 🔔 For easy viewing of memory status, we generate mini-level CMUs (i.e., only 32 16-bit counters in each CMU) here. You can choose a larger level of memory (e.g., memory_level_8) for more practical purposes. The available memory levels are list in `flymon_compiler.py`.

Once the data plane codes are generated, you can build the p4 codes with bf-p4c. Here we give a setup script if you don't known how to compile the codes.

```bash
# If you are working on SDE 9.7.0+
export FLYMON_DIR=/path/to/your/flymon
./setup.sh
```
> 🔔 You also need to check if SDE environment variables (e.g., `SDE` and `SDE_INSTALL`) are set correctly.

> 🔔 The compilation process usually takes between 20 and 60 minutes. Yes, it does compile slowly, but please be patient. 


### 🚀 Running FlyMon

Starting FlyMon requires starting the data plane and the control plane separately.

Firstly, load the program for the data plane.

```bash
$SDE/run_switchd.sh -p flymon
```

Secondly, start the FlyMon interactive control plane in another terminal.
```
cd $FLYMON_DIR/control_plane/
./run_controller.sh
```

If all goes well, you will be taken to the command line interface of FlyMon.

```
----------------------------------------------------
    ______   __            __  ___                
   / ____/  / /  __  __   /  |/  /  ____     ____ 
  / /_     / /  / / / /  / /|_/ /  / __ \   / __ \
 / __/    / /  / /_/ /  / /  / /  / /_/ /  / / / /
/_/      /_/   \__, /  /_/  /_/   \____/  /_/ /_/ 
              /____/                                 
----------------------------------------------------
    An on-the-fly network measurement system.       
    **NOTE**: FlyMon's controller will clear all previous data plane 
              tasks/datas when setup.
    
flymon> 
```


### 📝 Use Cases

We demonstrate the dynamic features of FlyMon through three typical use cases.


<details><summary><b>Dynamic Deployment of Measurement Tasks</b></summary>

Suppose we deploy a new measurement task. We define key as SrcIP/24 and attribute as frequency(1). We are interested in the traffic with SrcIP in 10.0.0.0/8. We can deploy this measurement task with the `add_task` command.

```
flymon> add_task -f 10.0.0.0/8,* -k hdr.ipv4.src_addr/24 -a frequency(1) -m 48
```

The above command will deploy a Count-Min Sketch (d=3, w=16) in the data plane for this task.

If there are enough resources in the data plane to deploy this measurement task, you will get the following output.

```
flymon> add_task -f 10.0.0.0/8,* -k hdr.ipv4.src_addr/24 -a frequency(1) -m 48
Required resources:
[ResourceType: CompressedKey, Content: hdr.ipv4.src_addr/24]
[ResourceType: CompressedKey, Content: hdr.ipv4.src_addr/24]
[ResourceType: CompressedKey, Content: hdr.ipv4.src_addr/24]
[ResourceType: Memory, Content: 16]
[ResourceType: Memory, Content: 16]
[ResourceType: Memory, Content: 16]
----------------------------------------------------
[Active Task] 
Filter= [('10.0.0.0', '255.0.0.0'), ('0.0.0.0', '0.0.0.0')]
ID = 1
Key = hdr.ipv4.src_addr/24
Attribute = frequency(1)
Memory = 48(3*16)
Locations:
 - loc0 = group_id=1, group_type=1, hkeys=[1], cmu_id=1, memory=((2, 0))
 - loc1 = group_id=1, group_type=1, hkeys=[2], cmu_id=2, memory=((2, 0))
 - loc2 = group_id=1, group_type=1, hkeys=[3], cmu_id=3, memory=((2, 0))

[Success] Allocate TaskID: 1 
```



</details>


<details><summary><b>Dynamic Memory Allocation</b></summary>


</details>

<details><summary><b>Data collection and Task Queries</b></summary>


</details>


## 📏 Simulation Framework

For the convenience of experimentation, we implemented a simulated version of FlyMon in C++ to test algorithms accuracy. Note that the simulation is not a simple implementation of the algorithms with c++. It also uses match-action tables to construct the measurement algorithms, just like the hardware implementation.
In addition, we constructed an automated testing framework to repeat the experiment. The simulation code is located in the [simulations](./simulations) directory.

## Lisense

TODO: we need a lisense.

## Links

* [Open-Tofino](https://github.com/barefootnetworks/Open-Tofino/tree/master/p4-examples/p4_16_programs/tna_dyn_hashing).

