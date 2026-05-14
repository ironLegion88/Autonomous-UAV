# Trade Study 04: Companion Computer, Vision Sensors, and AI Pipeline

**Status:** Finalized  
**Author:** Sarthak Rathi  
**Methodology:** SWaP (Size, Weight, and Power) analysis, software ecosystem compatibility mapping, and computer vision latency modeling.

---

## 1. Introduction & Objectives
In an autonomous object-tracking drone, the Companion Computer (CC) acts as the high-level brain. It is responsible for bridging the flight controller (ArduPilot) to the external world by handling hardware-accelerated video encoding, routing MAVLink telemetry, and executing or forwarding Computer Vision (CV) workloads via ROS 2.

Integrating a CC on a 6-inch multirotor introduces strict **SWaP (Size, Weight, and Power)** constraints. The objective of this trade study is to select a Single Board Computer (SBC) and camera sensor that provide enough compute headroom for the OpenHD digital video pipeline and AI integration, without exceeding the payload capacity or thermal limits of the airframe.

---

## 2. Companion Computer (SBC) Evaluation

The CC must continuously encode 1080p or 720p video to H.264 while managing network protocols. I evaluated several SBCs against the system's 1.5 kg AUW and ~15W avionics power limit.

### 2.1 Hardware Candidates

| SBC Candidate | RAM | Peak Power | Weight (w/o heatsink) | AI Capability | Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Raspberry Pi Zero 2W** | 512 MB | ~2.5 W | 15 g | Very Poor | Rejected (Too weak) |
| **Orange Pi Zero 2** | 1 GB | ~4.0 W | 30 g | Poor | Rejected (Driver issues) |
| **Raspberry Pi 4 Model B**| **4 GB** | **~7.0 W** | **46 g** | **Moderate** | **Selected** |
| **Raspberry Pi 5** | 4-8 GB | ~12.0 W | 46 g | High | Rejected (Software incompat.)|
| **Nvidia Jetson Nano** | 4 GB | ~15.0 W | >140 g | Excellent | Rejected (Too heavy/power hungry) |

### 2.2 Why Not the Pi Zero 2W?
My initial BoM included the Pi Zero 2W to save weight. However, while it *can* run OpenHD, its 512MB of RAM creates a severe bottleneck. Once the OS and OpenHD video encoder allocate memory, there is virtually zero RAM left for running ROS 2 nodes or onboard tracking scripts, leading to system crashes.

### 2.3 The "Pi 5" Software Compatibility Paradox
Logically, the newest and most powerful Raspberry Pi 5 should be the best choice. However, it was explicitly rejected due to **software ecosystem immaturity**. 
OpenHD historically relies on the proprietary Broadcom `MMAL` (Multi-Media Abstraction Layer) pipeline and the hardware H.264 encoder built into the VideoCore IV/VI GPUs of the Pi 3 and Pi 4. The Raspberry Pi 5 completely removed this legacy hardware encoder and shifted to a new software/hardware architecture. Consequently, OpenHD does not officially or stably support the Pi 5 yet.

```mermaid
%%{init: {'theme': 'dark', 'themeVariables': {'fontSize': '14px', 'primaryColor': '#1e1e1e', 'primaryTextColor': '#ffffff', 'primaryBorderColor': '#4a9eff', 'lineColor': '#4a9eff'}, 'flowchart': {'useMaxWidth': true}}}%%
xychart-beta
    title "SBC Power Draw vs. Acceptable Avionics Limit"
    x-axis ["Pi Zero 2W", "Orange Pi", "Pi 4 (4GB)", "Pi 5", "Jetson Nano"]
    y-axis "Peak Power Draw (Watts)" 0 --> 20
    bar [2.5, 4, 7, 12, 15]
    line [10, 10, 10, 10, 10]
```
*(The line at 10W represents the optimal target maximum power draw for a 6-inch quad's CC to preserve flight time).*

**Conclusion:** The **Raspberry Pi 4 (4GB)** is the indisputable "sweet spot." It offers robust OpenHD support via hardware encoding, enough RAM to host ROS 2 middleware, and manageable power/weight profiles.

---

## 3. Vision Sensor Selection (Camera Module)

For computer vision and object tracking, the camera is not just a lens; it is a measurement instrument. The camera must provide a deterministic, low-latency feed.

### 3.1 Pi Camera Module 2 vs. Module 3
*   **Camera Module 3:** Features a 12MP Sony IMX708 sensor, HDR, and **Autofocus**.
*   **Camera Module 2:** Features an 8MP Sony IMX219 sensor and **Fixed Focus**.

While the Module 3 has superior image quality, it was **rejected** for two critical engineering reasons:
1.  **Autofocus Hunting:** In a high-vibration drone environment, autofocus logic constantly "hunts" to maintain sharpness. This introduces non-deterministic latency and blurring, which destroys the bounding-box consistency of object-tracking algorithms (like YOLO). Fixed focus ensures optical consistency.
2.  **Software Stack (`libcamera`):** Camera Module 3 requires the modern `libcamera` stack. As discussed in the SBC evaluation, OpenHD relies on the legacy MMAL video pipeline. `libcamera` integration in OpenHD is currently highly experimental and prone to crashing. 

```mermaid
%%{init: {'theme': 'dark', 'themeVariables': {'fontSize': '14px', 'primaryColor': '#1e1e1e', 'primaryTextColor': '#ffffff', 'primaryBorderColor': '#4a9eff', 'lineColor': '#4a9eff'}, 'flowchart': {'useMaxWidth': true}}}%%
flowchart LR
    subgraph Camera Selection
    Cam3[Camera Module 3] -->|Requires| LC[libcamera Stack]
    LC -->|Breaks| OHD[OpenHD Legacy MMAL]
    
    Cam2[Camera Module 2] -->|Native| MMAL[MMAL / Raspivid]
    MMAL -->|Stable| OHD
    end
    
    style Cam3 fill:#cc3333,stroke:#ff6666,stroke-width:2px,color:#ffffff
    style Cam2 fill:#33cc33,stroke:#00aa00,stroke-width:2px,color:#000000
```

**Conclusion:** The **Raspberry Pi Camera Module 2** was definitively selected. It provides plug-and-play compatibility with OpenHD and ensures a consistent, fixed focal plane for the tracking AI.

---

## 4. Dual-Mode Perception and AI Architecture

With the CC and Camera finalized, the architectural flow of the autonomous tracking system was mapped out. 

Given the computational limits of the Raspberry Pi 4 (which must reserve hardware resources for H.264 video encoding and ROS 2 middleware), a rigid single-architecture approach is a potential point of failure. To maximize flexibility, the software architecture is designed to operate in **two distinct modes**, selectable via ROS 2 launch parameters prior to flight.

### 4.1 Mode 1: Distributed AI (Ground Station Processing)
In this mode, the drone acts as a remote sensor and actuator, offloading heavy computer vision inference to the Ground Station.
*   **Pipeline:** The Pi 4 encodes the camera feed and broadcasts it via OpenHD. The Ground Station (equipped with an RTX 4070 GPU) ingests the stream, runs heavy deep-learning models (like YOLOv8 or YOLOv11), calculates the centroid error, and transmits MAVLink velocity vectors back over the 5GHz link.
*   **Advantages:** Allows for state-of-the-art, high-resolution neural network inference without thermal or CPU throttling on the drone.
*   **Disadvantages:** Introduces round-trip network latency (~120ms to 180ms). If the 5GHz Wi-Fi link degrades, autonomous tracking is immediately lost.

### 4.2 Mode 2: Edge AI (On-board Processing)
In this mode, the drone achieves true autonomy. The Pi 4 intercepts the raw CSI camera frames, splits the pipeline, and processes the AI locally while simultaneously streaming video for human monitoring.
*   **Pipeline:** The Pi 4 runs optimized, lightweight tracking algorithms (e.g., OpenCV CSRT/KCF trackers, color-blob detection, or quantized TFLite models) directly in its RAM. MAVLink velocity commands are sent locally via the physical UART connection to the flight controller. 
*   **Advantages:** **Zero network latency** in the control loop. The drone will continue to track and follow the target even if the OpenHD video link back to the ground station is completely severed or jammed.
*   **Disadvantages:** Limited to lower-resolution frames (e.g., 320x240) and simpler algorithms to prevent CPU max-out and thermal throttling on the Pi 4.

### 4.3 Data Flow Pipeline (State Machine)

```mermaid
%%{init: {'theme': 'dark', 'themeVariables': {'fontSize': '14px', 'primaryColor': '#1e1e1e', 'primaryTextColor': '#ffffff', 'primaryBorderColor': '#4a9eff', 'lineColor': '#4a9eff'}, 'flowchart': {'useMaxWidth': true}}}%%
flowchart TD
    CAM[Pi Camera V2 Raw Frames] --> SPLIT{ROS 2 Mode Selector}
    
    %% MODE 2: On-board AI
    SPLIT -->|Mode 2: Edge AI| ONBOARD[Pi 4: OpenCV / TFLite Node]
    ONBOARD -->|Calculate Centroid| VEL2[Generate Velocity Cmd]
    VEL2 -->|Local UART| FC[SkyStars H7 Flight Controller]
    
    %% MODE 1: Ground Station AI
    SPLIT -->|Mode 1: Distributed| ENC[Pi 4: H.264 Encoder]
    ENC -->|5GHz Wi-Fi| GS[Ground Station RTX 4070]
    GS -->|YOLOv8 Inference| VEL1[Generate Velocity Cmd]
    VEL1 -->|5GHz Wi-Fi| FC
    
    %% Monitoring
    ONBOARD -.->|Background Task| ENC
    
    style ONBOARD fill:#4ac485,stroke:#7cffb3,stroke-width:2px,color:#000000
    style GS fill:#f9a873,stroke:#ffbc7a,stroke-width:2px,color:#000000
```

---

## 5. Conclusion
The selection of the **Raspberry Pi 4 (4GB)** and the **Pi Camera Module 2** represents the safest, most reliable path for achieving a digital video link on a research drone. By respecting the software limitations of the OpenHD ecosystem and adopting a **Dual-Mode AI architecture**, the platform is incredibly versatile. It can leverage Ground Station GPUs for complex neural network research (Mode 1), while retaining the capability to run hard real-time, RF-independent tracking algorithms directly on the edge (Mode 2). This architecture minimizes thermal output while maximizing mission reliability.