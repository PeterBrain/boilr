# Boilr

Water boiler automation with a Fronius pv inverter on a Raspberry Pi.

The goal was to use the overproduction of the PV system and increase the self consumption during daytime by heating water. By doing that, you decrease the amount of energy supplied to the grid, but also reduce consumption of pellets, oil or other fuel for heating.

That's the theory. But what about special cases like an already running heater? Or taking away power generated from the pv and you have to use power from the grid to use the stove?
I don't know, I don't care. Just wanted to do this in my spare time. Otherwise I would have wasted the time invested in this project by watching Netflix or Youtube.

If you are not comfortable with some electrical parts, call an electrician, because they can definitely kill you. Things like networking and connecting the raspberry to the relay shouldn't be that hard.

## Additional Downloads
- Fronius official API documentation: [Documentation - Fronius Solar API V1](https://www.fronius.com/~/downloads/Solar%20Energy/Operating%20Instructions/42%2C0410%2C2012.pdf)
- Postman request collection: [Postman Collection - Fronius Solar API V1](https://www.getpostman.com/collections/27c663306206d7fbf502)

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
python3 -m boilr [-h] [-v] {start,stop,status,restart,debug,manual {0,1}}
```

Complete guide (boilr -h):

```bash
usage: boilr [-h] [-v] {start,stop,status,restart,debug,manual} ...

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
    debug               Starts boilr daemon in debug mode
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
- Python 3 (tested with 3.7)
- some python packages

### Hardware

Here is a list of all parts I used:

- contactor to switch the three phases AC (~20€)
- 5x2.5mm2 copper stranded cable
  - ferrules (only if you have stranded wires)
- circuit breaker (had one laying around, but around 20€)
- distribution box (~20€)
- Raspberry Pi 1B (used for about 5€) + an sd card for the os (laying around)
- relay for the pi (5pcs for 8€, but we need only one)
- ethernet cable (had an old one at home (Cat5 - not even Cat5e))
- network switch (used, gigabit (overkill) around 5-10€, or an old router with a builtin switch for free)

I could have used an wifi dongle instead of an ethernet cable, but the signal strengh in my cellar (where the water boiler is) is somewhat inexistent. Plus, the pv inverter (already connected via lan) is also there.

## Cost analysis

Well, let's just asume there is a working product for this scenario out there that costs about 200-400€ without installation (I actually don't know if there is one).

For me it took three days to each six hours, to get the software up and running (3days x 6h = 18h). PayScale rates the average salary for an software engineer at 15.50€ per hour in Austria. Let me just do the math real quick (24hours * 15.50€/hour = 279€). Just shy of 300€ for a simple program. BTW, i am just a beginner in python.

Now for the installation part. An electrician gets 22.30€ per hour (rate also from Payscale for Austria). I am not that routined like a real electrician, but I managed to get it done in two hours. Quic mafs: (2hours * 22.30€/hour = 44.60€). With a little bit of rounding, we settle at 50€. My calculation is without all the extra stuff we would have to pay for the electrician, because that is the salary he would get for this job from his boss, and not what we would pay for it. From experience it would cost about 50-80€ per hour (without material)!

So, 300€ for the software and 50€ for the electical installation? Kind of, but without material costs and without actual costs we would have to pay. So my previous three paragraphs are pretty useless, because we can't compare salary of an average software engineer or electrician to the amount on the receipt we would have to pay. I plain words: I wasted your time (and my time by writing this).

At least I get to say: "Hey mum, look what I did"

### TL; DR

Heating water with not used power from the pv. That's it, cost analysis is just blabla.

## TODO

### Required

- installer
- tests (obvious)
- store response (file or list)
  - running median (prevents system nervousness - contactor toggles often)

### Optional

- daemon
  - working directory (auto install - elevated privileges)
  - run chrooted
  - reload config
- logrotate
