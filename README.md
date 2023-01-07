# Nutzung eines BME680 Sensors an einem Raspberry Pi als Luftqualitätssensor in HomeKit

Name: Henrik Panhans
Matrikel-Nummer: 573550

## Inhaltsverzeichnis

-   [[semesters/22-wise/iot/bme680-homekit-accessory/README#Projektidee und Kontext|Projektidee und Kontext]]
-   [[semesters/22-wise/iot/bme680-homekit-accessory/README#Recherche|Recherche]]
-   [[semesters/22-wise/iot/bme680-homekit-accessory/README#Einrichtung der Hardware|Einrichtung der Hardware]]
-   [[semesters/22-wise/iot/bme680-homekit-accessory/README#Einrichtung der Entwicklungsumgebung|Einrichtung der Entwicklungsumgebung]]
-   [[semesters/22-wise/iot/bme680-homekit-accessory/README#Implementation|Implementation]]
    -   [[semesters/22-wise/iot/bme680-homekit-accessory/README#HomeKit Bridge Server|HomeKit Bridge Server]]
    -   [[semesters/22-wise/iot/bme680-homekit-accessory/README#WrappedAccessory|WrappedAccessory]]
    -   [[semesters/22-wise/iot/bme680-homekit-accessory/README#WrappedSensor|WrappedSensor]]
    -   [[semesters/22-wise/iot/bme680-homekit-accessory/README#AQI-Algorithmus|AQI-Algorithmus]]
    -   [[semesters/22-wise/iot/bme680-homekit-accessory/README#Service Erstellung|Service Erstellung]]
-   [[semesters/22-wise/iot/bme680-homekit-accessory/README#Fazit|Fazit]]
-   [[semesters/22-wise/iot/bme680-homekit-accessory/README#Ausblick|Ausblick]]
-   [[semesters/22-wise/iot/bme680-homekit-accessory/README#Quellen|Quellen]]

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

-   Python 3.10.7, installiert über `pyenv`
-   HAP-python für die Einbindung in die Home-App
-   bme680-python zum Auslesen der Sensordaten

---

## Einrichtung der Hardware

Als ersten Schritt der Durchführungsphase musste ich natürlich die Hardware einrichten und konfigurieren. Ich benötigte Folgendes:

-   Bosch BME680 Sensor
-   Raspberry Pi (Modell ist an sich egal, einer ist ein 4B mit 4GB RAM-Speicher)
-   microSD-Karte zur Installation des Betriebsystems
-   Lötkolben
-   4x Male-to-Female Jumper/Dupont Kabel (z.B. wie [hier auf BerryBase](https://www.berrybase.de/40pin-jumper/dupont-kabel-male-female-trennbar))
-   USB-C Netzkabel

![[bme680_project_1.jpeg]]
\- Bild #1, Bosch BME680 Sensor als Breakout-Board von BerryBase

Zuerst ließ ich mir von meinen Mitbewohner erklären, wie ich die mitgelieferte Pin-Leiste (sichtbar rechts in Bild #1) an den Sensor löte. Da ich vorher noch nie selber gelötet hatte, stellte das meine Nerven ziemlich auf die Probe, es hat aber alles funktioniert.
Nach dem Löten und dem Anschließen der Jumper-Kabel sah das Ganze dann so aus:

![[bme680_project_3.jpeg]]
\- Bild #2, BME680 Sensor mit angelöteter Pin-Leiste und daran angeschlossenen Jumper-Kabeln.

Da ich das I2C-Interface benutzen wollte, musste ich nur vier der sechs Pins an den Sensor anschließen. Wie in Bild #2 zu sehen, die beiden oberen Pins sind unbenutzt. Das sind die Pins `SC0` und `CS` (Bild #1).

Nun musste ich also theoretisch nur noch die Kabel an die richtigen GPIO-Pins (General Purpose In/Out) des Raspberry Pi anschließen und das I2C-Interface des Pi aktivieren und schon sollte der Sensor erkannt werden. Hierzu musste ich erst einmal Raspberry Pi OS installieren. Hierzu nutzte ich das Tool [Raspberry Pi Imager](https://www.raspberrypi.com/software/). Ich wählte Raspberry Pi OS Lite 64-Bit, hierbei bedeutet Lite, dass das Betriebsystem keine grafische Oberfläche wie man sie als normaler Endnutzer von macOS oder Windows kennt, sondern nur eine Kommando-Zeile. Da ich mit dem Pi aber sowieso eigentlich nur über SSH arbeite, ist das absolute ausreichend. Praktischerweise kann man dem Raspberry Pi Imager direkt auch WLAN, SSH und das Login des Pi konfigurieren, sodass beim ersten Bootvorgang direkt schon alles bereit ist. Nachdem das OS erfolgreich auf der angeschlossenen microSD-Karte installiert war, steckte ich diese in den Raspberry Pi und schaltete die Stromversorgung an. Kurzes Warten und ein Blick auf das Interface meiner FritzBox bestätigten, dass der Pi sich erfolgreich im Netzwerk eingewählt hatte. Also konnte ich mich nun mit SSH verbinden:

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
\- Bild #3, von [Laub-Home](https://www.laub-home.de/images/thumb/b/b2/GPIO-Pinout-Diagram-2.png/1200px-GPIO-Pinout-Diagram-2.png), Visualisierung der GPIO-Pin Belegung eines Raspberry Pi 4

Laut den Anweisungen von [Laub-Home](https://www.laub-home.de/wiki/Raspberry_Pi_BME680_Gas_Sensor#Anschluss_des_Sensors_am_GPIO) sollte ich die Pins 1 (3v3 Strom), 3 (SDA), 5 (SCL) und 6 (Ground) benutzen. Dies stellte allerdings ein Problem dar, da ich an meinem Raspberry Pi einen kleinen Lüfter betreibe, der sich je nach Last zuschaltet um den Prozessor kühl zu halten. Dieser blockierte die vom Sensor benötigten Pins:

![[bme680_project_2.jpeg]]
\- Bild #4, Raspberry Pi GPIO-Pinleiste, wobei Pin 1, 3, 5 und 6 markiert sind

Es stellte sich heraus, dass der Raspberry Pi zwei verschiedene I2C-Interfaces hat, das Primäre wie erwähnt an Pin 3 und 5 und das Zweite an Pin 27 und 28. Also schloss ich den Sensor zunächst einmal an Pin 27 und 28 an, da diese Pins nicht vom Lüfter blockiert wurden.
Außerdem musste ich erst noch das I2C-Interface softwareseitig aktivieren. Das geht mit dem Befehl:

```bash
$ raspi-config nonint do_i2c 0
```

Außerdem braucht es noch einige Packages:

```bash
$ apt install -y python3-smbus i2c-tools
```

Testen, dass alle Module korrekt geladen wurden:

```bash
$ lsmod | grep i2c_
i2c_brcmstb            16384  0
i2c_bcm2835            16384  2
i2c_dev                20480  4
```

Nachdem nun softwareseitig alles bereit war, konnte ich den Sensor endlich anschließen. Dazu schaltete ich den Pi zuerst natürlich aus, und verband dann die Kabel mit den Pins 27, 28, 25 (Ground) und 17 (3v3 Strom). Nach dem Reboot, wollte ich verifizieren, dass der Sensor erkannt wird:

```bash
$ i2cdetect -y 1
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:                         -- -- -- -- -- -- -- --
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
70: -- -- -- -- -- -- -- --
```

Das war der erste große Rückschlag. Der Sensor wurde nicht erkannt, und ich wusste nicht wieso. Nach einigem Durchforsten des Webs, stoß ich auf [einen Foreneintrag](https://forum-raspberrypi.de/forum/thread/31667-i2c-an-pin27-pin28-des-gpio-steckers/?postID=259968#post259968), der genau mein Problem beschrieb. Anscheinend sind Pin 27 und 28 reserviert für EEPROMs (electrically erasable programmable read-only memory) und daher nicht wirklich für den _normalen_ I2C Betrieb gedacht.
Also probierte ich den Sensor, wie gefordert, an Pin 1, 3, 5 und 7 anzuschließen, um zu testen, dass der Sensor an sich funktioniert und korrekt gelötet ist. Das bedeutete zwar, dass ich meine Lüfter nicht gleichzeitig betreiben konnte, das war allerdings verkraftbar, da ich bei BerryBase dann [einen anderen Lüfter](https://www.berrybase.de/argon-fan-hat-fuer-raspberry-pi) fand, der keine GPIO Pins blockiert.
Nach dem Umstecken des Sensors, funktionierte dann alles wie gewollt:

```bash
$ i2cdetect -y 1
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:                         -- -- -- -- -- -- -- --
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
70: -- -- -- -- -- -- -- 77
```

Hardwareseitig war nun alles bereit, um mit der Implementation zu beginnen.

---

## Einrichtung der Entwicklungsumgebung

Zunächst wollte ich Python und `pip` zur Installation von Python-Packages installieren. Wenn ich dem Guide von Laub-Home gefolgt wäre, hätte ich dies einfach durch `apt install python3-pip -y` tun können. Ich wollte aber gerne [pyenv](https://github.com/pyenv/pyenv) verwenden, da dies die Installation und Nutzung mehrerer Python-Version ermöglicht. Zur Installation unter Raspberry Pi OS, nutze ich den bereitgestellten Installer:

```bash
$ curl -L https://github.com/pyenv/pyenv-installer/raw/master/bin/pyenv-installer | bash
```

Nachdem ich die Anweisung zum Einrichten der benötigten Environment-Variablen befolgt hatte, musste ich noch ein paar Dependencies installieren:

```bash
$ sudo apt update
$ sudo apt install make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev
```

Nachdem ich rebootet habe, wollte ich Python 3.10.7 installieren:

```bash
$ pyenv install 3.10.7
# ...
ERROR: The Python ssl extension was not compiled. Missing the OpenSSL lib?
# ...
```

Na toll. Die Python-Installation war im Nachhinein gesehen tatsächlich der Part, mit dem ich mich mit am Meisten rumgeärgert habe und am Meisten Zeit verschwendet habe. Zum Glück schien dieser Fehler häufig aufzutreten, weshalb es sogar [eine extra Sektion im pyenv Wiki](https://github.com/pyenv/pyenv/wiki/Common-build-problems#error-the-python-ssl-extension-was-not-compiled-missing-the-openssl-lib) gibt. Nach einigem rumprobieren, folgte ich dann [diesem Guide](https://help.dreamhost.com/hc/en-us/articles/360001435926-Installing-OpenSSL-locally-under-your-username) um OpenSSL unter meinem Benutzer zu selbst zu compilen und installeren und dann pyenv manuell davon wissen zu lassen. Schlussendlich konnte ich Python mit dem folgenden Befehl installieren:

```bash
$ CPPFLAGS=-I$HOME/openssl/include LDFLAGS=-L$HOME/openssl/lib SSH=$HOME/openssl pyenv install -v 3.10.7
```

Dann konnte ich die globale Python-Version setzen und `pip` installieren:

```bash
$ pyenv global 3.10.7
$ python --version
Python 3.10.7
$ python -m ensurepip --upgrade
```

Zum Verwalten von Dependencies wollte ich [pipenv](https://pipenv.pypa.io/en/latest/) verwenden, da dieses `Pipfile` und `Pipfile.lock` benutzt. Das erschien mir moderner und besser, [als Dependencies aus einer simplen .txt Datei auszulesen und zu installieren](https://stackoverflow.com/a/15593865/4553482). Außerdem kann ich mit `Pipfile` sicher sein, welche Versionen verwendet werden, was mir tatsächlich im Nachhinein zugute kam (dazu später mehr).

```bash
$ pip install pipenv
```

Dann konnte das tatsächliche Setup der Repository erfolgen:

```bash
$ mkdir ~/bme680-homekit-accessory
$ cd ~/bme680-homekit-accessory
```

HAP-python erfordert noch ein paar extra Dependencies:

```bash
$ sudo apt-get install libavahi-compat-libdnssd-dev
```

Schlussendlich konnte ich die beiden benötigten Python-Libraries wie folgt installieren:

```
$ pipenv install bme680 HAP-python[QRCode]
Creating a virtualenv for this project...
Pipfile: /home/pi/bme680-homekit-accessory/Pipfile
Using /home/pi/.pyenv/versions/3.10.7/bin/python3 (3.10.7) to create virtualenv...
⠧ Creating virtual environment...created virtual environment CPython3.10.7.final.0-64 in 992ms
  creator Venv(dest=/home/pi/.local/share/virtualenvs/bme680-homekit-accessory-4T_QXEXt, clear=False, no_vcs_ignore=False, global=False, describe=CPython3Posix)
  seeder FromAppData(download=False, pip=bundle, setuptools=bundle, wheel=bundle, via=copy, app_data_dir=/home/pi/.local/share/virtualenv)
    added seed packages: pip==22.2.2, setuptools==65.4.1, wheel==0.37.1
  activators BashActivator,CShellActivator,FishActivator,NushellActivator,PowerShellActivator,PythonActivator

✔ Successfully created virtual environment!
Virtualenv location: /home/pi/.local/share/virtualenvs/bme680-homekit-accessory-4T_QXEXt
Installing dependencies from Pipfile.lock (b45f9f)...
To activate this project's virtualenv, run pipenv shell.
Alternatively, run a command inside the virtualenv with pipenv run.
```

Damit war das Setup beinahe abgeschlossen, ich musste nämlich noch einen Weg finden mit funktionierendem Auto-Complete programmieren zu können, denn die bme680 Library ist nicht macOS kompatibel, wodurch ich sie nicht lokal installieren konnte. Hierfür benutzte ich Visual Studio Code in Verbindung mit der [Remote - SSH](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-ssh) Extension, welche es mir ermöglicht, mich direkt in VS Code mit meinem Pi zu verbinden, und dessen Virtual Environments und dergleichen zu benutzen. Das bedeutet zwar auch, dass das Syntax Highlighting und Auto-Complete etwas verzögert ist (da die Infos immer erst zwischen meinem Mac und dem Pi hin- und hergeschickt werden müssen), aber das war die für mich beste Lösung. Zwischenzeitlich dachte ich, es macht Sinn Ubuntu auf meinem Mac als Dual-Boot zu installieren, da ich dann die bme680 Library lokal hätte installieren können, aber dann hätte ich nicht gleichzeitig testen können.

---

## Implementation

### HomeKit Bridge Server

Nun war endlich alles bereit um tatsächlich zu programmieren. Als Erstes brauchte ich ein Skript, was als Eingangspunk für die Ausführung dienen sollte:

```bash
$ touch main.py
```

Hier fügte ich die folgenden Zeilen ein:

```python
#!/usr/bin/env python3

import logging
import signal

from pyhap.accessory import Bridge
from pyhap.accessory_driver import AccessoryDriver


def make_bridge(accessory_driver):
  bridge = Bridge(accessory_driver, "RaspiBridge")
  return bridge


# Start the accessory on port 51826
driver = AccessoryDriver(
  port=51826, persist_file="~/bme680-homekit-accessory/accessory.state"
)
# Hide sensor behind a bridge. This makes it easier to add more accessories later
driver.add_accessory(accessory=make_bridge(driver))

# We want SIGTERM (terminate) to be handled by the driver itself,
# so that it can gracefully stop the accessory, server and advertising.
signal.signal(signal.SIGTERM, driver.signal_handler)

# Start it!
driver.start()
```

Dieser Starter-Code ist größtenteils der [Beispiel-Code von HAP-python](https://github.com/ikalchev/HAP-python/blob/dev/main.py). Beim Überlegen, wie ich meinen Code strukturieren wollte, entschied ich mich dafür zwei Klassen zu erstellen:

1. Eine Wrapper-Klasse für den Sensor, die dessen Daten ausliest und aufbereiten kann. Dies war außerdem sinnvoll, da ich mir noch einen Algorithmus zur Berechnung eines _Luftqualitätsscores_ ausdenken musste, da der BME680 einem nur die rohen Daten liefert (zumindest in Verbindung mit der von mir benutzen Library) und ich diesen nicht einfach irgendwo in die `main.py` Datei schmeißen wollte
2. Eine Unterklasse von `Accessory` aus der `HAP-python` Library, die die drei erwünschten Metriken (Temperatur, Luftfeuchtigkeit, Luftqualität) in einem Sensor zusammenfasst.

Anfangs war ich der Auffassung, dass ich pro Metrik eine einzelne Unterklasse von `Accessory` brauche, die sich dann jeweils nur um die für sie relevanten Daten kümmert. Das Problem hiermit war Zeitsynchronisation - ein Klassiker. Da alle Unterklassen/Accessories fast gleichzeitig jeweils Daten vom Sensor angefordert haben, hat dieser mehrere Male hintereinander gemessen, was nicht nur die Ergebnisse verfälscht hat, da sich der Sensor aufheizt, sondern dies auch einfach unnötige Arbeit ist. Außerdem hätte das dazu geführt, dass drei separate Sensoren in der Home-App angezeigt werden, was natürlich auch semantisch Quatsch ist, da ja alle Daten nur von einem einzigen Sensor kommen.

### WrappedAccessory

Ein Sensor-Accessory hat die folgenden Grundstruktur:

```python
from pyhap.accessory import Accessory
from pyhap.const import CATEGORY_SENSOR

class WrappedAccessory(Accessory):

  category = CATEGORY_SENSOR # This is for the icon in the iOS Home app.

  def __init__(self, driver, display_name):
    super().__init__(driver, display_name)
    # TODO: Add the services that this Accessory will support here

  @Accessory.run_at_interval(15)
  def run(self):
    # TODO: Update data here
```

Zur Erläuterung:

-   `category = CATEGORY_SENSOR` signalisiert der Home-App, dass es sich bei dem Accessory um einen Sensor handelt
-   mit `@Accessory.run_at_interval(15)` bestimmen wir, dass alle 15 Sekunden der Wert, der in der Home-App angezeigt wird aktualisiert werden soll. In meinem Fall bedeutete das, dass ich alle 15 Sekunden die Daten des Sensors auslese.

Der nächste Schritt war die gewünschten _Services_ zu registrieren. Ein Service im Kontext eines Accessories ist eine Fähigkeit, die das Gerät bietet und diese der Home-App zur Anzeige anzubieten. Also habe ich den `def __init__` meines `WrappedAccessory` um folgende Zeilen erweitert:

```python
# ...
humidity_service = self.add_preload_service("HumiditySensor")
self.humidity_char = humidity_service.get_characteristic("CurrentRelativeHumidity")

temp_service = self.add_preload_service("TemperatureSensor")
self.temp_char = temp_service.get_characteristic("CurrentTemperature")

aqi_service = self.add_preload_service("AirQualitySensor")
self.aqi_char = aqi_service.get_characteristic("AirQuality")
```

Die Zeilen, in denen ein `xxx_service` erstellt werden, definieren jeweils die **Art des Sensors**, z.B. `HumiditySensor` teilt HomeKit mit, dass es sich um einen Feuchtigkeitssensor handelt.
Die Zeilen, in denen `xxx_service.get_characteristic("someCharacteristic")` steht, sagen HomeKit, welche **Art von Daten** in zum Beispiel `self.humidity_char` gespeichert werden.
Die Liste an möglichen Kombinationen von Sensor-Art und Daten-Art, konnte ich der [`services.json`](https://github.com/ikalchev/HAP-python/blob/dae7650f9f95a141b4d827e057cd2cfe6127c692/pyhap/resources/services.json) Datei aus der HAP-python Repository entnehmen.

Danach habe ich erstmal fake Daten verwendet, um zu testen ob alles funktioniert. Die Daten werden in der `def run(self)` Methode aktualisiert.

```python
@Accessory.run_at_interval(15)
def run(self):
	self.humidity_char.set_value(random.randint(0, 100))
	self.temp_char.set_value(random.randint(-10, 50))
	self.aqi_char.set_value(random.randint(1, 5)) # 0 is for unknown quality
```

Anfangs war ich der Auffassung, dass Luftqualität ebenfalls in Prozent angegeben, so wie Luftfeuchtigkeit. Hier bekam ich aber eine Exception ausgespuckt, dass der Wert ungültig sei. Auch hier stieß ich schließlich auf eine [`characteristics.json`](https://github.com/ikalchev/HAP-python/blob/dae7650f9f95a141b4d827e057cd2cfe6127c692/pyhap/resources/characteristics.json) Datei, welche die gültigen Werte für die jeweiligen Charakteristiken definiert.

Dann habe ich noch die `def make_bride(accessory_driver)` Methode in `main.py` angepasst um den Sensor als Accessory zu verwenden:

```python
from wrapper.wrapped_accessory import WrappedAccessory

def make_bridge(accessory_driver):
  bridge = Bridge(accessory_driver, "RaspiBridge")
  bridge.add_accessory(WrappedAccessory(accessory_driver, "BME680Sensor"))
  return bridge
```

Wenn wir nun das Skript mit `pipenv run python main.py` (wir müssen `pipenv run` als Präfix vor den eigentlichen Befehl setzen, um sicher zu gehen, dass wir das virtuelle Environment verwenden und damit alle Dependencies zur Verfügung haben) sehen wir Folgendes:

```bash
$ pipenv run python main.py
[accessory_driver] Storing Accessory state in `/home/pi/bme680-homekit-accessory/accessory.state`
[accessory_driver] Starting the event loop
[accessory_driver] Starting accessory RaspiBridge on address 192.168.178.33, port 51826.
Setup payload: X-HM://0024E886ZTU18
Scan this code with your HomeKit app on your iOS device:

# Eigentlich wird an dieser Stelle ein QR-Code angezeigt, da dieser aber nur eingefärbte Leerzeichen sind,
# konnte ich diesen nicht im Codeblock beinhalten

Or enter this code in your HomeKit app on your iOS device: 559-25-115
```

Wenn man den erwähnten QR-Code scannt, öffnet sich die Home-App und fragt einen, ob man die "RaspiBridge" hinzufügen möchte. Dann muss man sich durch ein kurzes Setup klicken und den Sensor einem Raum zuweisen. Nach dem Setup sieht das Ganze dann so aus:

![[bem680_project_home_app_screenshot.png]]
\- Bild #5, Screenshot aus der Home-App nachdem der Sensor eingerichtet wurde

An dieser Stelle möchte ich auf die `accessory.state` Datei eingehen, die HAP-python für Persistenz verwendet. Sobald `start()` auf einem `AccessoryDriver` aufgerufen wird, liest dieser (falls vorhanden) die `accessory.state` Datei aus oder erstellt diese, falls sie nicht existiert. Diese Datei ist eine relativ simple JSON-Datei, in der einige Metadaten gespeichert werden, damit man nicht bei jedem Start des `AccessoryDriver` den Pairing-Prozess neu durchführen muss. Die von meinem Pi gespeicherte Datei sieht zum Beispiel so aus:

```json
{
    "mac": "F7:6A:13:B6:F2:80",
    "config_version": 2,
    "paired_clients": {
        "ba77b6d0-ebb7-4721-84ba-37ffd59eaedb": "e4ae920fbdb29002e10761cdeb7275e1a7d1463da78c6b02559d6eeea2543567"
    },
    "client_properties": {
        "ba77b6d0-ebb7-4721-84ba-37ffd59eaedb": {
            "permissions": 1
        }
    },
    "accessories_hash": "e67c6828ffd3aa8254fa4ad932a6872514b20d62977b332dc5761d111ed123b3e7250ed32161fc5ef5bec192d7dc44cbe725b6806ac9eddee86df246f2589644",
    "private_key": "you_wish_you_knew_my_private_key",
    "public_key": "aa2659047b9df62e32f95210ae5d2f3ad4246a5c3bd4b57d9178e7c4da1f1f79"
}
```

Zu Beginn des Projekts funktionierte alles ganz ohne Probleme (zugegebenermaßen etwas zu meiner Überraschung). Dann kam allerdings die iOS 16.2 Beta heraus, und ich las in einem Artikel, dass dieses Update die Home-App Architektur so überarbeitet, dass Geräte mit Matter-Unterstützung hinzugefügt werden können. Das fand ich natürlich spannend und installierte dieses Update auf meinem iPhone. Ich musste außerdem meinen Apple TV updaten, der im lokalen Netzwerk als Hub funktioniert, sodass ich meine Geräte auch von unterwegs steuern kann. Nach dem Update ging plötzlich nichts mehr. Egal was ich versuchte (sprich egal welchen Pfad ich für die `accessory.state` Datei manuell angab), nach jedem Neustart des `AccessoryDriver` musste ich die Bridge neu hinzufügen. Das ist natürlich nicht wünschenswert, da man sonst nach jedem Neustart des Pi den gesamten Pairing-Prozess wiederholen muss.
Ich war der Verzweiflung sehr nahe. Ich kam auch nicht auf die Idee, dass es vielleicht am Client (also an meinem iPhone) liegen könnte und nicht am Server (Pi). Nach Durchforsten der HAP-python Library nach offenen Issues oder Pull Requests (nachfolgend PR), fand ich eine PR mit folgendem Titel:

> Fix pairing with iOS 16 #424
> https://github.com/ikalchev/HAP-python/pull/424

Das klang viel versprechend. Nach Lesen des ersten Satz war mir bewusst, wo mein Fehler lag:

> UUIDs must be upper case with iOS 16 or they will get unpaired by the iOS device because it no longer compares them case insensitive.

\- PR Beschreibung von @bdraco

Die PR wurde mittlerweile [gemerged](https://github.com/ikalchev/HAP-python/commit/9a54ecf84faca675364d374eb1cf2dc7ab008ce5), aber es wurde noch kein neuer offizieller Release veröffentlicht (Stand 29.11.). Deshalb habe ich entschlossen, HAP-python einfach direkt vom `dev` Branch zu verwenden. Also musste ich auch die `Pipfile` entsprechend anpassen:

```
# Old
hap-python = {extras = ["qrcode"], version = "*"}

# New
ha-hap-python = {extras = ["qrcode"], editable = true, ref = "dev", git = "https://github.com/ikalchev/HAP-python"}
```

Nun einmal `pipenv install` ausgeführt und schon funktionierte wieder alles wie gewollt. Die eine Hälfte der Implementation war damit so gut wie erledigt. Jetzt brauchte ich nur noch echte Daten vom Sensor.

### WrappedSensor

Beim Auslesen der Daten orientierte ich mich stark an den [Beispielen aus der pimoroni-Repository](https://github.com/pimoroni/bme680-python/tree/master/examples). Als Erstes wollte ich den Sensor in einer Wrapper-Klasse unterbringen:

```python
class WrappedSensor:
    def __init__(self):
        # 1:
        try:
            sensor = bme680.BME680(bme680.I2C_ADDR_PRIMARY)
        except (RuntimeError, IOError):
            sensor = bme680.BME680(bme680.I2C_ADDR_SECONDARY)

        # 2:
        # These oversampling settings can be tweaked to
        # change the balance between accuracy and noise in
        # the data.
        sensor.set_humidity_oversample(bme680.OS_2X)
        sensor.set_pressure_oversample(bme680.OS_4X)
        sensor.set_temperature_oversample(bme680.OS_8X)
        sensor.set_filter(bme680.FILTER_SIZE_3)
        sensor.set_gas_status(bme680.ENABLE_GAS_MEAS)

        sensor.set_gas_heater_temperature(320)
        sensor.set_gas_heater_duration(600)
        sensor.select_gas_heater_profile(0)

    def get_data(self) -> SensorData:
        # Read data from sensor, process and put into `SensorData` wrapper class
        self.sensor.get_sensor_data()
        aqi_score = self.get_air_quality(self.sensor.data)
        return SensorData(
            temperature=self.sensor.data.temperature,
            humidity=self.sensor.data.humidity,
            pressure=self.sensor.data.pressure,
            aqi_score=aqi_score
        )


class SensorData:
    """Structure for storing BME680 sensor data."""

    def __init__(self, temperature, pressure, humidity, aqi_score):
        self.temperature = temperature
        self.pressure = pressure
        self.humidity = humidity
        self.aqi_score = aqi_score
```

Zur Erläuterung:

1. Hier erstellen wir den Sensor im Code und geben ihm als Parameter den Wert `I2C_ADDR_PRIMARY` welcher die Adresse des Sensors darstellt. Kann der Sensor an dieser Adresse nicht gefunden werden, versuchen wir ihn noch einmal an der sekundären Adresse zu finden. Die beiden möglichen Adressen sind `76` und `77` (Hexadezimal), unter welcher der Sensor zu finden ist, kann wie oben beschrieben mit `i2cdetect -y 1` herausgefunden werden.
2. Diese Einstellungen konfigurieren den Sensor etwas, in dem sie zum Beispiel die Dauer einstellen, die der Gas-Sensor benutzt um sich aufzuheizen wenn Daten angefragt werden. Je länger diese Dauer ist, desto präziser ist der ausgelesene Wert, aber er erhöht natürlich auch die Antwortzeit des Sensors.

Als Nächstes habe ich den Sensor dem Accessory über dessen `__init__` übergeben:

```python
def __init__(self, driver, display_name, sensor: WrappedSensor):
    super().__init__(driver, display_name)
    self.sensor = sensor

    # Erstellen der gewünschten Services, siehe oben bei WrappedAccessory
```

Dann musste ich noch eine kleine Änderung in `main.py` vornehmen:

```python
# ...
from wrapper.wrapped_sensor import WrappedSensor

sensor = WrappedSensor()
sensor.burn_in_sensor() # Erläuterung zu dieser Zeile folgt im Abschnitt AQI-Algorithmus

# ...
accessory = WrappedAccessory(accessory_driver, "BME680Sensor", sensor=sensor)
```

Jetzt kann `WrappedAccessory` in der Methode `run(self)` die Methode `get_data(self) -> SensorData` des `WrappedSensor` aufrufen und die echten Daten verwenden:

```python
class WrappedAccessory(Accessory):

    # ...

    @Accessory.run_at_interval(15)
    def run(self):
        data = self.sensor.get_data()
        self.humidity_char.set_value(data.humidity)
        self.temp_char.set_value(data.temperature)
        self.aqi_char.set_value(data.aqi_score)
```

Alle weiteren Änderungen können intern in der Klasse `WrappedSensor` vorgenommen werden.

### AQI-Algorithmus

Bevor ich wirklich anfing überhaupt selber Code zu schreiben, probierte ich Einige der [Beispiel-Skripte in der pimoroni-Repository](https://github.com/pimoroni/bme680-python/tree/master/examples) aus, um zu testen, ob der Sensor überhaupt richtig funktioniert und korrekt verlötet ist. Dabei stieß ich auf das Skript aqi*sample.py. In diesem wurde der Sensor für 5 Minuten lang in kurzen Abständen ausgelesen, um ihn quasi zu kalibrieren. Es wurden die letzten 50 Gas-Werte benutzt um einen Mittelwert zu errechnen und dann eine \_Gas-Baseline* zu speichern. Anschließend wurde bei jedem neuen Auslesen, aus der Abweichung des Gas-Werts zur Baseline, in Kombination mit der Luftfeuchtigkeit (hierbei legt man den Idealwert selbst fest, z.B. 40%) einen _Luftqualitätsscore_ errechnen. Den Algorithmus zum Erstellen eines Basiswerts habe ich im Prinzip 1:1 übernommen:

```python
class WrappedSensor:

    def __init__(self):
        super().__init__()

        # 40% Luftfeuchtigkeit werden als optimal angesehen
        self.hum_baseline = 40.0

        # Definiert die Gewichtung zwischen Feuchtigkeit und Gas-Wert
        self.hum_weighting = 0.25

        self.gas_baseline = None
        self.did_complete_burnin = False

	# ...

    def burn_in_sensor(self):
        start_time = time.time()
        curr_time = time.time()
        burn_in_time = 300
        burn_in_data = []

        print("Collecting gas resistance burn-in data for 5 mins\n")

        while curr_time - start_time < burn_in_time:
            curr_time = time.time()
            if self.sensor.get_sensor_data() and self.sensor.data.heat_stable:
                gas = self.sensor.data.gas_resistance
                burn_in_data.append(gas)
                print("Gas: {0} Ohms, %RH: {1:.2f}".format(gas, self.sensor.data.humidity))
                time.sleep(5)

        self.gas_baseline = sum(burn_in_data[-50:]) / 50.0

        print("Gas baseline: {0} Ohms, humidity baseline: {1:.2f} %RH\n".format(self.gas_baseline, self.hum_baseline))
        self.did_complete_burnin = True
```

Bei der Berechnung des Scores, fand ich allerdings die resultierenden Werte eher unrealistisch, weshalb ich mich nach anderweitiger Inspiration umschaute. Ich fand eine [BME680-Example Repository](https://github.com/G6EJD/BME680-Example), die einen mir besser erscheinenden Algorithmus benutzte. Meine Implementation zur Berechnung sieht so aus:

```python
temperature_boundary = 100.0 if self.IDEAL_TEMPERATURE < data.temperature else -21.0
humidity_boundary = 100.0 if self.IDEAL_HUMIDITY < data.humidity else 0.0
gas_boundary = 500000 if self.gas_baseline < data.gas_resistance else 50000

# IDEAL_TEMPERATURE kann zum Beispiel als 21 definiert
temperature_deviation_from_ideal = (data.temperature - self.IDEAL_TEMPERATURE) / (temperature_boundary - self.IDEAL_TEMPERATURE)
temperature_score = temperature_deviation_from_ideal * 10

# IDEAL_HUMIDITY kann zum Beispiel als 40 definiert werden
humidity_deviation_from_ideal = (data.humidity - self.IDEAL_HUMIDITY) / (humidity_boundary - self.IDEAL_HUMIDITY)
humidity_score = humidity_deviation_from_ideal * 10

gas_deviation_from_ideal = (data.gas_resistance - self.gas_baseline) / (gas_boundary - self.gas_baseline)
gas_score = gas_deviation_from_ideal * 80

total_score = 100 - min(100.0, temperature_score + humidity_score + gas_score)
```

Zusammengefasst berechnet dieser Algorithmus eine Punktzahl von 0 bis 100. Je weiter die gemessenen Werte von den definierten Idealwerten abweichen, desto niedriger. Die Gewichtung hierbei ist folgendermaßen:

-   Temperatur 10%
-   Luftfeuchtigkeit 10%
-   Gaswiderstand 80%

Nun musste dieser Score von 0 bis 100 noch auf eine Skala von 1 bis 5 gemapped werden, was ich aber an dieser Stelle als trivial ansehe.

### Service Erstellung

Nun war ich mit der Implementation soweit fertig (abgesehen von kleineren Fixes), sodass ich das Ganze mal so richtig austesten wollte, sprich über längeren Zeitraum. Dafür erstellte ich also einen Service:

```bash
sudo nano /etc/systemd/system/bme680.service
```

Bei der folgenden Konfiguration des Service orientierte ich mich stark an einem [Beispiel von Rob Peck](https://www.robpeck.com/2017/11/using-pipenv-with-systemd/), da die Erstellung eines Service in Verbindung mit `pipenv` etwas trickreich ist. Man muss auf jeden Fall das `WorkingDirectory` spezifizieren, und den absoluten Pfad zu der gewünschten `pipenv`-Installation, sonst werden die installierten Packages nicht gefunden.

```bash
[Unit]
Description=HAP-python daemon
Wants=pigpiod.service
After=network-online.target pigpiod.service

[Service]
User=pi
Restart=always
# Script starting HAP-python, e.g. main.py
WorkingDirectory=/home/pi/bme680-homekit-accessory
ExecStart=/home/pi/.local/bin/pipenv run python /home/pi/bme680-homekit-accessory/main.py

[Install]
WantedBy=multi-user.target
```

Zur Erläuterung:

-   `Wants=pigpiod.service` definiert sozusagen eine Dependency auf einen anderen Service. In diesem Fall handelt es sich um den Service der die GPIO-Pins bereitstellt
-   `After=network-online.target pigpiod.service` sagt dem System, das der `bme680.service` erst gestartet werden soll, wenn das Netzwerk und die GPIO-Pins verfügbar sind
-   `ExecStart` ist der tatsächliche Befehl der vom System ausgeführt wird, hier starten wir den HAP-python Server

Ich muss wirklich mit vielen verschiedenen Kombination von absoluten und relativen Pfaden rumspielen, bevor ich eine Kombi fand, bei der `pipenv` alle Pfade und Packages richtig erkannte.

Anschließend habe ich den Service beim Boot aktiviert:

```bash
sudo systemctl enable bme680
```

Und um den Service sofort zu starten

```bash
sudo systemctl start bme680
```

Um zu überprüfen, ob auch alles läuft wie gewünscht, habe ich mir die Logs anzeigen lassen:

```bash
journalctl -u bme680 -b

-- Journal begins at Thu 2022-09-22 05:06:10 CEST, ends at Mon 2022-12-05 10:45:33 CET. --
Nov 29 10:40:26 raspberry-henrik systemd[1]: Started HAP-python daemon.
Nov 29 10:45:38 raspberry-henrik pipenv[774]: [accessory_driver] Loading Accessory state from `/home/p>
Nov 29 10:45:38 raspberry-henrik pipenv[774]: [accessory_driver] Starting the event loop
Nov 29 10:45:38 raspberry-henrik pipenv[774]: [accessory_driver] Starting accessory RaspiBridge on add>
Nov 29 10:45:38 raspberry-henrik pipenv[774]: [hap_protocol] ('192.168.178.26', 51488): Connection mad>
Nov 29 11:03:09 raspberry-henrik pipenv[774]: Collecting gas resistance burn-in data for 5 mins
Nov 29 11:03:09 raspberry-henrik pipenv[774]: Gas: 160272.1883473701 Ohms, %RH: 70.27
Nov 29 11:03:09 raspberry-henrik pipenv[774]: Gas: 252819.5008894688 Ohms, %RH: 70.20
Nov 29 11:03:09 raspberry-henrik pipenv[774]: Gas: 256348.43893691813 Ohms, %RH: 67.82
# ...
```

## Fazit

Alles in allem war es ein meiner Meinung nach sehr interessantes Projekt. Erstens wollte ich so etwas in die Richtung schon wirklich lange machen, da ich HomeKit spannend finde und außerdem mein Pi nur rumlag und ich schon fast ein schlechtes Gewissen entwickelt habe deswegen. Weiterhin habe ich wirklich viel gelernt, angefangen beim Löten, aber auch vor Allem softwareseitige Dinge, so wie Serviceerstellung und -konfiguration unter Linux, die Verwendung von `pipenv` und Python generell. Bisher hatte ich bisher mit Python nämlich nur sehr einfach Skripts geschrieben.

## Ausblick

Um das Projekt noch weiterzuführen, könnte man mehrere Dinge tun. Zum Einen könnte ich mehrere Raspberry Pis mit Sensoren ausstatten und so zum Beispiel die Luftqualität in meiner gesamten Wohnung messen. Zum Anderen könnte ich die gemessen Daten aber auch in irgendeiner Form mit ihrer jeweiligen Timestamp persistieren und dann einen zeitlichen Verlauf der Daten visualisieren, sodass man beispielsweise sehen kann, wann ich gelüftet habe (zumindest im Winter würde das nämlich logischerweise zu einem Temperatureinbruch führen).

## Quellen

-   Die meisten Quellen sind direkt im Text verlinkt
-   Bilder die nicht explizit gekennzeichnet sind, wurden von mir selbst aufgenommen
-   https://www.robpeck.com/2017/11/using-pipenv-with-systemd/
-   https://github.com/dnutiu/bme680-homekit/blob/master/sensors/main.py
-   https://github.com/ikalchev/HAP-python
-   https://pipenv.pypa.io/en/latest/
-   https://github.com/pyenv/pyenv
-   https://www.balena.io/etcher/
-   https://www.raspberrypi.com/software/
-   https://www.laub-home.de/wiki/Raspberry_Pi_BME680_Gas_Sensor
-   https://github.com/pimoroni/bme680-python
