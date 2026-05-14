```mermaid
flowchart TD
    %% Define Styles
    classDef power_high fill:#f9d0c4,stroke:#e63946,stroke-width:2px,color:#000
    classDef power_low fill:#ffe8d6,stroke:#f4a261,stroke-width:2px,color:#000
    classDef avionics fill:#d4e1f9,stroke:#1d3557,stroke-width:2px,color:#000
    classDef flight fill:#d4f9d8,stroke:#2a9d8f,stroke-width:2px,color:#000
    classDef actuator fill:#e9c46a,stroke:#e76f51,stroke-width:2px,color:#000

    %% Main Power Source
    BAT["4S Li-ion Battery (14.8V-16.8V)"]:::power_high

    %% Splitting the Main Power
    BAT -->|12 AWG| ESC_P["KM60 60A 4-in-1 ESC"]:::power_high
    BAT -->|16 AWG| BUCK["XL4015 Buck Converter (Set to 5.1V)"]:::power_high
    
    %% ESC Decoupling
    CAP["1000uF 50V Low-ESR Capacitor"]:::power_high
    ESC_P -.- CAP

    %% Avionics Power Regulation (5V Rail)
    BUCK -->|5V / GND| FILTER["RushFPV Blade LC Filter"]:::power_low
    FILTER -->|Clean 5V| PI_RAIL(("5V Avionics Power Rail")):::power_low

    %% Avionics Power Distribution
    PI_RAIL -->|GPIO 5V / GND| PI["Raspberry Pi 4 (Companion PC)"]:::avionics
    PI_RAIL -->|VCC / GND| WIFI["BL-M8812EU2 Wi-Fi Module"]:::avionics

    %% Flight Controller Power & DShot
    ESC_P -->|Current Sensor / VBAT| FC["SkyStars H7 Dual Gyro FC"]:::flight
    ESC_P -->|DShot600| MOTORS["4x Emax 2807 1500KV Motors"]:::actuator

    %% Peripheral Data Routing
    FC <-->|UART / I2C| GPS["HGLRC M100 Pro GPS + Compass"]:::flight
    FC <-->|UART #40;CRSF#41;| ELRS["Radiomaster RP4TD-M Receiver"]:::flight
    PI <-->|UART #40;TX to RX, RX to TX#41;| FC
    
    %% Camera & Wi-Fi Data
    CAM["Pi Camera Module V2"]:::avionics -->|CSI Ribbon Cable| PI
    PI <-->|USB D+ / D-| WIFI

    %% Subgraphs for visual grouping
    subgraph Propulsion System
        ESC_P
        CAP
        MOTORS
    end

    subgraph Avionics Power & Compute
        BUCK
        FILTER
        PI_RAIL
        PI
        WIFI
        CAM
    end

    subgraph Flight Control & RF
        FC
        GPS
        ELRS
    end
```