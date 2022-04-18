# Boilr

Water boiler automation with a Fronius pv inverter on a Raspberry Pi.

The goal was to use the overproduction of the PV system and increase the self consumption during daytime by heating water. By doing that, you decrease the amount of energy supplied to the grid, but also reduce consumption of pellets, oil or other fuel for heating.

That's the basic idea of this project. But what about special cases like an already running heater? Or taking away power generated from the pv and you have to use power from the grid to use the stove?
I don't know, I don't care. Just wanted to do this in my spare time. Otherwise I would have wasted the time invested in this project by watching Netflix or Youtube.

![sufficiency over one day](./docs/sufficiency.jpg)
The yellow area shows the own consumption of the produced energy after using Boilr (this program) to increase self-sufficiency. The blue line is the overall energy consumption. The gray area shows produced energy that is fed into the grid. The green line is the charging level of the battery in percent, whereas the green area shows the produced energy fed into the battery.

![self-sufficiency example](./docs/fronius.jpg)
Here you can see that all the energy from the pv system is either used to charge the battery or consumed directly (all electrical consumer + heating element of the water heater)

If you are not comfortable with the electrical part, call an electrician, because it can definitely kill you. Although, things like networking and connecting the raspberry to the relay shouldn't be that hard.

## Additional Downloads

- Fronius official API documentation: [Documentation - Fronius Solar API V1](https://www.fronius.com/~/downloads/Solar%20Energy/Operating%20Instructions/42%2C0410%2C2012.pdf)
- Postman request collection: [Postman Collection - Fronius Solar API V1](https://www.getpostman.com/collections/27c663306206d7fbf502)

## Setup

### Containerised (recommended)

1. Build image (on Raspberry Pi)
   - `docker-compose build`
1. Run app in container
   - `docker-compose up -d`

#### Notes

In order to install and use Docker on a Raspberry Pi 1 Model B I had to set `sysctl vm.overcommit_memory=1` and restart after the installation.

### cli

1. Install python3
   - `sudo apt install python3 python3-venv`
1. Clone the repo
   - `git clone https://github.com/PeterBrain/boilr.git boilr`
   - `cd boilr`
1. Create a virtual environment (not not... it's up to you) & activate it
   - `python3 -m venv venv`
   - `source venv/bin/activate`
1. Install all requirements
   - `pip install -r requirements.txt`
1. Create boilr folder in /var/log
   - `mkdir /var/log/boilr`
1. Create boilr.log file in /var/log/boilr
   - `touch /var/log/boilr/boilr.log`
1. Edit configfile to your needs
   - `vi boilr/config.py`

## Usage

Starting:

```bash
python3 -m boilr start
```

Stopping:

```bash
python3 -m boilr stop
```

Others:

```bash
python3 -m boilr [-h] [-v] {start,stop,status,restart,run,manual {0,1}}
```

Complete guide (boilr -h):

```bash
usage: boilr [-h] [-v] {start,stop,status,restart,run,manual} ...

Water boiler automation with a Fronius pv inverter on a Raspberry Pi.

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         log extra information

commands:
  {start,stop,status,restart,debug,manual}
    start               Starts boilr daemon
    stop                Stops boilr daemon
    status              Show the status of boilr daemon
    restart             Restarts boilr daemon
    run                 Starts boilr in command line
    manual              Manually override gpio channel (contactor)

Additional hardware required. Please check:
https://github.com/PeterBrain/boilr
```

<!-- for later
```bash
python3 setup.py
```
-->

## Requirements

### Software

- Raspberry Pi with operating system (i use the 1B with a headless raspbian)
- Python 3 (tested with 3.9)
- some python packages
- Docker

### Hardware

Here is a list of all parts I used:

- contactor to switch the three phases AC (~20€)
- 5x1.5mm2 copper stranded cable (~10€)
  - ferrules (only if you have stranded wires)
- circuit breaker (had one laying around, but around 20€)
- distribution box (~20€)
- Raspberry Pi 1B (used for about 5€) + an sd card for the os (laying around)
- relay for the pi (5pcs for 8€, but we need only one)
- ethernet cable (had an old one at home (Cat5 - not even Cat5e))
- network switch (used, gigabit (overkill) around 5-10€, or an old router with a builtin switch for free)

I could have used an wifi dongle instead of an ethernet cable, but the signal strengh in my cellar (where the water boiler is) is somewhat inexistent. Plus, the pv inverter (already connected via lan) is also there.

Inside | Outside
:-----:|:-------:
![inside view](./docs/inside.JPG) | ![outside view](./docs/outside.JPG)

You can judge me for that second schuko socket, because I messed up and didn't think about the lid of the distribution box. The lid does not close if there is anything plugged into the schuko socket on the hut rail. Thats why there is a second one inside the box.

## Cost analysis

It took me three days to each six hours, to get the software up and running (3days x 6h = 18h). PayScale rates the average salary for an software engineer at 15.50€ per hour in Austria. Let me just do the math real quick (24hours * 15.50€/hour = 279€). Just shy of 300€ for a simple program. BTW, i am just a beginner in python.

Now for the electrical installation part. An electrician gets 22.30€ per hour (rate also from Payscale for Austria). I am not that routined like a real electrician, but I managed to get it done in two hours. Quic mafs: (2hours * 22.30€/hour = 44.60€). With a little bit of rounding, we settle at 50€. My calculation is without all the extra stuff we would have to pay for the electrician, because that is the salary he would get for this job, and not what we would pay for it. From experience it would cost about 50-80€ per hour (without material)!

So, 300€ for the software and 50€ for the electical installation? Kind of, but with very optimistic calculated installation costs.

## Weaknesses

This current design has a major drawback: Unlike Ohmpilot, a comparable product from Fronius with a much higher efficiency thanks to PWM, my installation has only two states. It's either on (with full power to the heating coil), or off. This most efficiency here is lost on days where pv production barely isn't enough to provide the current consumption of the house plus heating water.

