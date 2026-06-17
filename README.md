# ROS2-RFID-reader
Documentation for a ROS2 based RFID reader system for robot tool holders. Upon request, the system reads and sends the RFID tag from a tool held in one of several designated tool holders. 
This project uses PN-532 NFC RFID V3 Readers mounted on robot tool holders to indetiffy different tools based on their unique tag.

# Prerequisites

### 1. Hardware Configuration
* Raspberry Pi4 (with ROS2 installed)
* PN532 NFC RFID V3
* SPI interface must be enabled on the Raspberry Pi. Run `sudo raspi-config`, navigate to **Interface Options -> SPI**, and enable it.

### 2. Required System Libraries
The script uses `RPi.GPIO` to handle multiple Chip Select (CS) pins:
```bash
sudo apt-get update
sudo apt-get install python3-rpi.gpio
```
### 3. Required pip3 and lgpio
```
apt update && apt install -y python3-pip
apt-get update && apt-get install -y python3-lgpio

```

### 4. Required Python Packages
The internal hardware drivers require Python's native SPI interaction layer:
```bash
pip3 install spidev
```

# Wiring
**IMPORTANT** Since the system works using SPI, make sure the selector switches on all PN532 modules are set to SPI:
|ON|KE|
|----|-----|
|0 (down)|1 (up)|

Since the readers share most pins, for the sake of clarity, these shared pins are presented in the table bellow, while the pins speciffic for each reader are displayed in the second table.

|RFID reader| Pi4 pin  |
|----|-----|
|SCK | 23  |
|MISO| 21  |
|MOSI| 19  |    
|VCC | 2   |
|GND | 14  |

The following table explains how to connect the SS pins of individual RFID readers to the raspberry pi pins. The number under RFID reader is the identiffying number of the reader/hodler itself. 
Note that it is very easy to change which reader should be connected to which pin by editing the defined GPIO pin in the rfid_service.py 

|RFID reader| Pi4 pin  | GPIO  |
|----|-----|-----|
|1.  |**3**|2|
|2.  |**5**|3|
|3.  |**7**|4|   
|4.  |**11**|17|
|5.  |**13**|27|
|6.  |**15**|22|
|7.  |**8**|14|
|8.  |**10**|15|
|9.  |**18**|18|
|10. |**16**|23|
|11. |**18**|24|
|12. |**22**|25|
|13. |**28**|1|   
|14. |**32**|12|
|15. |**36**|16|
|16. |**38**|20|
|17. |**40**|21|
|18. |**27**|0|
|19. |**29**|5|
|20. |**31**|6|
|21. |**33**|13|
|22. |**35**|19|
|23. |**37**|26|

The raspberry pi4 should also be connected to a power supply as well as your network via a LAN cable. 
# Installation

### 1. Create a Workspace (If you don't have one)
```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src
```

### 2. Clone the Repository
Navigate to your workspace source (`src`) directory and clone this package directly from GitHub:
```bash
cd ~/ros2_ws/src
git clone https://github.com/Mesha-M/RFID-reader.git RFID_reader
```

### 3. Compile the Package
Navigate back to the root of your workspace and use colcon to build the RFID package:
```bash
cd ~/ros2_ws
colcon build --packages-select RFID_reader
```

### 4. Source the Overlay
```bash
source install/setup.bash
```

# Use
### 1. Running the RFID Node
Launch the RFID service node with the following command:
```bash
ros2 run RFID_reader rfid_node
```
Upon a successful connection, you will see the console log confirmation messages for each active reader defined in your GPIO configuration (e.g., `Reader [Holder_1] ready on CS GPIO 2`).

### 2. Interfacing via ROS2 Services
The package exposes two types of services for interacting with your RFID array. Open a separate terminal window(You can do it on a different computer in the same LAN network), source your workspace (`source ~/ros2_ws/install/setup.bash`), and run:

#### Scan All Readers Simultaneously
Triggers a synchronized read across every configured holder channel:
```bash
ros2 service call /scan_all std_srvs/srv/Trigger
```
* **Expected Response:** A combined string list matching the reader tags: `success=True, message="Holder_1:0x4-0x8a-...|Holder_2:No tag"`

#### Scan a Specific Reader Channel
Triggers a read on exactly one target holder:
```bash
ros2 service call /scan_one/Holder_1 std_srvs/srv/Trigger
```

---

## Modifying Pins (Optional)

### Adding/removing readers:
The system supports up to 23 readers, but since so many probably will not be needed, the preset is for 6 readers. This can be easily changed by opening `RFID_reader/rfid_service.py` and adding more holders by uncommenting the code for the needed holders. Alternativelly, you can remove unnecessery readers by commenting their respective line:

```
READER_CONFIG = {
    'Holder_1': 2,
    'Holder_2': 3,
    'Holder_3': 4,
    'Holder_4': 17,
    'Holder_5': 27,
    'Holder_6': 22,
#    'Holder_7': 14,
#    'Holder_8': 15,
#    'Holder_9': 18,
}
```
### Assigning pins to readers
If you want to change which reader/holder is on which pin, open `RFID_reader/rfid_service.py` and modify the mapping dictionary. For example, changing Holder 1 pin from pin 2 to pin 18:
```python
READER_CONFIG = {
    'Holder_1': 18,
    'Holder_2': 3,
}
```
*Note: Always run `colcon build --packages-select RFID_reader` after editing the Python code to update the installation workspace.*
