# SURGE-2024
Anti-Spoof Fingerprint 

# Raspberry Pi Fingerprint Sensor and Anti spoof Detection 

This Python script is part of a research project conducted by Team X under the supervision of Professor Tushar Sandhan during the summer internship. The project focuses on integrating a fingerprint sensor with an RGB display using a Raspberry Pi, combining hardware interfacing, fingerprint operations, and machine learning for enhanced security.

## Abstract

The project involves implementing a machine learning model designed to de-
tect spoofing attempts, deployed on a Raspberry Pi hardware setup. The model
analyze fingerprint images using innovative techniques like Ten Crop patch and
crop processing. This approach not only expands the dataset but also enables
the model to develop a keen eye for detail, effortlessly distinguishing genuine
fingerprints from clever forgeries

## Project Details

- **Project Title**: Integrating Fingerprint Sensor with RGB Display for Security Applications and Anti-Spoof Detection
- **Proffessor**: Professor Tushar Sandhan

- **Project Team**: Fingerprint Team

  - Tejasri
  - Sritan
  - Sanya
  - Prateek
  - Naina
  - Riddhima

- **Mentors**:
   - Aman
   - AjaySingh
   - Adarsh

## Project directory Structure
```
SURGE/
│
├── README.md
|
├── src/
│   |__fingerprint_sensor_display.py
│   
├── images/
│   ├── image1.jpg
│   └── image2.png
│
└── requirements.txt
```


## Requirements

### Hardware Requirements

- Raspberry Pi: Tested on Raspberry Pi 3 Model B+
- Fingerprint Sensor: Compatible with `PyFingerprint` library, connected via UART (`/dev/ttyUSB0`)
- Adafruit RGB Display: ST7735R, connected via SPI

### Software Requirements

- Python 3.x
- Python Libraries (Install via `pip install -r requirements.txt`):
  - `RPi.GPIO`: GPIO control for Raspberry Pi
  - `Pillow`: Image processing operations
  - `pyfingerprint`: Interface with the fingerprint sensor
  - `torch`, `torchvision`: Machine learning framework and models
  - `adafruit-blinka`: CircuitPython GPIO library compatibility layer

### Development Environment

- Operating System: Recommended on Raspberry Pi OS (formerly Raspbian)
- Virtual Environment: Create and activate a virtual environment for Python dependencies.

## Setup

### Virtual Environment Setup

1. **Create a Virtual Environment**:

   - Open your terminal or command prompt.
   - Navigate to your project directory:

     ```bash
     cd path/to/your/project
     ```

   - Create a new virtual environment (replace `venv` with your preferred name):
     - For Windows:

       ```bash
       python -m venv venv
       ```

     - For macOS and Linux:

       ```bash
       python3 -m venv venv
       ```

2. **Activate the Virtual Environment**:

   - Activate the virtual environment:
     - For Windows:

       ```bash
       venv\Scripts\activate
       ```

     - For macOS and Linux:

       ```bash
       source venv/bin/activate
       ```

### Installing Dependencies

3. **Install Dependencies**:

   - Install required Python libraries using `pip` with `requirements.txt`:

     ```bash
     pip install -r requirements.txt
     ```

4. **Configure Hardware**:

   - Connect the fingerprint sensor to the Raspberry Pi via UART (`/dev/ttyUSB0`).
   - Connect the Adafruit RGB display to the Raspberry Pi using SPI.

5. **Configure Script**:

   - Adjust GPIO pin numbers (`BUTTON_PINS`) and display pins (`cs_pin`, `dc_pin`, `reset_pin`, `led_pin`) in the Python script (`fingerprint_sensor_display.py`) based on your hardware setup.

6. **Run Script**:
    ```bash
    python fingerprint_sensor_display.py
    ```
 Follow the instructions as displayed on the LCD.

## Visuals

### Complete Setup

![display](https://github.com/sanya22-hub/SURGE-2024/assets/130730788/89563ff1-b8b3-4ea9-8c8b-d4776916b23f)

*Caption: Example caption describing the complete setup of the Raspberry Pi, fingerprint sensor, and RGB display integrated into a compact device.*

## Functionality

- **Enroll Finger**: Allows users to enroll new fingerprints into the system.
- **Delete Finger**: Deletes existing fingerprints from the sensor's database.
- **Anti-Spoof Guard**: Toggle feature to enable or disable spoof detection using machine learning.
- **Search Finger**: Searches for a fingerprint match in the system's database.(searches continuosly)
- **Back**:Return to main menu.


## Functionality of Push Buttons

The Python script `fingerprint_sensor_display.py` utilizes push buttons connected to the Raspberry Pi GPIO pins for user interaction. Here's a brief overview of their functionality:

- **Button 1**: Enrolls a new fingerprint into the system.
- **Button 2**: Deletes an existing fingerprint from the sensor's database.
- **Button 3**: Toggles the anti-spoof guard feature, enabling or disabling spoof detection using      machine learning.
- **Button 4**: Returns to the main menu after performing an operation or during idle states.

These buttons are configured using the RPi.GPIO library in the script. Each button press triggers specific functions related to fingerprint operations, display updates, and system configurations.

## Dataset

- **CrossMatch**,**Greenbit** are used for cooperative framework.

## Acknowledgement

We would like to express our sincere gratitude to **Professor Tushar Sandhan** for his invaluable guidance and support throughout this project. Special thanks to our mentors,**Aman**, **Ajay Singh**, and **Adarsh**, for their feedback which greatly contributed to the success of this project.

## Notes

- Due to patent rights, the spoof detection algorithm's details and accuracy metrics cannot be disclosed.
- The compact device housing the entire setup was fabricated using 3D printing for robustness and integration.
