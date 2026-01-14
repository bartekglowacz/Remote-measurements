#!/usr/bin/env python3  #shebang line

"""
    visa to pakiet Pythona, który umożliwia sterowanie wszelkiego rodzaju
    urządzeniami pomiarowymi niezależnie od interfejsu (GPIB, RS232, USB, Ethernet).
"""
import pyvisa as visa

version = "1.0.0 Released December 2023"


class visaDevice:
    """
        Klasa visaDevice służy do obługi urządzenia, udostępniając użytkownikowi
        operacja otwarcia/zamknięcia połączenia z/do urządzenia, operacji zapisu
        i odczytu oraz wykonanie zapytania
    """

    def __init__(self, ip, open_timeout=10000):
        self.ip = ip
        self.address = 'TCPIP::' + ip + '::INSTR'
        self.open_timeout = open_timeout
        self.opened = False
        self.instr = None

    def isopen(self) -> bool:
        return self.opened and True or False

    def open(self):
        if not self.opened:
            self.instr = visa.ResourceManager().open_resource(resource_name=self.address,
                                                              open_timeout=self.open_timeout)
            self.opened = True
        return self.instr.session

    def close(self):
        if self.opened:
            self.instr.close()
            self.opened = False
        return

    def get_ip(self) -> str:
        return self.ip

    def get_address(self) -> str:
        return self.address

    def get_session(self):
        if self.opened:
            return self.instr.session
        return None

    def read(self) -> str:
        if not self.opened:
            self.open()
        return self.instr.read()

    def write(self, strCmd: str):
        if not self.opened:
            self.open()
        self.instr.write(strCmd)

    def query(self, strQuery: str, remove_new_line_character=True) -> str:
        if not self.opened:
            self.open()
        """
            If our device (open in the variable inst) has been configured to transfer data 
            in ASCII when the command is issued, we can just query the values using this:
            query_ascii_values(strQuery) or query(strQuery)
        """
        answer = self.instr.query(strQuery)
        return answer.replace('\n', '') if remove_new_line_character else answer

    def query_ascii_values(self, strQuery: str):
        return self.instr.query_ascii_values(strQuery)

    def query_ascii_value(self, strQuery: str) -> str:
        return self.instr.query_ascii_values(strQuery)[0]

    def reset(self):
        """
        Funkcja wykonuje reset urządzenia. Ustawienia przywracane są do wartości domyślnych
        :return:
        """
        self.write('*RST')

    rst = reset

    def clear_status(self):
        """
        Funkcja czyści zawartość rejestru statusu
        """
        self.write('*CLS')

    cls = clear_status

    def reset_and_clear_status(self):
        """
        Funkcja resetowania urządzenia oraz czyszczenie zawartości rejestru statusu
        :return:
        """
        self.write('*RST;*CLS')

    rstcls = reset_and_clear_status

    def get_identifier(self) -> str:
        """
        Funkcja odczytuje identyfikator urządzenia (odpowiedź na zapytanie ^IDN?)
        :return:
        """
        return self.query('*IDN?')

    def get_stb(self) -> int:
        """
        Funkcja zwraca wartość zapisana w rejestrze statusu STB (Status Byte Register)
        """
        return int(self.query('*STB?'))

    def set_sre_mask(self, mask: int):
        """
        Funkcja ustawia maskę rejestru zdarzeń SRE (Service Request Enable Register)
        :param mask: maska zdarzeń, wartość typu byte, złożona z flag poszeczgólnych
        zdarzeń, sumowanych za pomocą funkcji OR
        :return:
        :remarks: bit 6 nie jest używany
        """
        cmd = '*SRE ' + format(mask & 0b10111111, 'd')
        self.write(cmd)

    def get_sre_mask(self) -> int:
        """
        Funkcja odczytuje aktualną wartość maski rejestru zdarzeń SRE (Service Enable Register)
        :return: Wartość maski rejestru zdarzeń SRE
        """
        return int(self.query('*SRE?'))

    def get_esr(self) -> int:
        """"
        Funkcja zwraca zawartość rejestru zdarzeń ESR (Event Status Register)
        """
        return int(self.query('*ESR?'))

    def set_ese_mask(self, mask):
        """
        Funkcja ustawia maskę rejestru ESE (Event Status Enable Register)
        :param mask:
        :return:
        """
        cmd = '*ESE ' + format(mask & 0xff, 'd')
        self.write(cmd)

    def get_ese_mask(self) -> int:
        """
        Funkcja zwraca zawartość rejestru ESE (Event Status Enable Register)
        :return:
        """
        return int(self.query('*ESE?'))


class SMF1000A(visaDevice):
    """
        Klasa generatora sygnału mikrofalowego SMF 100A firmy Rhode & Schwarz
    """

    def __init__(self, ip):
        super().__init__(ip)
        self.unit = "dBuV".upper()
        self.att_mode: str = 'auto'
        self.att_value = 0
        self.pow_level = 55

    def __str__(self):
        return "R&S® SMF 100A Microwave Signal Generator"

    def set_attenuator(self, mode='auto', value=0):
        """
        Funkcja ustawiania tłumika wyjściowego nadajnika
        :param mode: określa tryb pracy tłumka równy odpowiednio 'auto' lub 'fixed'
        :param value: określa wartość tłumienia, w decybelach, dla trybu 'fixed'
        w zakresie od 0 do 110 dB z krokiem 10 dB
        Po resecie urządzenia ('*RST') wartość tłumienia równa jest 0 dB
        :return:
        """
        if mode in ('auto', 'fixed'):
            self.att_mode = mode
            cmd = ""
            if mode == 'auto':
                self.att_mode = mode
                cmd = "OUTP:AMOD AUTO"
            elif (mode == 'fixed') and (value is not None) and (type(value) in (int, float)):
                value = (0 if value < 0 else (110 if value > 100 else value))
                self.att_value = value
                cmd = "OUTP:AMOD FIX;SOUR:POW:ATT {0}".format(value)
            self.write(cmd)

    def set_frequency(self, frequency):
        """
        Funkcja ustawienia częstotliwosci
        :param frequency: częstotliwość, w MHz
        :return:
        """
        self.write('FREQ {0} MHz'.format(frequency))

    def set_unit(self, unit='DBUV'):
        """
        Funkcja określająca domyślną jednostkę dla mocy
        Po wykonaniu resetu urządzenia (komenda *RST), wartość jednostki mocy ustawiona jest na 'DBM'
        :param unit: idenyfikator jednostki mocy : 'V', 'DBUV', 'DBM'
        :return: None
        """
        self.unit = unit.upper()
        self.write("UNIT:POW {0}".format(self.unit))

    def set_generator(self, onoff):
        """
        Funkcja włączenia (on)/ wyłączenia (off) generatora
        :param onoff: wartość zero (0) lub True oznacza włączenie, pozostałe przypadki
        to wyłaczenie generatora
        :return:
        """
        cmd = 'OUTP {0}'.format("ON" if onoff else "OFF")
        self.write(cmd)

    def set_level(self, level):
        """
        Funkcja ustawiania poziomu sygnału na wyjściu nadajnika
        :param level: wartość poziomu na wyjściu nadajnika w wybranych jednostkach
        :return:
        """
        self.pow_level = level
        cmd = 'POW {0} {1}'.format(level, self.unit)
        self.write(cmd)


class ESU40(visaDevice):
    """
        Klasa odbiornika ESU 40 firmy Rhode & Schwarz
    """

    def __init__(self, ip):
        super().__init__(ip)
        self.att_mode: str = 'auto'
        self.att_value = 0
        self.coupling_mode: str = 'AC'
        self.detector_type: str = 'AVER'
        self.bw_mode: str = 'auto'
        self.bw_value = 500
        self.span = 200

    def __str__(self) -> str:
        return 'R&S® ESU EMI Test Receiver'

    def set_if_mode(self):
        self.write('INST:SEL IFAN')

    def set_input_port(self, input_number):
        self.write('INP:TYPE INPUTP{0}'.format(input_number))

    def set_coupling(self, acFlag):
        """
        Funkcja ustawienia sprzęgu (coupling) :param acFlag: flaga typu boolean, której wartość True określa sprzęg
        AC, w przeciwnym wypadku (wartość False) to sprzęg DC :return:
        """
        cmd = 'INP:COUP {0}'.format('AC' if acFlag else 'DC')
        self.write(cmd)

    def get_coupling(self) -> str:
        return self.query('INP:COUP?')

    def set_detector(self, averFlag):
        """
        Funkcja ustawienia detektora :param averFlag: flaga typu boolean, której wartość True określa detektor
        wartości średniej, w przeciwnym wypadku (wartość False) wartości szczytowej :return:
        """
        cmd = 'DET:REC {0}'.format('AVER' if averFlag else 'POS')
        self.write(cmd)

    def get_detector(self) -> str:
        return self.query('DET:REC?')

    def set_span(self, span):
        """
        Funkcja ustawia szerokości pasma wykresu (span)
        :param span: wartość szerokości pasma wykresu, w kHz, z zakresu od 1 do 1000 kHz
        :return:
        """
        span = 1 if span < 1 else (1000 if span > 1000 else span)
        cmd = 'FREQ:SPAN {0} kHz'.format(span)
        self.write(cmd)

    def get_span(self):
        return self.query('FREQ:SPAN?')

    def set_attenuator(self, level='auto'):
        """
        Funkcja ustawienia tłumika na wejściu odbiornika
        :param level: jeżeli wartość równa jest 'auto', to tłumienie ustawiane jest w  tryb auto
        w przeciwnym wypadku wartość level, w decybelach, określa wartość tłumika
        :return:
        """
        cmd = None
        if (type(level) is str) and (level == 'auto'):
            self.att_mode = 'auto'
            cmd = 'INP:ATT:AUTO ON'
        elif type(level) in (int, float):
            self.att_mode = 'fixed'
            self.att_value = level
            cmd = 'INP:ATT:AUTO {0};INP:ATT {1} dB'.format('ON' if level == 'auto' else 'OFF', level)
        if cmd is not None:
            self.write(cmd)

    def set_center_frequency(self, frequency):
        """
        Funkcja ustawienia częstotliwości środkowej odbiornika.
        Częstotliwość środkowa musi być ustawiona na co najmniej dwukrotność szerokości pasma IF.
        Gdy częstotliwość środkowa jest niższa niż dwukrotność szerokości pasma IF,
        szerokość pasma IF jest automatycznie zmniejszana, tak żeby warunek był ponownie spełniony.
        :param frequency: częstotliwość strojenia, w MHz
        :return:
        """
        cmd = 'FREQ:CENT {0} MHz'.format(frequency)
        self.write(cmd)

    def get_center_frequency(self) -> float:
        """
        Funkcja zwraca częśtotliość środkową
        :return: częstotliwość, w Hz
        """
        return float(self.query('SENS:FREQ:CENT?'))

    def set_center_frequency_and_span(self, frequency, span):
        """
        Funkcja ustawia szerokości pasma wykresu (span)
        :param frequency: częstotliwość, w MHz
        :param span: wartość szerokości pasma wykresu, w kHz, z zakresu od 1 do 1000 kHz
        :return:
        """
        span = 1 if span < 1 else (1000 if span > 1000 else span)
        cmd = 'FREQ:CENT {0} MHz; SPAN {1} kHz'.format(frequency, span)
        self.write(cmd)

    def set_measure_time(self, time):
        """
        Funkcja ustawienia czasu pomiaru

        :param time: 'auto' dla trybu według tabeli z rozdziału 4.5.4.2 'Setting the Measurement Time' \
        dokumentu R&S®ESU EMI Test Receiver Operating Manual 1302.6163.12 - 04, lub wartość typu int lub float \
        w milisekundach (ms)
        :return:
        """
        cmd = None
        if isinstance(time, str) and (time == 'auto'):
            bandwidth = int(self.get_bandwidth())
            if bandwidth <= 10:
                cmd = 'SWE:TIME 1s'
            if bandwidth == 100:
                cmd = 'SWE:TIME 100ms'
            if 200 <= bandwidth <= 300:
                cmd = 'SWE:TIME 50ms'
            if 1000 <= bandwidth <= 3000:
                cmd = 'SWE:TIME 10ms'
            if 9000 <= bandwidth <= 30000:
                cmd = 'SWE:TIME 1ms'
            if bandwidth >= 100000:
                cmd = 'SWE:TIME 0.1ms'
        elif type(time) in ('int', 'float'):
            # odejście od zaleceń producenta i ustawienie czasu pomiaru wg. użytkownika
            cmd = 'SWE:TIME {0}ms'.format(time)
        if cmd is not None:
            self.write(cmd)
        return

    def set_bandwidth(self, bandwidth):
        """

        :param bandwidth: Szerokość pasma, w Hz
        :return:
        """
        if bandwidth in ('auto', 'manual'):
            cmd = ''
            if bandwidth == 'auto':
                self.bw_mode = 'auto'
                cmd = 'BAND:AUTO ON'
            elif type(bandwidth) in ('int', 'float'):
                self.bw_mode = 'fixed'
                self.bw_value = bandwidth
                cmd = 'BAND: {0}HZ'.format(bandwidth)
            self.write(cmd)

    def get_bandwidth(self):
        """

        :return: Wartość szerokości pasma jako wyrażenie łańcuchowe (str)
        """
        return self.query('BAND?')

    def start_calculation(self, input_number=1, marker_number=1):
        self.write('CALC{0}:MARK{1}:MAX'.format(input_number, marker_number))

    def get_calc_level(self, input_number=1, marker_number=1) -> float:
        return float(self.query('CALC{0}:MARK{1}:Y1?'.format(input_number, marker_number).replace('\n', '')))

    def get_calc_level_str(self, input_number=1, marker_number=1, remove_new_line_char=True) -> str:
        answer = self.query('CALC{0}:MARK{1}:Y1?'.format(input_number, marker_number))
        return answer.replace('\n', '') if remove_new_line_char is True else answer

    def get_calc_level_int(self, input_number=1, marker_number=1) -> int:
        return int(self.query('CALC{0}:MARK{1}:Y1?'.format(input_number, marker_number)).replace('\n', ''))

    def get_calc_level_float(self, input_number=1, marker_number=1) -> float:
        return self.get_calc_level(input_number, marker_number)


class FSV3030(visaDevice):
    """
        Klasa analizatora FSV3030 firmy Rhode & Schwarz
    """

    def __init__(self, ip):
        super().__init__(ip)

    def get_att_mode_auto_bool(self) -> bool:
        return int(self.query("INP:ATT:AUTO?").replace("\n", "")) == 1

    def get_att_mode_auto_str(self) -> str:
        return 'ON' if int(self.query("INP:ATT:AUTO?").replace("\n", "")) == 1 else 'OFF'

    def get_att_mode_auto_int(self) -> int:
        return int(self.query("INP:ATT:AUTO?").replace("\n", ""))

    def set_att_mode_auto(self, mode):
        if isinstance(mode, str) and mode.upper() in ['ON', 'OFF']:
            auto_mode = mode.upper()
        elif isinstance(mode, bool):
            auto_mode = "ON" if mode is True else "OFF"
        elif isinstance(mode, int):
            auto_mode = "OFF" if mode == 0 else "ON"
        else:
            return
        if auto_mode in ['ON', 'OFF']:
            self.write("INP:ATT:AUTO {0}".format(auto_mode))
        return

    def get_att(self) -> float:
        return float(self.query("INP:ATT?"))

    def set_att(self, att: float):
        self.write("INP:ATT {0}".format(att))

    def get_coupling(self) -> str:
        return self.query("INP:COUP?")

    def set_coupling(self, coupling: str):
        coupling = coupling.upper()
        if coupling in ['AC', 'DC']:
            self.write("INP:COUP {0}".format(coupling))

    def get_center_frequency(self) -> float:
        return float(self.query("FREQ:CENT?"))

    def set_center_frequency(self, frequency, unit='MHz'):
        unit = unit.upper()
        if unit in ['HZ', 'KHZ', 'MHZ', 'GHZ']:
            self.write("FREQ:CENT {0} {1}".format(frequency, unit))

    def get_frequency_offset(self) -> float:
        return float(self.query('FREQ:OFFS?'))

    def set_frequency_offset(self, offset: float = 0.0, unit: str = 'Hz'):
        unit = unit.upper()
        if unit in ['HZ', 'KHZ', 'MHZ']:
            self.write(f'FREQ:OFFS {offset} {unit}')

    def get_preamplifier_state(self) -> str:
        return 'ON' if int(self.query("INP:GAIN:STATE?")) == 1 else 'OFF'

    def is_preamplifier_state_on(self) -> bool:
        """
        Funkcja zwraca wartość logiczną prawda jeżeli przedwzmacniacz jest włączony.
        W przeciwnym wypadku zwracana jest wartośĆ fałsz
        :return: prawda jeżeli przedwzmacniacz jest włączony, w przeciwnym wypadku zwracana jest wartośĆ fałsz
        """
        return self.get_preamplifier_state() == 'ON'

    def is_preamplifier_state_off(self) -> bool:
        """
        Funkcja zwraca wartość logiczną prawda jeżeli przedwzmacniacz jest wyłączony.
        W przeciwnym wypadku zwracana jest wartośĆ fałsz
        :return: prawda jeżeli przedwzmacniacz jest wyłączony, w przeciwnym wypadku zwracana jest wartośĆ fałsz
        """
        return self.get_preamplifier_state() == 'OFF'

    def set_preamplifier_state(self, state: str):
        """
        Ustawienie stanu przedwzmacniacza
        :param state: 'ON' (przedwzmacniacz zostaje włączony), 'OFF' (przedwzmacniacz zostaje wyłączony)
        :return:
        """
        state = state.upper()
        if state in ['ON', 'OFF']:
            self.write("INP:GAIN:STATE {0}".format(state))

    def set_preamplifier_state_on(self):
        self.set_preamplifier_state('ON')

    def set_preamplifier_state_off(self):
        self.set_preamplifier_state('OFF')

    def set_preamplifier_gain(self, gain):
        if self.is_preamplifier_state_on() and (gain in [15, 30]):
            self.write("INP:GAIN:VAL {0}".format(gain))

    def get_span_value(self) -> float:
        return float(self.query("FREQ:SPAN?"))

    def set_span_value(self, value, unit='Hz'):
        unit = unit.upper()
        self.write("FREQ:SPAN {0} {1}".format(value, unit))

    def get_power_unit(self) -> str:
        return self.query("UNIT:POW?")

    def set_power_unit(self, unit: str = 'dBuV'):
        unit = unit.upper()
        if unit in ['A', 'AMP', 'DBM', 'DBMV', 'DBUV', 'DBPW', 'DBUA', 'WATT', 'VOLT', 'V']:
            self.write("UNIT:POW {0}".format(unit))

    def get_bandwidth_auto_mode_str(self) -> str:
        return "ON" if int(self.query("BAND:AUTO?")) == 1 else "OFF"

    def get_bandwidth_auto_mode_int(self) -> int:
        return int(self.query("BAND:AUTO?"))

    def get_bandwidth_auto_mode_bool(self) -> bool:
        return int(self.query("BAND:AUTO?")) == 1

    def is_bandwidth_auto_mode_on(self) -> bool:
        return self.get_bandwidth_auto_mode_bool()

    def is_bandwidth_auto_mode_off(self) -> bool:
        return self.get_bandwidth_auto_mode_bool()

    def set_bandwidth_auto_mode(self, mode):
        if isinstance(mode, bool):
            self.write("BAND:AUTO {0}".format('ON' if mode is True else 'OFF'))
            return
        if isinstance(mode,int):
            self.write("BAND:AUTO {0}".format('OFF' if mode == 0 else 'ON'))
            return
        if isinstance(mode, str) and (mode.upper() in ['ON', 'OFF']):
            self.write("BAND:AUTO {0}".format(mode.upper()))

    def set_bandwidth_auto_mode_on(self):
        self.set_bandwidth_auto_mode("ON")

    def set_bandwidth_auto_mode_off(self):
        self.set_bandwidth_auto_mode("OFF")

    def get_measure_time(self) -> float:
        """
        Funkcja zwraca wartość czasu pomiaru w sekundach
        :return:
        """
        return float(self.query("SWE:TIME?"))

    def set_measure_time(self, time, unit='s'):
        unit = unit.upper()
        if unit in ['MS', 'S']:
            self.write("SWE:TIME {0} {1}".format(time, unit))

    def get_input_connector(self) -> str:
        """
        Określa, z którego złącza pobierane jest sygnał do pomiaru.
        Jeśli aktywny jest zewnętrzny frontend, złącze jest automatycznie ustawiane na RF.
        :return:
            'RF' dla wejscia sygnału radiowego (RF)
            'RFPR' dla wejscia próbnika sygnału
        """
        return self.query("INP:CONN?")

    def set_input_connector(self, connector: str):
        """
        Określa, z którego złącza pobierane jest sygnał do pomiaru.
        :param connector: 'RF lub 'RFPR'
        :return:
        """
        if isinstance(connector, str) and connector.upper() in ['RF', 'RFPR']:
            self.write("INP:CONN {0}".format(connector.upper()))

    def get_bandwidth(self) -> float:
        """
        Funkcja zwraca szerokoś pasma, w Hz
        :return: Szerokoś pasma, w Hz
        """
        return float(self.query("BAND?").replace('\n', ''))

    def set_bandwidth(self, bandwidth: float, unit: str):
        unit = unit.upper()
        if unit in ['Hz', 'kHz', 'MHz']:
            self.write("BAND {0} {1}".format(bandwidth, unit))

    def set_reference_level_mode_auto(self):
        return

    def set_reference_level_mode_manual(self):
        return

    def set_reference_level_value(self, value: float):
        return

    def start_calculation(self, input_number=1, marker_number=1):
        self.write('CALC{0}:MARK{1}:MAX'.format(input_number, marker_number))

    def get_calc_level(self, input_number=1, marker_number=1) -> float:
        return float(self.query('CALC{0}:MARK{1}:Y1?'.format(input_number, marker_number)))
