# Final Project Report: Design and Architecture of a High-Endurance Autonomous UAV

**Project Title:** Development of a High-Fidelity Digital Twin and Autonomous Control Framework for a 6-Inch Research Quadcopter  
**Author:** Sarthak Rathi  
**Course:** Independent Study Module (ISM) - Robotic Design Simulation  
**Project Status:** System Architecture Finalized, Simulation Scaffolding Complete, Hardware Mechanically Assembled.  

---

## 1. Abstract
This report details the end-to-end systems engineering of a 6-inch autonomous multirotor platform capable of real-time computer vision and object tracking. Constrained by a 2.5-month timeline, the project was executed using a "Digital Twin" methodology. Rather than engaging in ad-hoc physical prototyping, rigorous trade-off studies, aerodynamic modeling, and power budgeting were conducted to finalize the architecture. A native Ubuntu 22.04 simulation environment (Gazebo Harmonic + ROS 2 + ArduPilot SITL) was established to validate the control theory. At the conclusion of this ISM, the physical drone is 80% mechanically assembled, with the electrical integration and physical flight testing clearly mapped out for future deployment.

## 2. Project Objectives
The overarching goal was to design a robust base platform that breaks away from the limitations of traditional, low-endurance FPV racing drones, creating instead a reliable tool for autonomous robotics research. The primary objectives were:
1. **Endurance:** Achieve 25–30 minutes of sustained flight using Li-ion chemistry, capable of carrying a ~25W avionics payload.
2. **Dual-Mode Autonomy:** Design a software pipeline capable of both *Distributed AI* (streaming video to a ground station GPU for heavy neural networks) and *Edge AI* (running lightweight tracking natively on the drone).
3. **Digital HD Pipeline:** Implement a digital video and telemetry link using OpenHD (802.11a/n/ac) to avoid the closed-ecosystem bottlenecks of proprietary digital FPV systems.
4. **Digital Twin Integration:** Build a simulated replica of the drone to safely train object-tracking algorithms prior to hardware deployment.

---

## 3. Systems Engineering and Trade Studies
Because physical testing was deferred to ensure architectural perfection, the project relied heavily on theoretical modeling. The following critical engineering decisions were formulated:

### 3.1 Propulsion and Aerodynamics
Standard 5-inch drones prioritize peak burst thrust, yielding flight times under 7 minutes. To achieve long endurance, the design philosophy shifted to minimizing continuous power draw during steady-state hover.
*   **Propeller Geometry:** 5-inch tri-blade propellers were rejected due to high parasitic drag and inefficient disk loading for a 1.5kg drone. The platform utilizes **Gemfan LR 6026-2 (6-inch bi-blades)**, which provide up to a 30% theoretical efficiency gain in cruise conditions.
*   **Motor Sizing:** Initially, 2306 1750KV motors were considered. However, torque modeling revealed that small stators draw excessive current attempting to swing 6-inch propellers at low RPMs. The **Emax 2807 1500KV** motor was selected; its massive stator volume provides the low-end torque required for highly efficient hover states.
*   **Energy Storage:** High-discharge LiPo batteries (100C) were rejected in favor of high-energy-density **21700 Li-ion cells**. While the physical drone is currently sized for a 4S1P (4500mAh) pack, mathematical modeling confirms that a 4S2P (10,000mAh) pack yields the optimal 30-minute endurance target.

### 3.2 Avionics and Flight Controller Constraints
Running autonomous navigation firmware (ArduPilot) on compact 30x30mm hardware introduces severe silicon constraints.
*   Budget FPV controllers (e.g., STM32F405) are limited to 1MB of Flash memory, forcing the use of feature-stripped firmware targets. 
*   The **SkyStars H7 Dual Gyro FC** was selected. The STM32H7 processor provides 2MB of Flash and a 480MHz clock speed, offering immense compute headroom for ArduPilot’s Extended Kalman Filter (EKF3) and redundant sensor logging.

### 3.3 Communications and RF Architecture
Autonomous computer vision requires a pristine digital video feed; analog composite video is too noisy for deterministic edge detection. 
*   **Video & Data:** **OpenHD** was selected, utilizing the RTL8812EU Wi-Fi chipset over the 5GHz band. This allows H.264 video and bi-directional MAVLink telemetry to be broadcast to the ground station.
*   **Control Link:** Relying on a Linux-based Wi-Fi pipeline for flight control introduces unacceptable latency and reliability risks. An independent **ExpressLRS (ELRS) 2.4GHz** control link (Radiomaster RP4TD-M True Diversity) was integrated to guarantee hardware-level manual override capabilities.

### 3.4 Companion Compute and Vision
The **Raspberry Pi 4 (4GB)** was selected as the optimal Companion Computer (CC). Lighter alternatives (Pi Zero 2W) lacked the RAM required for ROS 2, while the newer Pi 5 was rejected due to its lack of hardware H.264 encoding support in the OpenHD ecosystem. The **Pi Camera Module 2** was chosen over the newer Module 3 because its fixed focus prevents autofocus "hunting," which introduces fatal jitter into bounding-box tracking algorithms.

### 3.5 Structural Integrity and Resonance
The 3D-printed nature of the frame necessitated careful material selection. Flexible filaments (PETG/PLA) deform elastically under thrust. This induces high-frequency micro-oscillations that alias into the flight controller's gyroscopes. The PID loop attempts to correct these vibrations, surging the motors and dissipating up to 20% of the battery’s energy as heat. To prevent this, the frame architecture mandates highly rigid thermoplastics like **ASA** or **PA6-CF (Carbon Fiber Nylon)**.

---

## 4. Digital Twin and Simulation Scaffolding
To validate the control loops without risking hardware, a ROS 2 Software-In-The-Loop (SITL) architecture was designed.

1.  **Environment:** A native Ubuntu 22.04 workspace utilizing **Gazebo Harmonic**. Gazebo was prioritized over Unreal Engine 5 for Phase 1 due to its native integration with ROS 2 and ArduPilot.
2.  **Mathematical Modeling:** A custom SDF (`drone.sdf`) was written. The mass ($m = 1.50 \text{ kg}$) and the inertia tensor matrices ($I_{xx}, I_{yy}$) were mathematically extrapolated from the physical CAD models. Matching the simulated inertia to the physical drone ensures that PID velocity tuning transfers smoothly to the real world (Sim-to-Real transfer).
3.  **Control Node:** A Python-based ROS 2 visual servoing node was developed. It translates bounding-box centroid errors (simulating a YOLO detection output) into proportional `geometry_msgs/Twist` velocity commands, which are routed to ArduPilot via MAVROS.

---

## 5. Current Physical Build Status
The project has successfully transitioned from the theoretical domain to the physical assembly phase.
*   **Mechanical Assembly:** The ASA/PETG airframe, 2807 motors, SkyStars ESC/FC stack, and Raspberry Pi 4 have been mechanically mounted.
*   **Electrical Status (Pending):** Electrical integration is currently halted. The theoretical wiring schematic is finalized, utilizing an XL4016 Buck Converter and a RushFPV LC Filter to safely power the Raspberry Pi and Wi-Fi module from the 6S battery without inducing voltage sags or brown-outs on the flight controller.

---

## 6. Conclusion and Path to Deployment
This Independent Study Module successfully yielded a highly optimized, research-grade UAV architecture. By rigorously analyzing component datasheets, power budgets, and silicon limitations prior to assembly, the design completely avoids the common pitfalls of DIY autonomous drones (such as payload brown-outs, RF desensitization, and flex-induced efficiency loss).

**Future Work:**
1.  **Electrical Integration:** Execute the finalized wiring schematic, ensuring proper grounding and isolation of the 5V avionics rail.
2.  **Firmware Flashing:** Flash ArduPilot Copter to the SkyStars H7, and configure the UART routing for OpenHD and ELRS.
3.  **Simulation Validation:** Finalize the tuning of the ROS 2 PID visual servoing nodes within Gazebo.
4.  **Maiden Flight:** Conduct physical hover testing, followed by the deployment of the distributed AI tracking pipeline.