import datetime
import math
import statistics
import time
import pyvisa


# keithley = rm.open_resource('GPIB0::16::INSTR')

class Device:
    def __init__(self, address, name, connected_device_name=None):
        self.connected_device_name = connected_device_name
        self.address = address
        self.name = name

    def connect(self):
        rm = pyvisa.ResourceManager()
        rm.list_resources()
        self.connected_device_name = rm.open_resource(self.address, timeout=6000)
        self.connected_device_name.write("*RST")
        return self.connected_device_name

    def IDN(self):
        print(f"Dane podłączonego urządzenia:\nNazwa: {self.name}\nIDN: {self.connected_device_name.query('*IDN?')}")


class Voltmeter(Device):
    def __init__(self, address, name):
        super().__init__(address, name)

    def AC_or_DC(self):
        self.connected_device_name.write("*RST")
        print("Wybierz tryb AC lub DC wpisując opowiednio te skróty")
        choice = input().upper()
        if choice == "AC":
            self.connected_device_name.write("FUNC 'VOLT:AC'")
            self.connected_device_name.write("UNIT:VOLT:AC V")
        elif choice == "DC":
            self.connected_device_name.write('FUNC "VOLT:DC"')
            self.connected_device_name.write("UNIT:VOLT:DC V")
        else:
            print("Dokonano złego wyboru")

    def RMS_or_Peak(self, Urms, type_of_result):
        if type_of_result.upper() == "PP":
            Upp = Urms * 2 * math.sqrt(2)
            return Upp
        elif type_of_result.upper() == "RMS":
            return Urms
        else:
            print("Nieprawidłowy wybór!")

    def read_level(self, freq):
        # self.connected_device_name.write("*RST")
        # self.connected_device_name.write(":SENS:VOLT:AC:RANG:AUTO OFF")  # ręcznie ustawienie zakresu woltomierza
        # self.connected_device_name.write(":SENS:VOLT:AC:RANG 1")  # ręcznie ustawienie zakresu woltomierza
        self.connected_device_name.write(":SENS:VOLT:AC:RANG:AUTO ON")
        self.connected_device_name.write("FUNC 'VOLT:AC'")
        self.connected_device_name.write("UNIT:VOLT:AC V")
        level_voltmeter = float(self.connected_device_name.query("read?"))
        return level_voltmeter


class SignalGenerator(Device):
    def __init__(self, address, name):
        super().__init__(address, name)

    def HighImpedance_or_Xohm(self, impedanceValue):
        if impedanceValue == "H":
            self.connected_device_name.write(f"OUTPut:LOAD INF")
        elif impedanceValue.isnumeric():
            self.connected_device_name.write(f"OUTPut:LOAD {impedanceValue}")
        else:
            print("Nieprawidłowy wybór")
            exit()

    def set_level(self, level_func):
        self.connected_device_name.write("VOLT:UNIT VOLT")
        self.connected_device_name.write(f":VOLT {level_func}")

    def power_on_off(self, mode):
        self.connected_device_name.write(f"OUTP {mode.upper()}")

    def set_single_frequency(self, f):
        self.connected_device_name.write(f"FREQ {f}")
        return f


def set_frequency_band():
    file = open("frequencies_txt", "r")
    frequencies = file.readlines()
    frequencies = [float(freq.replace(",", ".")) for freq in frequencies]
    return frequencies


def result_file_name(name, result_list, header):
    now = datetime.datetime.now()
    year = str(now.year)
    month = "%02d" % now.month
    day = "%02d" % now.day
    hour = "%02d" % now.hour
    minute = "%02d" % now.minute
    second = "%02d" % now.second
    prefix_name = year + month + day + "_" + hour + minute + second + "_"
    full_name_of_file = prefix_name + name + ".csv"
    result_txt = open(f"C:\\Users\\bglowacz\\PycharmProjects\\Praca_IL-PIB\\pliki wynikowe txt\\{full_name_of_file}",
                      "w")
    result_txt.write(f"f [Hz];U [{header}]\n")
    for x in result_list:
        result_txt.write(x.replace(".", ",") + "\n")
    result_txt.close()


keithley2000 = Voltmeter('GPIB0::16::INSTR', "Keithley")
keithley2000.connect()
keithley2000.IDN()
# keithley2000.AC_or_DC()

HMF2550 = SignalGenerator("ASRL3::INSTR", "HMF2550")
HMF2550.connect()
HMF2550.IDN()
HMF2550.power_on_off("ON")
print("Podaj impedancję generatora\nLiczbę - dla konkretnej wartości\nH - dla trybu wysokiej impedancji")
impedanceValue = input()
HMF2550.HighImpedance_or_Xohm(impedanceValue)
print("Podaj napięcie generatora: ")
generator_level = float(input())
HMF2550.set_level(generator_level)
frequency_list = set_frequency_band()

# ROZPOCZĘCIE POMIARU
result = []
print("Wpisz:\npp - dla rezultatu peak-peak\nrms - dla rezultatu w RMS")
pp_rms = input()
print("Wpisz:\ndB - dla wyniku z dBuV\nV - dla wyniku w V")
dB_V = input()
f_result = []
U_result = []

if dB_V not in ["V", "dB"]:
    print("Nieprawidłowy wybór")
    exit()
for f in frequency_list:
    frequency = float(HMF2550.set_single_frequency(f))
    print(f"f generatora = {frequency} Hz")
    time.sleep(0.5)
    level = abs(float(keithley2000.read_level(f)))
    level = keithley2000.RMS_or_Peak(level, pp_rms)  # p dla wartości peak, rms dla wartości rms
    if dB_V == "dB":
        level = 20 * math.log(level * pow(10, 6), 10)
    print(f"U = {level} {dB_V} {pp_rms}")
    f_result.append(frequency)
    U_result.append(level)
    result.append(str(frequency) + ";" + str(level))

# TU SIĘ DZIEJE STATYSTYKA
Uaver = statistics.mean(U_result)
modifier = 5
Uaver_modified = Uaver - modifier
# print(f_result)
# print(U_result)
print(f"średnia wartość napięcia to: {Uaver}")

# # DOMIAR ODSTAJĄCYCH WARTOŚCI
# print("Domiar:")
# for f, U in zip(f_result, U_result):
#     if U < Uaver_modified:
#         print(f"odczytana wartość {round(U, 5)}, na częstotliwości {f} jest mniejsza niż wartość średnia zmodyfikowana {round(Uaver_modified, 5)}")
#     elif U > Uaver_modified:
#         print(f"odczytana wartość {round(U, 5)}, na częstotliwości {f} jest większa niż wartość średnia zmodyfikowana {round(Uaver_modified, 5)}")
#         frequency = float(HMF2550.set_single_frequency(f))


HMF2550.power_on_off("off")

print("Nazwa pliku:")
file_name = input()
result_file_name(file_name, result, dB_V)
