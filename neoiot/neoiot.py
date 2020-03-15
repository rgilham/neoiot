
from time import sleep
from threading import Thread

class Gpio:
    def __init__(self ,reset=False):
        self.gpios = {24 :6 ,36 :67 ,19 :203 ,25 :2 ,27 :3 ,31 :64 ,33 :65 ,35 :66 ,6 :363 ,7 :17 ,23 :0 ,34 :1}
        pinno = self.gpios.keys()
        v = [0 ] *len(self.gpios)
        self.gpiodir = dict(zip(pinno ,v))
        self.gpioval = dict(zip(pinno ,v))
        self.OUTPUT = 1
        self.INPUT = 0
        self.HIGH = 1
        self.LOW = 0
        if (reset):
            for key, value in self.gpios.items():
                try:
                    with open("/sys/class/gpio/export", "w") as create:
                        create.write("%d" % value)
                        create.close()
                    with open("/sys/class/gpio/gpio%d/direction" % value, "w") as writedir:
                        writedir.write('in')
                except:
                    pass

    def pinMode(self, pin, direction=0):
        try:
            gpio = self.gpios[int(pin)]
            if int(direction) != self.gpiodir[pin]:
                with open("/sys/class/gpio/gpio%d/direction" % gpio, "w") as writer:
                    writer.write("in" if direction < 1 else "out")
                    writer.close()
                self.gpiodir[pin] = (0 if direction < 1 else 1)
            return True
        except KeyError:
            print ("ERROR: Invalid pin %s" % pin)
            return False
        except ValueError:
            print ("ERROR: pinMode, value inserted wasn't an int")
            return False
        except:
            print ("ERROR: pinMode, error using pinMode")
            return False
    def digitalWrite(self, pin, value=0):
        try:
            gpio = self.gpios[int(pin)]
            if self.gpiodir[pin] != 1:
                with open("/sys/class/gpio/gpio%d/direction" % gpio, "w") as re:
                    re.write("out")
                self.gpiodir[pin] = 1
            with open("/sys/class/gpio/gpio%d/value" % gpio, "w") as writes:
                writes.write("0" if value < 1 else "1")
            self.gpioval[pin] = (0 if value < 1 else 1)
            return True
        except KeyError:
            print ("ERROR: Invalid pin %s" % pin)
            return False
        except ValueError:
            print ("ERROR: digitalWrite, value inserted wasn't an int")
            return False
        except:
            print ("ERROR: digitalWrite, error running")
            return False

    def digitalRead(self, pin):
        try:
            gpio = self.gpios[int(pin)]
            if self.gpiodir[pin] != 0:
                with open("/sys/class/gpio/gpio%d/direction" %gpio, "w") as re:
                    re.write("in")
                self.gpiodir[pin] = 0
            with open("/sys/class/gpio/gpio%d/value" % gpio, "r") as reader:
                self.gpioval[pin] = int(reader.read().replace('\n', ''))
            return self.gpioval[pin]
        except KeyError:
            print("ERROR: Invalid pin %s" % pin)
            return False
        except ValueError:
            print("ERROR: digitalRead, value inserted wasn't an int")
            return -1
        except:
            print("ERROR: digitalRead, error running")
            return -1


class easyGpio():
    def __init__(self, pin):
        self.pin = int(pin)
        self.gpio = Gpio()
        self.value = 0

    def pinOUT(self):
        self.gpio.pinMode(self.pin, 1)

    def pinIN(self):
        self.gpio.pinMode(self.pin, 0)

    def on(self):
        self.gpio.digitalWrite(self.pin, 1)
        self.value = 1

    def off(self):
        self.gpio.digitalWrite(self.pin, 0)
        self.value = 0

    def toggle(self):
        self.value ^= 1
        self.gpio.digitalWrite(self.pin, self.value)

    def get(self):
        return self.gpio.digitalRead(self.pin)

    def getValue(self):
        return self.value


class BlueLed:
    def __init__(self):
        self.led = 0

    def on(self):
        with open("/sys/class/leds/nanopi:blue:status/brightness", "w") as w:
            w.write("1")

    def off(self):
        with open("/sys/class/leds/nanopi:blue:status/brightness", "w") as w:
            w.write("0")


class GreenLed:
    def __init__(self):
        self.led = 0

    def on(self):
        with open("/sys/class/leds/nanopi:green:pwr/brightness", "w") as w:
            w.write("1")

    def off(self):
        with open("/sys/class/leds/nanopi:green:pwr/brightness", "w") as w:
            w.write("0")


class Output:
    def __init__(self, pin):
        self.relayIO = easyGpio(pin)

    def On(self):
        self.relayIO.on()

    def Off(self):
        self.relayIO.off()

    def Toggle(self):
        self.relayIO.toggle()

    def Pulse(self, duration):
        self.relayIO.on()
        threading.Timer(duration, self.Off).start()

    def Value(self):
        return self.relayIO.getValue()


class Input:
    RISING = 0
    FALLING = 1
    BOTH = 2

    def __init__(self, pin, callback=None, direction=BOTH):
        self.inp = easyGpio(pin)
        self.inp.pinIN()
        self.callback = callback
        self.direction = direction
        self.value = self.Value()
        if not (self.callback == None):
            self.t = threading.Thread(target=self.__readValue)
            self.t.daemon = True
            self.t.start()

    def setChangeCallback(self, callback=None, direction=BOTH):
        if not (self.callback == None):
            self.t.__stop()
            self.t.join()
        self.callback = callback
        self.direction = direction
        if not (self.callback == None):
            self.t = threading.Thread(target=self.__readValue)
            self.t.daemon = True
            self.t.start()

    def Value(self):
        return self.inp.get()

    def isHigh(self):
        return self.inp.get() == 1

    def isLow(self):
        return self.inp.get() == 0

    def __readValue(self):
        while True:
            currentValue = self.Value()
            if not (self.value == currentValue):
                if (self.value == 0):
                    direction = Input.RISING
                else:
                    direction = Input.FALLING
                if (self.direction == Input.BOTH):
                    self.callback(currentValue, direction)
                elif (self.direction == direction):
                    self.callback(currentValue, direction)
            self.value = currentValue
            time.sleep(0.1)


class __Relay1(Output):
    def __init__(self):
        Output.__init__(self, 35)


class __Relay2(Output):
    def __init__(self):
        Output.__init__(self, 36)


class __ModemPwr(Output):
    def __init__(self):
        Output.__init__(self, 6)


class __SIMSel:
    def __init__(self):
        self.Select = Output(33)
        self.selected = 0
        self.INTERNAL = 1
        self.EXTERNAL = 0

    def Internal(self):
        self.Select.Off()
        self.selected = self.INTERNAL

    def External(self):
        self.Select.On()
        self.selected = self.EXTERNAL

    def getSelected(self):
        return self.selected


class __USB2Pwr(Output):
    def __init__(self):
        Output.__init__(self, 7)


class __LED(Output):
    def __init__(self):
        Output.__init__(self, 31)


class __DOUT0(Output):
    def __init__(self):
        Output.__init__(self, 24)


class __DOUT1(Output):
    def __init__(self):
        Output.__init__(self, 23)


class __Input1(Input):
    def __init__(self, callback=None, direction=Input.BOTH):
        Input.__init__(self, 27, callback, direction)


class __Input2(Input):
    def __init__(self, callback=None, direction=Input.BOTH):
        Input.__init__(self, 19, callback, direction)


class __OptoIn(Input):
    def __init__(self, callback=None, direction=Input.BOTH):
        Input.__init__(self, 34, callback, direction)

gpio = Gpio(True)
Relay1 = __Relay1()
Relay2  = __Relay2()
ModemPwr = __ModemPwr()
SIMSel = __SIMSel()
USB2Pwr = __USB2Pwr()
DOUT0 = __DOUT0()
DOUT1 = __DOUT1()
Input1 = __Input1()
Input2 = __Input2()
OptoIn = __OptoIn()
LED = __LED()