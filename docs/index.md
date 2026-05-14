# Autonomous Long-Endurance 6-Inch Research UAV

**Status:** System Architecture Finalized | Simulation Framework Drafted | Hardware 80% Assembled  
**Methodology:** Systems Engineering, Digital Twin Modeling, and Theoretical Trade Studies  

## Executive Summary
This repository documents the end-to-end systems engineering, component analysis, and architectural design of a 6-inch autonomous quadcopter. The platform is engineered to bridge the gap between high-agility FPV multirotors and long-endurance autonomous research drones. 

Due to strict 2.5-month project timeline constraints, this project utilizes a **Systems Engineering and Digital Twin methodology**. Before any physical electrical integration or flight testing was conducted, the entire powertrain, electrical load, software pipeline, and simulation scaffolding were rigorously modeled using component datasheets, thrust tables, and industry data. The physical airframe has been mechanically assembled as a validation of the 3D-printed structural design and component packaging, with electrical integration and maiden flights slated for future work.

## Project Objectives
1. **Endurance:** Design a powertrain capable of 15–30 minutes of sustained flight using Li-ion battery chemistry (4S1P/4S2P).
2. **Dual-Mode Autonomy:** Integrate a Raspberry Pi 4 companion computer to run ROS 2 nodes capable of executing a dual-mode AI pipeline: 
   * **Mode 1 (Distributed):** Streaming video to a Ground Station GPU for heavy neural network processing (e.g., YOLOv8).
   * **Mode 2 (Edge AI):** Running lightweight object tracking algorithms natively on the Pi 4 for true, RF-independent autonomy.
3. **Digital HD Pipeline:** Utilize OpenHD over 5GHz Wi-Fi for low-latency digital video and bi-directional MAVLink telemetry without relying on closed-source ecosystems (e.g., DJI).
4. **Digital Twin:** Establish a Gazebo (Harmonic) + ROS 2 + ArduPilot SITL simulation environment native to Ubuntu 22.04 for Reinforcement Learning (RL) and tracking algorithm training.

## Hardware Architecture
The hardware was selected after extensive trade-off studies evaluating compute load, flash memory limits, aerodynamic efficiency, and structural resonance.

| Subsystem | Component | Rationale (Brief) |
| :--- | :--- | :--- |
| **Flight Controller** | SkyStars H7 Dual Gyro + KM60 ESC | 2MB Flash for full ArduPilot support; superior I/O for peripherals compared to F405 boards. |
| **Propulsion** | Emax ECO II 2807 1500KV | High stator volume provides massive torque at low RPMs, required for 6-inch endurance. |
| **Propellers** | Gemfan LR 6026-2 (Bi-Blade) | Lowest aerodynamic drag; offers 20-30% efficiency gain over 5" tri-blades for cruise. |
| **Companion Compute** | Raspberry Pi 4 (4GB) | Required for OpenHD encoding and ROS 2 workloads. (Replaced Pi Zero 2W due to thermal/CPU limits). |
| **Vision & Comms** | Pi Camera V2 + RTL8812EU Wi-Fi | OpenHD integration. V2 camera selected to avoid autofocus latency and `libcamera` compatibility issues. |
| **Control Link** | Radiomaster RP4TD-M (ELRS) | True diversity 2.4GHz CRSF link for unbreakable manual override safety. |
| **Primary Power** | 4S1P 21700 Li-ion (4500mAh) | Balances high discharge (45A) with excellent energy density. *Note: Frame is currently built for 4S1P, with 4S2P mathematically modeled as a future upgrade.* |

## Repository Structure
```text
Project-Endurance-UAV/
├── README.md                           # Project overview and executive summary
├── docs/                               # Engineering documentation and research
│   ├── Trade_Studies/                  # Deep-dive component and architectural analyses
│   │   ├── 01_Propulsion_and_Endurance.md
│   │   ├── 02_Flight_Controller_Stack.md
│   │   └── 03_Companion_Computer_AI.md
│   ├── Architecture_Diagrams/          # Visual schematics (Electrical & Software)
│   └── Power_Consumption_and_Budget.md # Complete electrical load and flight time models
├── hardware_cad/                       # Physical design files
│   ├── frame_assemblies/               # 3D printable files (STLs) and structural analysis
│   └── custom_mounts/                  # Antenna, Pi 4, and Camera TPU mounts
└── simulation_ws/                      # Native Ubuntu 22.04 ROS 2 & Gazebo Workspace
    ├── src/
    │   ├── uav_description/            # SDF models with calculated mass and inertia matrices
    │   └── uav_gazebo/                 # ArduPilot SITL and Gazebo launch files
```

## Software Stack
* **OS:** Native Ubuntu 22.04 LTS (Desktop & Raspberry Pi)
* **Middleware:** ROS 2 Humble Hawksbill
* **Simulation:** Gazebo Harmonic + ArduPilot SITL
* **Autopilot Firmware:** ArduPilot (Copter)
* **Telemetry & Video:** OpenHD (H.264 encapsulation via Wi-Fi Broadcast)

## Current Status & Future Work
**Completed:**
* Comprehensive Component Trade Studies
* Power Budgeting and Flight Time Mathematical Modeling
* ROS 2 / Gazebo Architecture Planning
* Mechanical Assembly of 3D-Printed Airframe and Motors

**Pending / Future Scope:**
*  **Electrical Integration:** Soldering the final power harness, including the XL4015 buck converter and LC filters to isolate the Raspberry Pi from ESC electrical noise.
*  **Simulation Validation:** Tuning the ROS 2 PID control loops for autonomous object tracking inside the Gazebo environment.
*  **Maiden Flight:** Physical hover testing, ArduPilot compass calibration, and OpenHD range testing.