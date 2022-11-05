# Nutzung eines BME680 Sensors an einem Raspberry Pi als Luftqualitätssensor in HomeKit

## Inhaltsverzeichnis

- [[semesters/22-wise/iot/bme680-homekit-accessory/README#Projektidee und Kontext|Projektidee und Kontext]]
- [[semesters/22-wise/iot/bme680-homekit-accessory/README#Recherche|Recherche]]
- [[semesters/22-wise/iot/bme680-homekit-accessory/README#Einrichtung der Hardware|Einrichtung der Hardware]]
- [[semesters/22-wise/iot/bme680-homekit-accessory/README#Einrichtung der Entwicklungsumgebung|Einrichtung der Entwicklungsumgebung]]

Name: Henrik Panhans
Matrikel-Nummer: 573550

- Projektidee (Motivation)
- Formulierung der konkreten Aufgabenstellung
- Systematik der Problemlösung, Dokumentation von (Zwischen-) Ergebnissen
- Tiefe der Ausarbeitung und Recherche
- empfohlene weiterführende Schritte
- Form (bspw. referenzierte Bildbeschriftungen, Quellen, Inhaltsverzeichnis, Rechtschreibung)
- Grad der Herausforderung

## Projektidee und Kontext

Ich habe seit circa zwei Jahren einen Raspberry Pi zuhause rumliegen, der nichts tut, außer einen [HomeBridge](http://homebridge.io)-Server zu hosten, sodass ich meine [Heizkörper-Thermostate von AVM](https://avm.de/produkte/fritzdect/fritzdect-301/) in die Home App auf meinen Apple Geräten einbinden kann. Das funktioniert über [ein Plugin](https://github.com/SeydX/homebridge-fritz-platform), welches mit meiner Fritz!Box kommuniziert, welche wiederum die Thermostate anfunkt.
Die Thermostate haben jeweils einen eingebauten Temperatur-Sensor, da ich mir aber nie sicher war wie präzise diese sind, wollte ich schon seit Längerem eine Eigenlösung basteln. Außerdem wollte ich zusätzliche Daten, so wie Luftqualität und Luftfeuchtigkeit messen können.
Die Aufgabenstellung an mich selbst war also:

> Lies die Daten von einem Luftqualitätssensor aus, der am Raspberry Pi angeschlossen ist, verwerte diese potentiell und stelle diese so bereit, dass die Home-App sie als Sensor-Quelle anzeigen kann.

---

## Recherche

Ich hatte nun also eine Idee und ein Ziel, aber absolut keine Ahnung wie ich dieses verwirklichen wollte, bzw. konnte. Fest stand im Prinzip nur, dass mein Raspberry Pi zum Einsatz kommen sollte. Als allererstes brauchte ich einen Sensor, wobei ich mich für den [BME680 von Bosch](https://www.berrybase.de/bme680-breakout-board-4in1-sensor-fuer-temperatur-luftfeuchtigkeit-luftdruck-und-luftguete) entschied. Zu diesem schien Einiges an Dokumentation zu existieren, und - für mich noch wichtiger - Code-Beispiele und Libraries in Python anstatt nur in C.
Ich fand zwei Libraries die speziell für den BME680 geschrieben waren, einmal eine von [pimoroni](https://github.com/pimoroni/bme680-python) und einmal von [adafruit](https://github.com/adafruit/Adafruit_CircuitPython_BME680). Ausprobiert habe ich beide, entschied mich aber schlussendlich für die von pimoroni, da diese bessere Code-Beispiele beinhaltete, wie zum Beispiel einen Algorithmus zur Berechnung der Luftqualität auf den ich später noch eingehen werde.
Die Kommunikation mit dem Sensor an sich war also klar, und damit auch die Programmiersprache, nämlich Python (weshalb ich zugegebenermaßen sehr erleichtert war, denn ich hatte wenig Lust mich in C einarbeiten zu müssen). Benutzt habe ich Python 3.10.7, diese Version war zum Zeitpunkt des Projektstarts die aktuellste Version.
Bei der Installation von Python und den benötigten Libraries gab es einige Probleme, siehe [[semesters/22-wise/iot/bme680-homekit-accessory/README#Einrichtung des Raspberry Pi|Einrichtung des Raspberry Pi]].
Mir fehlte also nur noch eine Library um mit der Home-App zu kommunizieren. Auch hier ergab eine Google-Suche mehrere mögliche Kandidaten, in die engere Auswahl nahm ich aber nur [HAP-python](https://github.com/ikalchev/HAP-python) (hierbei steht HAP für [_HomeKit Accessory Protocol_](https://developer.apple.com/apple-home/)) und [homekit_python](https://github.com/jlusiardi/homekit_python). Nach ein bisschen durch die jeweiligen Dokumentationen graben, entschied ich mich für HAP-python, da es mir logischer strukturiert und "polierter" erschien. Außerdem wird homekit_python nicht aktiv weiterentwickelt und betreut:

> Due to lack of time I (@jlusiardi) will not put much time into this project in the foreseeable future.

\- Erste Zeile aus der README.md Datei der homekit_python Repository auf Github

**Anmerkung:** Ab iOS 16.2 (Stand 1. November 2022 noch in Beta) unterstützt die Home-App auch Geräte, die über das kürzlich Finalisierte [Matter-Protokoll](https://csa-iot.org/all-solutions/matter/) kommunizieren. Dieses soll Smart Home Geräte plattformunabhängig und sicher untereinander kommunizieren lassen können. Um aber die Komplexität meines Projekts nicht unnötig ins Unermessliche steigen zu lassen, indem ich den Standard selbst implementiere, entschied ich mich nur eine reine HAP Integration zu bauen.

Mein Techstack war also der Folgende:

- Python 3.10.7, installiert über `pyenv`
- HAP-python für die Einbindung in die Home-App
- Adafruit_CircuitPython_BME680 zum Auslesen der Sensordaten

---

## Einrichtung der Hardware

Als ersten Schritt der Durchführungsphase musste ich natürlich die Hardware einrichten und konfigurieren. Ich benötigte Folgendes:

- Bosch BME680 Sensor
- Raspberry Pi (Modell ist an sich egal, einer ist ein 4B mit 4GB RAM-Speicher)
- microSD-Karte zur Installation des Betriebsystems
- Lötkolben
- 4x Male-to-Female Jumper/Dupont Kabel (z.B. wie [hier auf BerryBase](https://www.berrybase.de/40pin-jumper/dupont-kabel-male-female-trennbar))
- USB-C Netzkabel

![[bme680_project_1.jpeg]]
\- Bosch BME680 Sensor als Breakout-Board von BerryBase

Zuerst ließ ich mir von meinen Mitbewohner erklären, wie ich die mitgelieferte Pin-Leiste an den Sensor löte. Da ich vorher noch nie selber gelötet hatte, stellte das meine Nerven ziemlich auf die Probe, es hat aber alles funktioniert.
Nach dem Löten und dem Anschließen der Jumper-Kabel sah das Ganze dann so aus:

![[bme680_project_3.jpeg]]
\- BME680 Sensor mit angelöteter Pin-Leiste und daran angeschlossenen Jumper-Kabeln.

{{TODO: Add comment about which Pins to use}}

Nun musste ich also theoretisch nur noch die Kabel an die richtigen GPIO-Pins (General Purpose In/Out) anschließen und das I2C-Interface des Raspberry Pi aktivieren und schon sollte der Sensor erkannt werden. Hierzu musste ich erst einmal Raspberry Pi OS installieren. Hierzu nutzte ich das Tool [Raspberry Pi Imager](https://www.raspberrypi.com/software/). Ich wählte Raspberry Pi OS Lite 64-Bit, hierbei bedeutet Lite, dass das Betriebsystem keine grafische Oberfläche wie man sie als normaler Endnutzer von macOS oder Windows kennt, sondern nur eine Kommando-Zeile. Da ich mit dem Pi aber sowieso eigentlich nur über SSH arbeite, ist das absolute ausreichend. Praktischerweise kann man dem Raspberry Pi Imager direkt auch WLAN, SSH und das Login des Pi konfigurieren, sodass beim ersten Bootvorgang direkt schon alles bereit ist. Nachdem das OS erfolgreich auf der angeschlossenen microSD-Karte installiert war, steckte ich diese in den Raspberry Pi und schaltete die Stromversorgung an. Kurzes Warten und ein Blick auf das Interface meiner FritzBox bestätigten, dass der Pi sich erfolgreich im Netzwerk eingewählt hatte. Also konnte ich mich nun mit SSH verbinden:

```bash
$ ssh pi@raspberry-henrik
Linux raspberry-henrik 5.15.61-v8+ #1579 SMP PREEMPT Fri Aug 26 11:16:44 BST 2022 aarch64

The programs included with the Debian GNU/Linux system are free software;
the exact distribution terms for each program are described in the
individual files in /usr/share/doc/*/copyright.

Debian GNU/Linux comes with ABSOLUTELY NO WARRANTY, to the extent
permitted by applicable law.
Last login: Mon Oct 31 23:39:07 2022 from 2a02:8109:a380:3748:cc44:6d6e:c58a:28d8
pi@raspberry-henrik:~ $
```

Mit dem `pinout`-Befehl ließ ich mir anzeigen, wie die genaue GPIO-Pin Belegung meines Raspberry Pi aussieht:

```
   3V3  (1) (2)  5V
 GPIO2  (3) (4)  5V
 GPIO3  (5) (6)  GND
 GPIO4  (7) (8)  GPIO14
   GND  (9) (10) GPIO15
GPIO17 (11) (12) GPIO18
GPIO27 (13) (14) GND
GPIO22 (15) (16) GPIO23
   3V3 (17) (18) GPIO24
GPIO10 (19) (20) GND
 GPIO9 (21) (22) GPIO25
GPIO11 (23) (24) GPIO8
   GND (25) (26) GPIO7
 GPIO0 (27) (28) GPIO1
 GPIO5 (29) (30) GND
 GPIO6 (31) (32) GPIO12
GPIO13 (33) (34) GND
GPIO19 (35) (36) GPIO16
GPIO26 (37) (38) GPIO20
   GND (39) (40) GPIO21
```

Eine bessere Visualisierung ist aber dieses Bild:

![GPIO-Pinout Diagram](https://www.laub-home.de/images/thumb/b/b2/GPIO-Pinout-Diagram-2.png/1200px-GPIO-Pinout-Diagram-2.png)

Laut den Anweisungen von [Laub-Home](https://www.laub-home.de/wiki/Raspberry_Pi_BME680_Gas_Sensor#Anschluss_des_Sensors_am_GPIO) sollte ich die Pins 1 (3v3 Strom), 3 (SDA), 5 (SCL) und 6 (Ground) benutzen. Dies stellte allerdings ein Problem dar, da ich an meinem Raspberry Pi einen kleinen Lüfter betreibe, der sich je nach Last zuschaltet um den Prozessor kühl zu halten. Dieser blockierte die vom Sensor benötigten Pins:

![[bme680_project_2.jpeg]]

---

## Einrichtung der Entwicklungsumgebung

## Installation

### Raspberry Pi OS

- flash with balena etcher
- Lite version is enough
- setup wifi and all

### Einrichtung des Raspberry Pi

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

## Quellen

Bilder die nicht explizit gekennzeichnet sind, wurden von mir selbst aufgenommen
https://www.robpeck.com/2017/11/using-pipenv-with-systemd/
https://github.com/dnutiu/bme680-homekit/blob/master/sensors/main.py
https://github.com/ikalchev/HAP-python
https://pipenv.pypa.io/en/latest/
https://github.com/pyenv/pyenv
https://www.balena.io/etcher/
https://www.raspberrypi.com/software/
https://www.laub-home.de/wiki/Raspberry_Pi_BME680_Gas_Sensor
https://github.com/pimoroni/bme680-python
