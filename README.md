# Boilr

## Preamble

Water boiler automation with a Fronius pv inverter on a Raspberry Pi.

Goal: Use the overproduction of the PV system and increase the self consumption during daytime by heating water. By doing that, you decrease the amount of energy supplied to the grid, but also reduce consumption of pellets, oil or other fuel for heating.

That's the theory. But what about special cases like an already running heater? Or taking away power generated from the pv and you have to use power from the grid to use the stove?
I don't know, I don't care. Just wanted to do this in my spare time. Otherwise I would have wasted the time invested in this project by watching Netflix or Youtube.

If you are not comfortable with some electrical parts, call an electrician, because they can definitely kill you. Things like networking and connecting the raspberry to the relay shouldn't be that hard.

## Hardware

Here is a list of all parts I used:

- contactor to switch the three phases AC (~30€)
- 5x2.5mm2 copper stranded cable
- ferrules for the copper wires
- circuit breaker (had one laying around, but around 30€)
- distribution box (~20-30€)
- Raspberry Pi 1B (used for about 5€) + an sd card for the os (laying around)
- relay for the pi (don't know yet)
- ethernet cable (had an old one at home (Cat5 - not even Cat5e))
- network switch (used, gigabit (overkill) around 5-10€)

I could have used an wifi dongle instead of an ethernet cable, but the signal strengh in my cellar (where the water boiler is) is somewhat inexistent. Plus, the pv inverter (already connected via lan) is also there.

## Cost analysis

Well, let's just asume there is a working product for this scenario out there that costs about 200-400€ without installation (I actually don't know if there is one).

For me it took three days to each six hours, to get the software up and running (3days x 6h = 18h). PayScale rates the average salary for an software engineer at 15.50€ per hour in Austria. Let me just do the math real quick (24hours * 15.50€/hour = 279€). Just shy of 300€ for a simple program. BTW, i am just a beginner in python.

Now for the installation part. An electrician gets 22.30€ per hour (rate also from Payscale for Austria). I am not that routined like a real electrician, but I managed to get it done in two hours. Quic mafs: (2hours * 22.30€/hour = 44.60€). With a little bit of rounding, we settle at 50€. My calculation is without all the extra stuff we would have to pay for the electrician, because that is the salary he would get for this job from his boss, and not what we would pay for it. From experience it would cost about 50-80€ per hour (without material)!

So, 300€ for the software and 50€ for the electical installation? Kind of, but without material costs and without actual costs we would have to pay. So my previous three paragraphs are pretty useless, because we can't compare salary of an average software engineer or electrician to the amount on the receipt we would have to pay. I plain words: I wasted your time (and my time by writing this).

At least I get to say: "Hey mum, look what I did"

## TL; DR

Heating water with not used power from the pv. That's it, everything else is just blabla.

## TODO

- http request exception handling (no network connection, no response)
- store response (file or list)
  - running median (prevents system nervousness - contactor toggles often)
- tests (obvious)
- daemon
  - working directory (auto install - elevated privileges)
  - run chrooted
  - add more signals
- logrotate
- watchdog (config reload)
- RPi.GPIO cleanup
