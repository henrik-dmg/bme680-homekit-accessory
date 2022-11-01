# Nutzung eines BME680 Sensors an einem Raspberry Pi als Luftqualitätssensor in HomeKit

- Projektidee (Motivation)
- Formulierung der konkreten Aufgabenstellung
- Systematik der Problemlösung, Dokumentierung von (Zwischen-) Ergebnissen
- Tiefe der Ausarbeitung und Recherche
- empfohlene weiterführende Schritte
- Form (bspw. referenzierte Bildbeschriftungen, Quellen, Inhaltsverzeichnis, Rechtschreibung)
- Grad der Herausforderung

## Projektidee und Kontext

Ich habe seit circa zwei Jahren einen Raspberry Pi zuhause rumliegen, der nichts tut, außer einen [HomeBridge](http://homebridge.io)-Server zu hosten,
sodass ich meine Heizköper-Thermostate von Fritz! in die Home App auf meinem Handy einbinden kann. Das funktioniert über ein Plugin, welches mit meiner Fritz!Box kommuniziert, welche widerum die Thermostate anfunkt.
Die Thermostate haben jeweils einen eingebauten Temperatur-Sensor, da ich mir aber nie sicher war wie präzise diese sind, wollte ich schon seit Längerem

## Recherche

## Installation

### Raspberry Pi OS

- flash with balena etcher
- Lite version is enough
- setup wifi and all

### Setup Pi
- `sudo apt install git` if not already installed
- go to dir where repo should live
- `git clone https://github.com/henrik-dmg/bme680-homekit-accessory`
- `cd bme680-homekit-accessory`
- enable i2c Interace with `raspi-config nonint do_i2c 0`
- `sudo apt install -y python3-smbus i2c-tools`
- `lsmod | grep i2c_` sollte module ausgeben
- `i2cdetect -y 1` sollte Sensor matrix bei 77 anzeigen
- `sudo apt install python3-pip -y`
- `pip3 install adafruit-circuitpython-bme680`

## Aufgetretene Probleme

- pyenv und pipenv
- service creation mit pipenv
- vorzeitiges iOS-16 Matter Upgrade führte dazu, dass keine Paarung mehr persistiert werden kann, da UUIDs nun case-sensitive behandelt werden (https://github.com/ikalchev/HAP-python/pull/424). Lösung: Fork benutzen

## Test References
[@bdracoFixPairingIOS2022]

## Quellen
https://www.robpeck.com/2017/11/using-pipenv-with-systemd/
https://github.com/dnutiu/bme680-homekit/blob/master/sensors/main.py
https://github.com/ikalchev/HAP-python
https://pipenv.pypa.io/en/latest/
https://github.com/pyenv/pyenv
https://www.balena.io/etcher/
https://www.raspberrypi.com/software/
https://www.laub-home.de/wiki/Raspberry_Pi_BME680_Gas_Sensor
https://github.com/pimoroni/bme680-python