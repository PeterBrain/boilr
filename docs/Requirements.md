# Requirements

## Software

- Raspberry Pi with operating system (tested with Model 1B and headless Raspbian)
- Python 3 (tested with 3.10)
- Some python packages
- Docker (optional, but recommended)
- MQTT Broker (optional, but recommended)

## Hardware

List of all parts I used:

- Distribution box
- Circuit breaker (3-phase AC)
- Contactor to switch the three phases AC
- 5x1.5mm2 copper stranded cable
  - Ferrules (for stranded wires)
- Raspberry Pi 1B + sd card
- Relay for the pi
- Network switch & Ethernet cable
- Fronius PV inverter
  - Fronius PV Battery (optional - Boilr will work just fine without a battery)

### Electrical installation example

Inside | Outside
:---:|:---:
![inside view][installation-example-inside] | ![outside view][installation-example-outside]

Unfortunately, the lid cannot be closed when there's something plugged into the power outlet on the hut rail. Thats why there is a second power outlet inside the distribution box.

> [!WARNING]
> If dealing with the electrical aspect isn't within your comfort zone, it's advisable to seek assistance from an electrician, as mishandling it can pose serious risks.


[installation-example-inside]: ../docs/inside.JPG
[installation-example-outside]: ../docs/outside.JPG
