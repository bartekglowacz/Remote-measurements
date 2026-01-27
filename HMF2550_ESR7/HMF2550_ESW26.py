import datetime
import time
import pyvisa


class Receiver:
    def __init__(self, address, name):
        self.address = address
        self.name = name

    def connect(self):
        rm = pyvisa.ResourceManager()
        rm.list_resources()
        self.name = rm.open_resource(self.address)
        # self.name.timeout = 10000
        self.name.write("*RST")
        return self.name

    def IDN(self):
        print(f"Dane podłączonego urządzenia: {self.name.query('*IDN?')}")

    def set_Frequency(self, frequency):  # frequency in MHz
        self.name.write(f"FREQ:CENT {str(frequency)}MHz")

    def input_coupling(self, f):
        if f > 10:
            self.name.write("INP:COUP AC")
        else:
            self.name.write("INP:COUP DC")

    def detector(self):
        print("Jaki detektor wariacie?\n1 - peak\n2 - average\n3 - quasi peak (dostępny od 100 Hz)")
        choice = int(input())
        if choice == 1:
            self.name.write("DET:REC POS")
        elif choice == 2:
            self.name.write("DET:REC AVER")
        elif choice == 3:
            self.name.write("DET:REC QPE")
        else:
            print("Nieprawidłowy wybór")

    def auto_attenuator(self):
        self.name.write("INP:ATT:AUTO ON")

    def sweep_time(self, f):
        if f < 100 / pow(10, 6):
            sweep_time = 1
        elif 100 / pow(10, 6) <= f < 1000 / pow(10, 6):
            sweep_time = 0.1
        elif 1000 / pow(10, 6) <= f < 10000 / pow(10, 6):
            sweep_time = 0.1
        elif 10000 / pow(10, 6) <= f < 100000 / pow(10, 6):
            sweep_time = 0.05
        elif 100000 / pow(10, 6) <= f < 120000 / pow(10, 6):
            sweep_time = 0.05
        elif 120000 / pow(10, 6) <= f < 1000000000 / pow(10, 6):
            sweep_time = 0.01
        elif 1000000000 / pow(10, 6) <= f < 7000000000 / pow(10, 6):
            sweep_time = 0.01
        self.name.write(f"SWE:TIME {sweep_time}s")
        return sweep_time

    def read_RBW(self):
        rbw_value = self.name.query('BAND?')
        print(f"RBW: {rbw_value}")
        return rbw_value

    def read_level(self, f):
        self.name.write(":DISP:BARG:PHOL:RES")
        if str(self.name.query("DET:REC?")).strip() == "QPE":
            print(f"Wykryto detektor {self.name.query('DET:REC?')}, jestem w pętli quasi-peak")
            multiplier = 2
            if f < 0.0001:
                time.sleep(3 * multiplier)
                level_tmp = self.name.query("trac? single")
            elif 0.0001 <= f < 0.001:
                time.sleep(2 * multiplier)
                level_tmp = self.name.query("trac? single")
            elif f >= 0.001:
                time.sleep(1 * multiplier)
                level_tmp = self.name.query("trac? single")
            return level_tmp
        elif str(self.name.query("DET:REC?")).strip() == "AVER":
            print(f"Wykryto detektor {self.name.query('DET:REC?')}, jestem w pętli aver")
            multiplier = 1
            if f < 0.0001:
                time.sleep(6 * multiplier)
                level_tmp = self.name.query("trac? single")
            elif 0.0001 <= f < 0.001:
                time.sleep(1.5 * multiplier)
                level_tmp = self.name.query("trac? single")
            elif f >= 0.001:
                time.sleep(0.5 * multiplier)
                level_tmp = self.name.query("trac? single")
            return level_tmp
        else:
            print(f"Wykryto detektor {self.name.query('DET:REC?')}, jestem w pętli peak")
            if f < 0.0001:
                time.sleep(3)
                level_tmp = self.name.query("trac? single")
            elif 0.0001 <= f < 0.001:
                time.sleep(2)
                level_tmp = self.name.query("trac? single")
            elif f >= 0.001:
                time.sleep(2)
                level_tmp = self.name.query("trac? single")
            return level_tmp


class HMF2550:
    def __init__(self, address, name):
        self.address = address
        self.name = name

    def connect(self):
        rm = pyvisa.ResourceManager()
        rm.list_resources()
        self.name = rm.open_resource(self.address)
        self.name.write("*RST")
        return self.name

    def IDN(self):
        print(f"Dane podłączonego urządzenia: {self.name.query('*IDN?')}")

    def power_on_off(self, mode):  # ON or OFF
        self.name.write(f"OUTP {mode.upper()}")

    def HighImpedance_or_Xohm(self):
        print("Podaj impedancję generatora\nDla trybu High Impedance wpisz ""H""")
        impedanceValue = input().upper()
        if impedanceValue == "H":
            self.name.write(f"OUTPut:LOAD INF")
        elif impedanceValue.isnumeric():
            self.name.write(f"OUTPut:LOAD {impedanceValue}")
        else:
            print("Nieprawidłowy wybór")
            exit()

    def set_level(self):
        print("Opcje:\n1 - V\n2 - dBm")
        choice = int(input())
        if choice == 1:
            self.name.write("VOLT:UNIT VOLT")
            print("Podaj poziom generatora")
            genLevel = float(input())
            self.name.write(f":VOLT {genLevel}")
            print(f"Poziom generatora: {genLevel} V")
        elif choice == 2:
            self.name.write("VOLT:UNIT DBM")
            print("Podaj poziom generatora")
            genLevel = float(input())
            self.name.write(f":VOLT {genLevel}")
            print(f"Poziom generatora: {genLevel} dBm")
        else:
            print("Nieprawidłowy wybór")

    def set_single_frequency(self, f):  # w Hz!
        self.name.write(f"FREQ {f * pow(10, 6)}")
        return f


def frequency_table(txt_file):
    print("1 - częstotliwości podane w Hz\n2 - częstotlwiości podane w MHz")
    choice = int(input())
    if choice == 1:
        txt_file = open(txt_file, "r")
        txt_file = [float(f.replace(",", ".")) / pow(10, 6) for f in txt_file]  # displayed in MHz
    elif choice == 2:
        txt_file = open(txt_file, "r")
        txt_file = [float(f.replace(",", ".")) for f in txt_file]  # displayed in MHz
    # print(txt_file)
    return txt_file


def result_file_name(name, result_list):
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
    result_txt.write(f"f [Hz];U [dBuV]\n")
    for x in result_list:
        result_txt.write(x.replace(".", ","))
    result_txt.close()


receiver = Receiver("TCPIP::172.19.1.170::inst0::INSTR", "ESR7")
receiver.connect()
receiver.IDN()
receiver.detector()
receiver.auto_attenuator()
signalGenerator = HMF2550("ASRL3::INSTR", "HMF2550")
signalGenerator.connect()
signalGenerator.IDN()
signalGenerator.HighImpedance_or_Xohm()
signalGenerator.set_level()

# signalGenerator.set_single_frequency(1)  # w MHz
signalGenerator.power_on_off("ON")
# receiver.set_Frequency(30)
# print(f"LEVEL: {receiver.read_level()}")  # w MHz


results = []
for f in frequency_table("C:\\Users\\bglowacz\\PycharmProjects\\Praca_IL-PIB\\HMF2550_ESR7\\frequencies_txt"):
    freq = signalGenerator.set_single_frequency(f)
    print(f"Częstotliwość generatora: {freq} MHz")
    receiver.sweep_time(float(f))
    receiver.input_coupling(f)
    receiver.set_Frequency(f)
    level = '{:.6f}'.format(float(receiver.read_level(f)))
    print(f"Poziom na odbiorniku: {level} dBμV")
    results.append(str(freq) + ";" + str(level) + "\n")
signalGenerator.power_on_off("OFF")

print("Nazwa pliku:")
file_name = input()
result_file_name(file_name, results)
