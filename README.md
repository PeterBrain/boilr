# Boilr

Water boiler automation with a Fronius pv inverter on a raspberry pi.

Goal: Use the overproduction of the PV system and increase the self consumption during daytime by heating water. By doing that, you decrease the amount of energy supplied to the grid, but also reduce consumption of pellets, oil or other fuel for heating.

## Hardware

- Raspberry Pi 1B
- relay for the pi
- contactor to switch the three phases AC
- circuit breaker
- distribution box
- ethernet cable
- network switch

## TODO

- date & time exception handling (wrong date or time format)
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
