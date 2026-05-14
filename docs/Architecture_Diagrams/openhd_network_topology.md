```mermaid
flowchart LR
    %% Styles
    classDef drone fill:#eef2f3,stroke:#457b9d,stroke-width:2px
    classDef ground fill:#fdfcdc,stroke:#e07a5f,stroke-width:2px
    classDef antenna_5g fill:#d4f9d8,stroke:#2a9d8f,stroke-width:2px,stroke-dasharray: 5 5
    classDef antenna_2g fill:#f9d0c4,stroke:#e63946,stroke-width:2px,stroke-dasharray: 5 5

    subgraph Drone [UAV Airframe Architecture]
        direction TB
        PI[Raspberry Pi 4] <-->|USB| WIFI_AIR[RTL8812EU Module]
        FC[SkyStars H7] <-->|UART| ELRS_RX[RP4TD-M Receiver]
        
        WIFI_AIR --> ANT_A1((5GHz Dipole<br>Vertical Mount)):::antenna_5g
        WIFI_AIR --> ANT_A2((5GHz Dipole<br>Horizontal Mount)):::antenna_5g
        
        ELRS_RX --> ANT_E1((2.4GHz T-Antenna)):::antenna_2g
    end

    subgraph RF Link [Wireless Propagation]
        direction TB
        L1{OpenHD Video + MAVLink<br>5.8 GHz Band<br>MIMO Broadcast}
        L2{Manual RC Override<br>2.4 GHz Band<br>CRSF Protocol}
    end

    subgraph GroundStation [Ground Station Architecture]
        direction TB
        WIFI_GND[RTL8812EU Module] <-->|USB| PC[Ubuntu AI Laptop]
        TX[Radiomaster TX Pocket]
        
        ANT_G1((5GHz 14dBi Patch<br>Directional)):::antenna_5g --> WIFI_GND
        ANT_G2((5GHz 5dBi Omni<br>Close-Range)):::antenna_5g --> WIFI_GND
        
        TX --> ANT_E2((2.4GHz Omni)):::antenna_2g
    end

    %% Connections
    ANT_A1 <-.-> L1
    ANT_A2 <-.-> L1
    L1 <-.-> ANT_G1
    L1 <-.-> ANT_G2

    ANT_E1 <-.-> L2
    L2 <-.-> ANT_E2

    %% Separation Note
    note1>Critical Design Rule: Physical Separation >15cm between 5GHz and 2.4GHz antennas on Airframe]
    Drone -.-> note1

    class Drone drone
    class GroundStation ground
```