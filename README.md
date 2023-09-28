## Tutorial on how to build an ultrasonic alarm system
**Author**: Viking Forsman
**Approximate time**: 3 hours

In this tutorial I will provide instructions on how to build an alarm system that is triggered via ultrasonic distance measuring. The basic idea behind this alarm system is that the alarm device is placed with an unobstructed view to a door. The user activates the system with a button press which initiates a countdown before the alarm is activated, which allows the user to leave and close the door. The system then performs periodic measurement of the distance to a door. A second countdown is triggered if the measured distance is deviating more than a specified threshold from the initial measurement. The system assumes that the person is an intruder if he or she does not press the button before the countdown finishes. If the countdown reaches its endpoint the system will start the emitting sounds with a passive buzzer and send a message to a REST API which in turn will trigger an SMS containing a warning to owner’s phone.

The required time to perform all steps in the tutorial is approximately three hours, but this may vary depending on how experienced the developer is with programming, electrical engineering and IoT.


### Objective
I choose this project because it is simple enough to be an introductory project while still providing plenty of opportunities for more experienced developers to expand the functionality the system. The finished system could serve as a deterrent from nosy family members or perhaps as a complementary home alarm system. The tutorial can provide some basic insight in how to connect the pycom device to sensors and actuators and how to push sensed data to an IoT platform. The data that is pushed to the platform is the alarm's status (offline, online, triggered, Unauthorized entry).


### Material
I got all the sensors and actuators in this project from a [bundle](https://www.kjell.com/se/produkter/el-verktyg/arduino/moduler/playknowlogy-stora-modul-paketet-for-arduino-p87291) sold by kjell & company, this bundle cost 499 SEK and it includes thirty-eight different modules. I acquired the LoPy 4, Expansion Board 3.0, breadboard and wires from [another bundle](https://www.electrokit.com/produkt/lnu-1dt305-tillampad-iot-lopy4-and-sensors-bundle/) which is sold by the company electrokit for 995 SEK. Lastly a [battery holder](https://www.electrokit.com/produkt/batterihallare-3xaaa-med-strombrytare-och-jst-kontakt) is necessary if the device should be runnable when not connected to a computer, the one I bought cost 29 SEK. Combined the total price for all material is 1523 SEK. However, for this tutorial not all components in the bundles are necessary and the required components can be purchased separately from several different vendors at a lower cost.


| Component | Usage | Image |
| -------- | -------- | -------- |
| Expansion Board 3.0 | Device to execute the code  on | ![](https://i.imgur.com/RqpGnTr.png) |
| LoPy 4 | Device to execute the code  on | ![](https://i.imgur.com/q7cKIk6.png) |
| Breadboard | Connects the components and pycom device | ![](https://i.imgur.com/sCYmmS4.png) |
| Wires | Connects the components and pycom device | ![](https://i.imgur.com/D1vRFit.png) |
| Dual ultrasonic sensor | Measure distance in ranges from 2 cm to 400 cm with a resolution of 0.3 cm | ![](https://i.imgur.com/T5v1pNT.png) |
| Button switch module | Button that can provide user input to the device | ![](https://i.imgur.com/wvj35Xc.png) |
| Passive buzzer module | Emit a range of sounds depending on the input frequency | ![](https://i.imgur.com/uWnW09x.png) |
| Battery Holder | Provide electricity to the device (output voltage of 3.3 – 4.5V) | ![](https://i.imgur.com/TDcgaDk.png) |


### Computer setup
The chosen IDE for this project is [Atom](https://atom.io/) which is a free and open source IDE that supports customizable commands and plugins. It is also one of the two IDE:s which supports the [pymakr](https://atom.io/packages/pymakr) plugin. I used this plugin since it provides an easy way to upload project files or directly execute commands on the pycom device. Atom is available for macOS 10.9 or later, Windows 7 and later, and Linux (RedHat or Ubuntu). 

The official pycom ["getting started guide"](https://docs.pycom.io/gettingstarted/) recommends that the expansion board's firmware should be updated before using the hardware. The pycom device will work out of the box for Windows 8 or later (I used Windows 10), otherwise additional drivers need to be installed. The firmware is continuously updated, and the most recent version is often the most stable version.  So, it is a good idea to keep the firmware updated. There is a [tool](https://software.pycom.io/findupgrade?product=pycom-firmware-updater&type=all&platform=win32&redirect=true) that allows the user to choose which version of the firmware to use.

### Putting everything together
The image below depict how the sensors and actuators are connected to the pycom device. 
![](https://i.imgur.com/PGMbEXA.png)


### Platform
The IoT platform I have chosen is [Ubidots](https://www.ubidots.com/) which enable users to send data to the cloud from internet-enabled devices. Ubidots can visualize the received data in dashboards that are customizable with HTML code and JavaScripts. Finally, Ubidots also allows the user to assign certain events to occur depending on the received data. These events include sending messages via SMS, email, slack or WebHocks.

Ubidots has a free version for educational or personal use but it has some limitations regarding the amount of active devices, messages and stored data. For this project the free version is more than sufficient, since we only need one active device and relatively few messages. 

Ubidots expects to receive messages with at most three fields: a value, a context, and a timestamp. The value part of the message is mandatory while the context and timestamp is optional. The value must be either an integer or float, nonnumerical values are not supported. However, nonnumerical information can be included in the optional context part of the message.  The timestamp can either be assigned by the device with Unix epoch time (in milliseconds) or this value will be assigned by the server when it is received.


### The code
The implementation is written in MicroPython which is a lean subset of python that is optimized for running on microcontrollers. I have tried to make the code easy to understand by including plenty of comments and print messages. The lopy LED light is used to indicate different states of the system. Green indicates that the alarm is offline and is waiting for activation, red indicate that the system is active, blue indicate that a timer has been initiated (either from starting the system or a threshold has been reached).

I will provide a brief description of the three main functions. The function **alarm_activation()** start a loop that exits when the button is pressed. The function **alarm_execute()** measure an initial distance and then start a loop in which the distance is remeasured. If the distance deviates more than 5 cm from the initial value or if the button is pressed the function returns a boolean value. If this boolean is true the **alarm_triggered()** function will be called, which starts a timer. If the button is pressed before the timer runs out the function exit, otherwise the passive buzzer will be actuated to emit sounds.


### Transmitting the data / connectivity
How often data is transmitted to the internet in this project is hard to determine, since no packages are scheduled in accordance to a time period. Instead the packages are transmitted based on events. The system sends a message when the alarm is activated or deactivated. The system also sends a message when the alarm is triggered, and if the alarm is not deactivated within a specified time frame another message is sent.

Initially, I considered transmitting data via the LoRa protocol since it has long range. Unfortunately, there were no gateways within a reasonable range where I live. Therefore I decided to use WiFi instead which has much more limited range but can send larger messages more frequent. The data is sent to via HTTP to the Ubidots REST API using the urequests module. 


### Presenting the data
The data that triggers the events are integers representing the states (offline, online, triggered, Unauthorized entry). The context information are strings that contains the alarm status in written form, which is less cryptic, so that is what I chose to display in the log table. The most recently received status information is presented in the widget on the top. The dot chart on the right visually displays when the messages were received and the system status in integer form, the X-axis represents the time and the Y-axis the status value. It is hard to determine how often data is saved, due to the same reason as in the previous section. 
![](https://i.imgur.com/CQbXJ5C.png)



### Finalizing the design
![](https://i.imgur.com/tJT0zHL.jpg)


I am quite happy with the outcome with the project, especially since it was my first time working with IoT. I had hoped to be able to try LoRa when connecting the pycome to the internet, since it seems to be prevalent in IoT projects. But the only gateway in my vicinity was 4 km away on ground level inside a building. I had to get really close to get a connection with this gateway, which would have been too impractical during the development process. For my next IoT project I will probably try to use sigfox.

An improvement on the current implementation would be to assign the context information in the server instead of sending this information from the device, since this would reduce the overall size of the messages. This could be done with the HTML Canvas widget in Ubidots, which allows the user to define dynamic behavior based on the received data using JavaScripts. Another possible improvement would have been to provide a 3d printed case so that it could be safely transpored and used in outdoor environments.

![](https://i.imgur.com/R6UxSMu.jpg)
