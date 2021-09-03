[![CodeQL](https://github.com/Medve01/Lexie/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/Medve01/Lexie/actions/workflows/codeql-analysis.yml)   [![CI](https://github.com/Medve01/Lexie/actions/workflows/test_develop.yml/badge.svg)](https://github.com/Medve01/Lexie/actions/workflows/test_develop.yml)
# Lexie

Lexie is supposed to be a framework for controlling smart home devices. Main focus is on LAN-based management and supported devices will start with Shelly devices, namely:
- Shelly 1
- Shelly 1L (not much difference to a Shelly 1)
- Shelly bulbs (as soon as they get delivered)
- Shelly DW
- Shelly HT

Current state is extremely early, version number is closer to negative than to 0. This repo is focusing on the backend. Frontend will be a different project starting when I'm staisfied with the backend progress. Planned features are:
- A unified API for accessing basic controls of devices
- A scheduler for scenes/routines/automations, whatever I will call them
- Auto-configure Shelly devices with URLs towards Lexie, so they update their status without the need for polling

Thw whole idea came to me in a way that I'm currently using Node-RED for this purpose, but setting up a new device is a 10-30 min task in node-red including copy/pasting flows, etc. Also, my node-red config already stretches the capabilities of my dedicated Raspberry PI3 and I truly beleive that that kind of hardware should be enough for my purposes.
