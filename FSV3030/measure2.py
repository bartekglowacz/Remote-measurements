# measure2.py
# https://www.pysimplegui.org/en/latest/cookbook/#recipe-save-and-load-program-settings
# https://www.pythontutorial.net/python-concurrency/python-async-await/
# https://stackoverflow.com/questions/70497095/implementing-asyncio-with-pysimplegui

import yaml
import datetime as dt
import os.path
import time
import numpy as np
import PySimpleGUI as sg
import matplotlib.figure as figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from device import *

version = __version__ = "1.1.1 Released 11-June-2024"

print(f"PySimpleGUI version {sg.version}")
print(f"PyVISA version {visa.__version__}")
print(f"PyYAML version {yaml.__version__}")
print(f"Application version {version}")

"""
    os.path.splitext - Split the pathname path into a pair (root, ext) such that root + ext = path, 
    and the extension, ext, is empty or begins with a period and contains at most one period. 
    If the filename has multiple dots, only the extension after the last one is removed
"""
yaml_file = os.path.splitext(__file__)[0] + '.yaml'
print(f"Application configuration YAML file: {yaml_file}")
config_file = open(yaml_file, 'r')
app_config = yaml.safe_load(config_file)

tr_selected = app_config["init"]["selected-transmitter"]
# print(f"Last selected transmitter is '{tr_selected}'")
rec_selected = app_config["init"]["selected-receiver"]
# print(f"Last selected receiver is '{rec_selected}'")

tr_selected_index = -1
trCount = len(app_config["config"]["transmitters"])
trs_list = []

print(f"Liczba nadajników: {trCount}")
for i in range(0, trCount):
    print(f"\tNadajnik #{i + 1}:")
    print(f"\t\tNazwa: {app_config['config']['transmitters'][i]['name']}")
    trs_list.append(app_config['config']['transmitters'][i]['name'])
    if app_config["config"]["transmitters"][i]["name"] == tr_selected:
        tr_selected_index = i
    print(f"\t\tAdres MAC: {app_config['config']['transmitters'][i]['mac'].upper()}")
    print(f"\t\tAdres IPv4: {app_config['config']['transmitters'][i]['ip']}")
    print(f"\t\tID: {app_config['config']['transmitters'][i]['idn']}")

transmitter_ip = app_config["config"]["transmitters"][tr_selected_index]["ip"]
transmitter_name = app_config["config"]["transmitters"][tr_selected_index]["name"]

recs_list = []
rec_selected_index = -1
recCount = len(app_config["config"]["receivers"])

print(f"Liczba odbiorników: {recCount}")
for i in range(0, recCount):
    print(f"\tOdbiornik #{i + 1}:")
    print(f"\t\tNazwa: {app_config['config']['receivers'][i]['name']}")
    recs_list.append(app_config["config"]["receivers"][i]["name"])
    if app_config["config"]["receivers"][i]["name"] == rec_selected:
        rec_selected_index = i
    print(f"\t\tAdres MAC: {app_config['config']['receivers'][i]['mac'].upper()}")
    print(f"\t\tAdres IPv4: {app_config['config']['receivers'][i]['ip']}")
    print(f"\t\tID: {app_config['config']['receivers'][i]['idn']}")
    if app_config["config"]["receivers"][i]["name"] == "FSV3030":
        device = FSV3030(app_config["config"]["receivers"][i]["ip"])
        print(f"\nFSV3030 VISA address is {device.get_address()}")

receiver_ip = app_config["config"]["receivers"][rec_selected_index]["ip"]
receiver_name = app_config["config"]["receivers"][rec_selected_index]["name"]
"""
print(f"Wybrany nadajnik {transmitter_name} ({transmitter_ip})\n"
      f"Wybrany odbiornik {receiver_name} ({receiver_ip})")
"""
rec_tab_first_entry: bool = True

FIGURE_WIDTH = 720
FIGURE_HEIGHT = 400

# nazwy elemntów graficznych

TR_ATT_AUTO = '-TRATTAUTO-'
TR_ATT_MANUAL = '-TRATTMANUAL-'
TR_ATT_VALUE = "-TRATTVALUE-"

TR_LEVEL = '-TRLEVEL-'

ESU_ATT_AUTO = '-ESUATTAUTO-'
ESU_ATT_MANUAL = '-ESUATTMANUAL-'
ESU_ATT_VALUE = "-ESUATTVALUE-"

ESU_BAND_AUTO = '-ESURBWAUTO-'
ESU_BAND_MANUAL = '-ESURBWMANUAL-'
ESU_BAND_VALUE = '-ESURBWVALUE-'
ESU_BAND_VALUE_UNIT = '-ESURBWUNIT-'

ESU_INPUT_PORT = '-ESURF_INPUT-'

ESU_DETECTOR_AVER = "-ESUDETAVER-"
ESU_DETECTOR_PEAK = "-ESUDETPEAK-"

ESU_SPAN = "-ESURECSPAN-"
ESU_MARKER = "-ESURECMARK-"
ESU_COUPLING_AC = "-ESUCOUPLAC-"
ESU_COUPLING_DC = "-ESUCOUPLDC-"

ESU_MEAS_TIME_AUTO = '-ESUMEASTIMEAUTO-'
ESU_MEAS_TIME_MANUAL = '-ESUMEASTIMEMANUAL-'
ESU_MEAS_TIME_VALUE = "-ESUMEASTIMEALUE-"

FSV_ATT_AUTO = '-FSVATTAUTO-'
FSV_ATT_MANUAL = '-FSVUATTMANUAL-'
FSV_ATT_VALUE = "-FSVATTVALUE-"

FSV_COUPLING_AC = "-FSVCOUPL_AC-"
FSV_COUPLING_DC = "-FSVCOUPL_DC-"
FSV_COUPLING_AUTO = "-FSVCOUPL_AUTO"

FSV_PREAMP_OFF = "-FSVPREAMPOFF-"
FSV_PREAMP_15 = "-FSVPREAMP15-"
FSV_PREAMP_30 = "-FSVPREAMP30-"

FSV_REF_LEVEL_AUTO = "-FSVREFLVLAUTO-"
FSV_REF_LEVEL_MANUAL = "-FSVREFLVLMANUAL-"
FSV_REF_LEVEL_VALUE = "-FSVREFLVLVALUE-"

FSV_INPUT_PORT = "-FSVINPUT-"
FSV_MARKER = "-FSVMARKER-"

FSV_BANDWIDTH_VALUE = "-FSVBANDVALUE-"
FSV_BANDWIDTH_UNIT = "-FSVBANDUNIT-"

FSV_MTIME_VALUE = "-FSVMTIMEVALUE-"
FSV_MTIME_UNIT = "-FSVMTIMEUNIT-"

FSV_SPAN_VALUE = "-FSVSPANVALUE-"
FSV_SPAN_UNIT = "-FSVSPANUNIT-"

MEAS_REPEAT = '-MEASREPEAT-'
MEAS_REPEAT_TRIGGER = '-REPTRIGGER-'
MEAS_REPEAT_COUNT = '-REPCOUNT-'

FREQFILENAME = '-FRQFILE-'
FREQ_LB = '-FRQLIST-'
DATA_SEPARATOR = '-SEPARATOR-'
DATA_HEADER = '-HEADER-'

DO_MEASURE = '-DOMEASURE-'

RESULTS_LB = '-RESULTS_LB-'
RESULT_FILE = '-RESULTFILE-'
PREFIX_CHK = '-CHECKPREFIX-'

FILESAVE_BTN = '-FILESAVEBTN-'
SAVEFILENAME = '-SAVEFILENAME-'

CONFIG_READ = '-CONFIGREAD-'
CONFIG_SAVE = '-CONFIGSAVE-'

STATMSG = '-STATUS-'

RECS_COMBO = "RECS_COMBO"
RECS_GROUP = "RECS_GROUP"

TRS_COMBO = "TRS_COMBO"
TRS_GROUP = "TRS_GROUP"

ON_COLOR = 'white'
OFF_COLOR = 'black'

# instantiate matplotlib figure
fig = figure.Figure()
ax = fig.add_subplot(111)
DPI = fig.get_dpi()
fig.set_size_inches(FIGURE_WIDTH / float(DPI), FIGURE_HEIGHT / float(DPI))

sg.theme("Dark Blue 3")


def clear_listbox(listbox_name, wnd):
    wnd[listbox_name].update("")
    return


def clear_frequency_listbox(wnd):
    clear_listbox(FREQ_LB, wnd)
    return


def update_frequency_listbox(wnd, contents):
    wnd[FREQ_LB].update(contents)


def clear_result_listbox(wnd):
    clear_listbox(RESULTS_LB, wnd)
    return


def read_frequency_from_file_and_fill_listbox(filename, wnd) -> bool:
    if filename == '':
        return False
    with open(filename, 'r') as f:
        contents = [s.strip('\n') for s in f.readlines()]
    contents[:] = [s for s in contents if s]
    lst = sorted(set(float(s) for s in contents if s))
    contents = [str(f) for f in lst]
    clear_frequency_listbox(wnd)
    clear_result_listbox(wnd)
    clear_figure(wnd)
    update_frequency_listbox(wnd, contents)
    enable_filesave_button(wnd, enable=False)
    msg = "Odczyt częstotliwości z pliku '{}'".format(filename)
    print(msg)
    set_status(wnd, msg)
    return True


def show_visa_exception_popup(title, info, error_code, abbreviation, description):
    if error_code < 0:
        error_code = error_code + 2 ** 32
    error_code = "0x" + hex(error_code).upper()[2:]
    msg = f"{info}\n{abbreviation} ({error_code})\n\n{description}"
    sg.popup(msg, title=title, keep_on_top=True)


#
# funkcje zapisu/odczytu do/z urządzeń
#
def init_transmitter(transmitter):
    if (transmitter is None) or (not transmitter.isopen):
        return
    transmitter.reset_and_clear_status()
    # po resecie:
    #    wartość tłumienia róna jest 0 dB,
    #    jednostka ustawiona jest na dBm
    transmitter.set_unit("dBuV")


def init_receiver(receiver):
    if (receiver is None) or (not receiver.isopen):
        return
    receiver.reset_and_clear_status()


def set_smf100a_transmitter_parameters(transmitter: SMF1000A, values):
    if (transmitter is None) or (not transmitter.isopen):
        return
    print('Ustawienia nadajnika:')
    if values[TR_ATT_AUTO] is True:
        print('Tłumik w trybie auto')
        transmitter.set_attenuator('auto')
    else:
        attValue = float(values[TR_ATT_VALUE])
        print('Tłumik w trybie manual, wartość {0:2.0f} dB'.format(attValue))
        transmitter.set_attenuator('fixed', attValue)
    level = float(values[TR_LEVEL])
    print('Poziom napięcia {0:4.1f} dBuV'.format(level))
    transmitter.set_level(level)
    transmitter.set_generator(onoff=True)


def set_esu_receiver_parameters(receiver: ESU40, values):
    if (receiver is None) or (not receiver.isopen):
        return
    print('Ustawinia odbiornika ESU40:')
    # tłumik wyjściowy
    if values[ESU_ATT_AUTO]:
        print('Tłumik w trybie auto')
        receiver.set_attenuator('auto')
    else:
        attValue = float(str(values[ESU_ATT_VALUE]).replace(',', '.'))
        print('Tłumik w trybie manual, wartość {0:2.0f} dB'.format(attValue))
        receiver.set_attenuator(attValue)
    # detector
    print('Detektor: wartość {0}'.format('średnia' if values[ESU_DETECTOR_AVER] else 'szczytowa'))
    receiver.set_detector(values[ESU_DETECTOR_AVER])
    # cupling
    print('Coupling: {0}'.format('AC' if values[ESU_COUPLING_AC] else 'DC'))
    receiver.set_coupling(values[ESU_COUPLING_AC])
    # span
    span = float(str(values[ESU_SPAN]).replace(',', '.'))
    print('Span: {0} kHz'.format(span))
    receiver.set_span(span)
    # pasmo filtru
    esu_bandwidth = 'auto' if values[ESU_BAND_AUTO] else (
        float(str(values[ESU_BAND_VALUE]).replace(',', '.')))
    print('Pasmo filtra: {0}'.format('auto' if values[ESU_BAND_AUTO] else
                                     ('manual, ' + str(esu_bandwidth) + ' kHz')))
    receiver.set_bandwidth(esu_bandwidth)
    # czas trwania pomiaru
    esu_meas_time = 'auto' if values[ESU_MEAS_TIME_AUTO] else (
        float(str(values[ESU_MEAS_TIME_VALUE]).replace(',', '.')))
    print('Czas pomiaru: {0}'.format('auto' if values[ESU_MEAS_TIME_AUTO] else
                                     ('manual, ' + str(esu_meas_time) + ' ms')))
    receiver.set_measure_time(esu_meas_time)
    print('Wejście sygnału RF: {0}\nMarker używany przy pomiarze: {1}'.format(int(values[ESU_INPUT_PORT]),
                                                                              int(values[ESU_MARKER])))
    return


def set_fsv_receiver_parameters(receiver: FSV3030, values):
    receiver.set_input_connector('RF')
    receiver.set_power_unit('DBUV')
    receiver.set_bandwidth_auto_mode_off()
    receiver.set_frequency_offset(0)
    if values[FSV_ATT_AUTO] is True:
        receiver.set_att_mode_auto(True)
    else:
        receiver.set_att_mode_auto(False)
        receiver.set_att(float(values[FSV_ATT_VALUE]))
    if values[FSV_COUPLING_AUTO] is False:
        receiver.set_coupling('AC' if values[FSV_COUPLING_AC] else 'DC')
    if values[FSV_PREAMP_OFF] is True:
        receiver.set_preamplifier_state_on()
    else:
        receiver.set_preamplifier_state_off()
        receiver.set_preamplifier_gain(15 if values[FSV_PREAMP_15] else 30)
    """
    if values[FSV_REF_LEVEL_AUTO] is True:
        receiver.set_reference_level_mode_auto()
    else:
        receiver.set_reference_level_mode_manual()
        receiver.set_reference_level_value(float(str(values[FSV_REF_LEVEL_VALUE]).replace(',', '.')))
    """
    receiver.set_measure_time(float(values[FSV_MTIME_VALUE].replace(",", ".")), str(values[FSV_MTIME_UNIT]))
    receiver.set_bandwidth(float(values[FSV_BANDWIDTH_VALUE].replace(",", ".")), str(values[FSV_BANDWIDTH_UNIT]))
    receiver.set_span_value(float(values[FSV_SPAN_VALUE].replace(",", ".")), str(values[FSV_SPAN_UNIT]))
    return


def schedule_sfm_transmitter_attenuator_auto_event(wnd, values, event):
    if values[TR_ATT_AUTO]:
        wnd[TR_ATT_AUTO].update(text_color=ON_COLOR)
        wnd[TR_ATT_MANUAL].update(text_color=OFF_COLOR)
        wnd[TR_ATT_VALUE].update(disabled=True)
    return


def schedule_sfm_transmitter_attenuator_manual_event(wnd, values, event):
    if values[TR_ATT_MANUAL] is True:
        wnd[TR_ATT_MANUAL].update(text_color=ON_COLOR)
        wnd[TR_ATT_AUTO].update(text_color=OFF_COLOR)
        wnd[TR_ATT_VALUE].update(disabled=False)
    return


def schedule_esu_receiver_attenuator_auto_event(wnd, values, event):
    if values[ESU_ATT_AUTO]:
        wnd[ESU_ATT_AUTO].update(text_color=ON_COLOR)
        wnd[ESU_ATT_MANUAL].update(text_color=OFF_COLOR)
        wnd[ESU_ATT_VALUE].update(disabled=True)
    return


def schedule_esu_receiver_attenuator_manual_event(wnd, values, event):
    if values[ESU_ATT_MANUAL] is True:
        wnd[ESU_ATT_MANUAL].update(text_color=ON_COLOR)
        wnd[ESU_ATT_AUTO].update(text_color=OFF_COLOR)
        wnd[ESU_ATT_VALUE].update(disabled=False)
    return


def schedule_esu_receiver_peak_detector_event(wnd, values, event):
    if values[ESU_DETECTOR_PEAK] is True:
        wnd[ESU_DETECTOR_PEAK].update(text_color=ON_COLOR)
        wnd[ESU_DETECTOR_AVER].update(text_color=OFF_COLOR)
    return


def schedule_esu_receiver_average_detector_event(wnd, values, event):
    if values[ESU_DETECTOR_AVER] is True:
        wnd[ESU_DETECTOR_AVER].update(text_color=ON_COLOR)
        wnd[ESU_DETECTOR_PEAK].update(text_color=OFF_COLOR)
    return


def schedule_esu_receiver_coupling_ac_event(wnd, values, event):
    if values[ESU_COUPLING_AC] is True:
        wnd[ESU_COUPLING_AC].update(text_color=ON_COLOR)
        wnd[ESU_COUPLING_DC].update(text_color=OFF_COLOR)
        return


def schedule_esu_receiver_coupling_dc_event(wnd, values, event):
    if values[ESU_COUPLING_DC] is True:
        wnd[ESU_COUPLING_DC].update(text_color=ON_COLOR)
        wnd[ESU_COUPLING_AC].update(text_color=OFF_COLOR)
    return


def schedule_esu_receiver_measure_time_auto_event(wnd, values, event):
    if values[ESU_MEAS_TIME_AUTO] is True:
        wnd[ESU_MEAS_TIME_AUTO].update(text_color=ON_COLOR)
        wnd[ESU_MEAS_TIME_MANUAL].update(text_color=OFF_COLOR)
        wnd[ESU_MEAS_TIME_VALUE].update(disabled=True)
    return


def schedule_esu_receiver_measure_time_manual_event(wnd, values, event):
    if values[ESU_MEAS_TIME_MANUAL] is True:
        wnd[ESU_MEAS_TIME_MANUAL].update(text_color=ON_COLOR)
        wnd[ESU_MEAS_TIME_AUTO].update(text_color=OFF_COLOR)
        wnd[ESU_MEAS_TIME_VALUE].update(disabled=False)
    return


def schedule_esu_receiver_bandwidth_auto_event(wnd, values, event):
    if values[ESU_BAND_AUTO] is True:
        wnd[ESU_BAND_AUTO].update(text_color=ON_COLOR)
        wnd[ESU_BAND_MANUAL].update(text_color=OFF_COLOR)
        wnd[ESU_BAND_VALUE].update(disabled=True)
    return


def schedule_esu_receiver_bandwidth_manual_event(wnd, values, event):
    if values[ESU_BAND_MANUAL] is True:
        wnd[ESU_BAND_MANUAL].update(text_color=ON_COLOR)
        wnd[ESU_BAND_AUTO].update(text_color=OFF_COLOR)
        wnd[ESU_BAND_VALUE].update(disabled=False)
    return


# obsługa zdarzeń FSV
def schedule_fsv_receiver_attenuator_auto_event(wnd, values, event):
    if values[FSV_ATT_AUTO]:
        wnd[FSV_ATT_AUTO].update(text_color=ON_COLOR)
        wnd[FSV_ATT_MANUAL].update(text_color=OFF_COLOR)
        wnd[FSV_ATT_VALUE].update(disabled=True)
    return


def schedule_fsv_receiver_attenuator_manual_event(wnd, values, event):
    if values[FSV_ATT_MANUAL] is True:
        wnd[FSV_ATT_MANUAL].update(text_color=ON_COLOR)
        wnd[FSV_ATT_AUTO].update(text_color=OFF_COLOR)
        wnd[FSV_ATT_VALUE].update(disabled=False)
    return


def schedule_fsv_receiver_coupling_ac_event(wnd, values, event):
    if values[FSV_COUPLING_AC] is True:
        wnd[FSV_COUPLING_AC].update(text_color=ON_COLOR)
        wnd[FSV_COUPLING_DC].update(text_color=OFF_COLOR)
        wnd[FSV_COUPLING_AUTO].update(text_color=OFF_COLOR)
        return


def schedule_fsv_receiver_coupling_dc_event(wnd, values, event):
    if values[FSV_COUPLING_DC] is True:
        wnd[FSV_COUPLING_AC].update(text_color=OFF_COLOR)
        wnd[FSV_COUPLING_DC].update(text_color=ON_COLOR)
        wnd[FSV_COUPLING_AUTO].update(text_color=OFF_COLOR)
    return


def schedule_fsv_receiver_coupling_auto_event(wnd, values, event):
    if values[FSV_COUPLING_AUTO] is True:
        wnd[FSV_COUPLING_DC].update(text_color=OFF_COLOR)
        wnd[FSV_COUPLING_AC].update(text_color=OFF_COLOR)
        wnd[FSV_COUPLING_AUTO].update(text_color=ON_COLOR)
    return


def schedule_fsv_receiver_preamp_off_event(wnd, values, event):
    if values[FSV_PREAMP_OFF] is True:
        wnd[FSV_PREAMP_OFF].update(text_color=ON_COLOR)
        wnd[FSV_PREAMP_15].update(text_color=OFF_COLOR)
        wnd[FSV_PREAMP_30].update(text_color=OFF_COLOR)
        return


def schedule_fsv_receiver_preamp_15_event(wnd, values, event):
    if values[FSV_PREAMP_15] is True:
        wnd[FSV_PREAMP_OFF].update(text_color=OFF_COLOR)
        wnd[FSV_PREAMP_15].update(text_color=ON_COLOR)
        wnd[FSV_PREAMP_30].update(text_color=OFF_COLOR)
    return


def schedule_fsv_receiver_preamp_30_event(wnd, values, event):
    if values[FSV_PREAMP_30] is True:
        wnd[FSV_PREAMP_OFF].update(text_color=OFF_COLOR)
        wnd[FSV_PREAMP_15].update(text_color=OFF_COLOR)
        wnd[FSV_PREAMP_30].update(text_color=ON_COLOR)
    return


def schedule_fsv_receiver_ref_level_auto_event(wnd, values, event):
    if values[FSV_REF_LEVEL_AUTO]:
        wnd[FSV_REF_LEVEL_AUTO].update(text_color=ON_COLOR)
        wnd[FSV_REF_LEVEL_MANUAL].update(text_color=OFF_COLOR)
        wnd[FSV_REF_LEVEL_VALUE].update(disabled=True)
    return


def schedule_fsv_receiver_ref_level_manual_event(wnd, values, event):
    if values[FSV_REF_LEVEL_MANUAL] is True:
        wnd[FSV_REF_LEVEL_MANUAL].update(text_color=ON_COLOR)
        wnd[FSV_REF_LEVEL_AUTO].update(text_color=OFF_COLOR)
        wnd[FSV_REF_LEVEL_VALUE].update(disabled=False)
    return


# pozostałe zdarzenia

def schedule_event_repeat_measure_trigger(wnd, values, event):
    text_color = ON_COLOR if values[MEAS_REPEAT] is True else OFF_COLOR
    input_disabled = False if values[MEAS_REPEAT] is True else True
    wnd[MEAS_REPEAT].update(text_color=text_color)
    wnd[MEAS_REPEAT_TRIGGER].update(disabled=input_disabled)
    wnd[MEAS_REPEAT_COUNT].update(disabled=input_disabled)
    return


def schedule_event_filename_prefix(wnd, values, event):
    text_color = ON_COLOR if values[PREFIX_CHK] is True else OFF_COLOR
    wnd[PREFIX_CHK].update(text_color=text_color)
    return


def schedule_event_data_header(wnd, values, event):
    text_color = ON_COLOR if values[DATA_HEADER] is True else OFF_COLOR
    wnd[DATA_HEADER].update(text_color=text_color)
    return


def schedule_browse_frequency_file_event(wnd, values, event):
    frequency_file = values[FREQFILENAME]
    read_frequency_from_file_and_fill_listbox(frequency_file, wnd)
    return


def schedule_measurement_event(wnd, values, event):
    if not wnd[FREQ_LB].Values:
        sg.popup('Lista częstotliwości jest pusta', title='Wykonaj pomiar')
    else:
        if type(wnd[FREQ_LB].Values[0]) is float:
            frequencies = wnd[FREQ_LB].Values
        elif type(wnd[FREQ_LB].Values[0]) is str:
            frequencies = [float(s.replace(',', '.')) for s in wnd[FREQ_LB].Values if s]
        else:
            sg.popup('Elementy listy częstotliwości nie są liczbami\nani wyrażeniami łańcuchowymi',
                     title='Wykonaj pomiar')
            return
        n = len(frequencies)
        if n > 0:
            clear_result_listbox(wnd)
            clear_figure(wnd)

            try:
                transmitter = SMF1000A(transmitter_ip)
                transmitter.open()
                print('Identyfikator nadajnika: {0}'.format(transmitter.get_identifier()))
            except visa.errors.VisaIOError as e:
                title = "Wyjątek"
                info = "Przy otwieraniu połączenia z nadajnikiem wystąił wyjątek"
                show_visa_exception_popup(title, info, e.error_code, e.abbreviation, e.description)
                return

            try:
                match rec_selected:
                    case "ESU40":
                        receiver = ESU40(receiver_ip)
                    case "FSV3030":
                        receiver = FSV3030(receiver_ip)
                    case _:
                        sg.popup('Brak zdefiniowanego odbiornika', title='Wykonaj pomiar')
                        return
                receiver.open()
                print(f'Identyfikator odbiornika: {receiver.get_identifier()}')
            except visa.errors.VisaIOError as e:
                title = "Wyjątek"
                info = "Przy otwieraniu połączenia z odbiornikiem wystąił wyjątek"
                show_visa_exception_popup(title, info, e.error_code, e.abbreviation, e.description)
                transmitter.close()
                return

            init_transmitter(transmitter)
            time.sleep(1.0)
            init_receiver(receiver)
            time.sleep(1.0)

            set_smf100a_transmitter_parameters(transmitter, values=values)
            time.sleep(1.0)

            """
                wait_time - czas oczekiwania na odczyt wynku, w sekundach
                measure_time -  czas pomiaru, w sekundach lub w milisekundach - konwersja do sekund
            """
            wait_time = float(app_config['measurement']['wait-time'])
            time_prefix = 0.001 if (
                    app_config['config']['receivers'][rec_selected_index]['settings']['mtime']['unit'] == 'ms') else 1.0
            measure_time = float(
                app_config['config']['receivers'][rec_selected_index]['settings']['mtime']['value']) * time_prefix
            if wait_time < measure_time:
                wait_time = measure_time

            coupling_auto = False
            match rec_selected:
                case "ESU40":
                    set_esu_receiver_parameters(receiver, values=values)
                    time.sleep(1.0)
                    rec_input = int(values[ESU_INPUT_PORT])
                    rec_marker = int(values[ESU_MARKER])
                case "FSV3030":
                    set_fsv_receiver_parameters(receiver, values)
                    time.sleep(1.0)
                    rec_input = int(values[FSV_INPUT_PORT])
                    rec_marker = int(values[FSV_MARKER])
                    coupling_auto = values[FSV_COUPLING_AUTO] is True
                case _:
                    sg.popup('Brak zdefiniowanego odbiornika', title='Wykonaj pomiar')
                    transmitter.close()
                    receiver.close()
                    return

            # wnd[FILESAVE_BTN].update(disabled=False)

            indices = range(0, n)
            e = []
            success = True
            coupling = ''

            for k in indices:
                if success:
                    freq = frequencies[k]

                    msg = 'Pomiar dla częstotliwości {0:9.3f} MHz ... '.format(freq)
                    print(msg, end='')
                    set_status(wnd, msg)

                    transmitter.set_frequency(freq)

                    if (freq == 30000) and (rec_selected == 'FSV3030'):
                        freq = 29999.995
                    receiver.set_center_frequency(freq)

                    if coupling_auto:
                        if coupling == '':
                            coupling = receiver.get_coupling()
                        coupling_required = 'AC' if freq > 10.0 else 'DC'
                        if coupling_required != coupling:
                            receiver.set_coupling(coupling_required)
                            coupling = coupling_required
                            time.sleep(0.5)

                    success = sg.one_line_progress_meter('Postęp obliczeń', k + 1, n,
                                                         msg, keep_on_top=True)
                    receiver.start_calculation(rec_input, rec_marker)
                    """
                    On Windows, if secs is zero, the thread relinquishes the remainder of its time slice 
                    to any other thread that is ready to run. If there are no other threads ready to run, 
                    the function returns immediately, and the thread continues execution. 
                    On Windows 8.1 and newer the implementation uses a high-resolution timer 
                    which provides resolution of 100 nanoseconds. If secs is zero, Sleep(0) is used.
                    """
                    time.sleep(wait_time)
                    level_received = round(receiver.get_calc_level(rec_input, rec_marker), 2)

                    if k == 0:
                        receiver.start_calculation(rec_input, rec_marker)
                        time.sleep(wait_time)
                        level_received = round(receiver.get_calc_level(rec_input, rec_marker), 2)

                    msg = 'Pomiar dla częstotliwości {0:9.3f} MHz ... {1:6.2f} dBuV'.format(freq, level_received)
                    set_status(wnd, msg)
                    msg = '{0:6.2f} dBuV'.format(level_received)
                    print(msg, end='\n')

                    e.append(level_received)
                    update_results_listbox(wnd, e)
                    plot_figure(wnd, frequencies, np.array(e))
                    time.sleep(0.75)

            if success:
                msg = "Zakończono obliczenia"
                print(msg)
                set_status(wnd, msg)
                plot_figure(wnd, frequencies, np.array(e))
                enable_filesave_button(wnd, enable=True)
                sg.one_line_progress_meter_cancel()
                sg.popup_ok(msg, title='Wykonaj pomiar')
            else:
                answer = sg.popup_yes_no('Czy chesz zachować wyniki dotychczasowych pomiarów ?',
                                         title='YesNo', keep_on_top=True)
                if answer == 'Yes':
                    frequencies = frequencies[:len(e)]
                    clear_frequency_listbox(wnd)
                    clear_result_listbox(wnd)
                    update_frequency_listbox(wnd, frequencies)
                    update_results_listbox(wnd, e)
                    plot_figure(wnd, frequencies, np.array(e))
                    enable_filesave_button(wnd, enable=True)
                else:
                    clear_result_listbox(wnd)
                    clear_figure(wnd)
                    enable_filesave_button(wnd, enable=False)
                msg = "Anulowano obliczenia"
                print(msg)
                set_status(wnd, msg)
            transmitter.close()
            receiver.close()


def load_sfm100a_transmitter_from_config_file(wnd, tr_settings):
    wnd[TR_ATT_VALUE].update(value=int(tr_settings['att']['value']))
    if tr_settings['att']['mode'] == 'auto':
        wnd[TR_ATT_AUTO].update(value=True)
        wnd[TR_ATT_AUTO].update(text_color=ON_COLOR)
        wnd[TR_ATT_MANUAL].update(value=False)
        wnd[TR_ATT_MANUAL].update(text_color=OFF_COLOR)
        wnd[TR_ATT_VALUE].update(disabled=True)
    else:
        wnd[TR_ATT_AUTO].update(value=False)
        wnd[TR_ATT_AUTO].update(text_color=OFF_COLOR)
        wnd[TR_ATT_MANUAL].update(value=True)
        wnd[TR_ATT_MANUAL].update(text_color=ON_COLOR)
        wnd[TR_ATT_VALUE].update(disabled=False)
        wnd[TR_ATT_VALUE].update(value=tr_settings['att']['value'])
    wnd[TR_LEVEL].update(value=int(tr_settings['power']['value']))


def load_esu_receiver_from_config_file(wnd, rec_settings):
    wnd[ESU_ATT_VALUE].update(value=float(rec_settings['att']['value']))
    if rec_settings['att']['mode'] == 'auto':
        wnd[ESU_ATT_AUTO].update(value=True)
        wnd[ESU_ATT_AUTO].update(text_color=ON_COLOR)
        wnd[ESU_ATT_MANUAL].update(value=False)
        wnd[ESU_ATT_MANUAL].update(text_color=OFF_COLOR)
        wnd[ESU_ATT_VALUE].update(disabled=True)
    else:
        wnd[ESU_ATT_AUTO].update(value=False)
        wnd[ESU_ATT_AUTO].update(text_color=OFF_COLOR)
        wnd[ESU_ATT_MANUAL].update(value=True)
        wnd[ESU_ATT_MANUAL].update(text_color=ON_COLOR)
        wnd[ESU_ATT_VALUE].update(disabled=False)
        wnd[ESU_ATT_VALUE].update(value=rec_settings['att']['value'])
    if rec_settings['detector']['type'] == 'aver':
        wnd[ESU_DETECTOR_AVER].update(value=True)
        wnd[ESU_DETECTOR_AVER].update(text_color=ON_COLOR)
        wnd[ESU_DETECTOR_PEAK].update(value=False)
        wnd[ESU_DETECTOR_PEAK].update(text_color=OFF_COLOR)
    else:
        wnd[ESU_DETECTOR_AVER].update(value=False)
        wnd[ESU_DETECTOR_AVER].update(text_color=OFF_COLOR)
        wnd[ESU_DETECTOR_PEAK].update(value=True)
        wnd[ESU_DETECTOR_PEAK].update(text_color=ON_COLOR)
    if rec_settings['coupling']['type'] == 'AC':
        wnd[ESU_COUPLING_AC].update(value=True)
        wnd[ESU_COUPLING_AC].update(text_color=ON_COLOR)
        wnd[ESU_COUPLING_DC].update(value=False)
        wnd[ESU_COUPLING_DC].update(text_color=OFF_COLOR)
    else:
        wnd[ESU_COUPLING_AC].update(value=False)
        wnd[ESU_COUPLING_AC].update(text_color=OFF_COLOR)
        wnd[ESU_COUPLING_DC].update(value=True)
        wnd[ESU_COUPLING_DC].update(text_color=ON_COLOR)
    wnd[ESU_INPUT_PORT].update(value=rec_settings['measure']['input'])
    wnd[ESU_MARKER].update(value=rec_settings['measure']['marker'])
    wnd[ESU_SPAN].update(value=rec_settings['span']['value'])
    wnd[ESU_BAND_VALUE].update(value=rec_settings['rbw']['value'])
    if rec_settings['rbw']['mode'] == 'auto':
        wnd[ESU_BAND_AUTO].update(value=True)
        wnd[ESU_BAND_AUTO].update(text_color=ON_COLOR)
        wnd[ESU_BAND_MANUAL].update(value=False)
        wnd[ESU_BAND_MANUAL].update(text_color=OFF_COLOR)
        wnd[ESU_BAND_VALUE].update(disabled=True)
    else:
        wnd[ESU_BAND_AUTO].update(value=False)
        wnd[ESU_BAND_AUTO].update(text_color=OFF_COLOR)
        wnd[ESU_BAND_MANUAL].update(value=True)
        wnd[ESU_BAND_MANUAL].update(text_color=ON_COLOR)
        wnd[ESU_BAND_VALUE].update(disabled=False)
    wnd[ESU_MEAS_TIME_VALUE].update(value=rec_settings['measure']['time']['value'])
    if rec_settings['measure']['time']['mode'] == 'auto':
        wnd[ESU_MEAS_TIME_AUTO].update(value=True)
        wnd[ESU_MEAS_TIME_AUTO].update(text_color=ON_COLOR)
        wnd[ESU_MEAS_TIME_MANUAL].update(value=False)
        wnd[ESU_MEAS_TIME_MANUAL].update(text_color=OFF_COLOR)
        wnd[ESU_MEAS_TIME_VALUE].update(disabled=True)
    else:
        wnd[ESU_MEAS_TIME_AUTO].update(value=False)
        wnd[ESU_MEAS_TIME_AUTO].update(text_color=OFF_COLOR)
        wnd[ESU_MEAS_TIME_MANUAL].update(value=True)
        wnd[ESU_MEAS_TIME_MANUAL].update(text_color=ON_COLOR)
        wnd[ESU_MEAS_TIME_VALUE].update(disabled=False)


def load_fsv_receiver_from_config_file(wnd, rec_settings):
    att_auto_selected = rec_settings["att"]["mode"] == "auto"
    wnd[FSV_ATT_AUTO].update(value=True if att_auto_selected else False)
    wnd[FSV_ATT_AUTO].update(text_color=ON_COLOR if att_auto_selected else OFF_COLOR)
    wnd[FSV_ATT_MANUAL].update(text_color=OFF_COLOR if att_auto_selected else ON_COLOR)
    wnd[FSV_ATT_VALUE].update(disabled=True if att_auto_selected else False)

    wnd[FSV_COUPLING_AUTO].update(value=True if rec_settings["coupling"]["type"] == "auto" else False)
    wnd[FSV_COUPLING_AUTO].update(text_color=ON_COLOR if rec_settings["coupling"]["type"] == "auto" else OFF_COLOR)
    wnd[FSV_COUPLING_AC].update(value=True if rec_settings["coupling"]["type"] == "AC" else False)
    wnd[FSV_COUPLING_AC].update(text_color=ON_COLOR if rec_settings["coupling"]["type"] == "AC" else OFF_COLOR)
    wnd[FSV_COUPLING_DC].update(value=True if rec_settings["coupling"]["type"] == "DC" else False)
    wnd[FSV_COUPLING_DC].update(text_color=ON_COLOR if rec_settings["coupling"]["type"] == "DC" else OFF_COLOR)

    wnd[FSV_PREAMP_OFF].update(value=True if rec_settings["preamp"]["mode"] == "off" else False)
    wnd[FSV_PREAMP_OFF].update(text_color=ON_COLOR if rec_settings["preamp"]["mode"] == "off" else OFF_COLOR)
    wnd[FSV_PREAMP_15].update(value=True if rec_settings["preamp"]["mode"] == "15" else False)
    wnd[FSV_PREAMP_15].update(text_color=ON_COLOR if rec_settings["preamp"]["mode"] == "15" else OFF_COLOR)
    wnd[FSV_PREAMP_30].update(value=True if rec_settings["preamp"]["mode"] == "30" else False)
    wnd[FSV_PREAMP_30].update(text_color=ON_COLOR if rec_settings["preamp"]["mode"] == "30" else OFF_COLOR)
    """
    wnd[FSV_REF_LEVEL_AUTO].update(value=True if rec_settings["ref-level"]["mode"] == "auto" else False)
    wnd[FSV_REF_LEVEL_AUTO].update(text_color=ON_COLOR if rec_settings["ref-level"]["mode"] == "auto" else OFF_COLOR)
    wnd[FSV_REF_LEVEL_MANUAL].update(text_color=OFF_COLOR if rec_settings["ref-level"]["mode"] == "auto" else ON_COLOR)
    ref_level_value = str(rec_settings['ref-level']['value'])
    if (ref_level_value.find(',')) > -1:
        ref_level_value = ref_level_value.replace(",", ".")
    wnd[FSV_REF_LEVEL_VALUE].update(value=float(ref_level_value))
    wnd[FSV_REF_LEVEL_VALUE].update(disabled=True if rec_settings["ref-level"]["mode"] == "auto" else False)
    """
    wnd[FSV_INPUT_PORT].update(value=rec_settings["input"]["value"])
    wnd[FSV_MARKER].update(value=rec_settings["marker"]["value"])

    bandwidth_value = str(rec_settings["bandwidth"]["value"])
    if bandwidth_value.find(",") > -1:
        bandwidth_value = bandwidth_value.replace(",", ".")
    wnd[FSV_BANDWIDTH_VALUE].update(value=float(bandwidth_value))
    wnd[FSV_BANDWIDTH_UNIT].update(rec_settings["bandwidth"]["unit"])

    measure_time_value = str(rec_settings["mtime"]["value"])
    if measure_time_value.find(",") > -1:
        measure_time_value = measure_time_value.replace(",", ".")
    wnd[FSV_MTIME_VALUE].update(value=float(measure_time_value))
    wnd[FSV_MTIME_UNIT].update(rec_settings["mtime"]["unit"])

    span_value = str(rec_settings["span"]["value"])
    if span_value.find(",") > -1:
        span_value = span_value.replace(",", ".")
    wnd[FSV_SPAN_VALUE].update(value=float(span_value))
    wnd[FSV_SPAN_UNIT].update(rec_settings["span"]["unit"])
    return


def load_measure_from_config_file(wnd, measure_settings):
    wnd[MEAS_REPEAT_COUNT].update(value=measure_settings['count'])
    wnd[MEAS_REPEAT_TRIGGER].update(value=measure_settings['trigger'])
    if bool(measure_settings['state']):
        wnd[MEAS_REPEAT].update(disabled=False)
        wnd[MEAS_REPEAT].update(text_color=ON_COLOR)
        wnd[MEAS_REPEAT_COUNT].update(disabled=False)
        wnd[MEAS_REPEAT_TRIGGER].update(disabled=False)
    else:
        wnd[MEAS_REPEAT].update(disabled=True)
        wnd[MEAS_REPEAT].update(text_color=OFF_COLOR)
        wnd[MEAS_REPEAT_COUNT].update(disabled=True)
        wnd[MEAS_REPEAT_TRIGGER].update(disabled=True)
    return


def load_settings_from_config_file(wnd, values, event):
    # nadajnik
    tr_settings = app_config['config']['transmitters'][tr_selected_index]['settings']
    match tr_selected:
        case "SFM100A":
            load_sfm100a_transmitter_from_config_file(wnd, tr_settings)
    # odbiornik
    rec_settings = app_config['config']['receivers'][rec_selected_index]['settings']
    match rec_selected:
        case "ESU40":
            load_esu_receiver_from_config_file(wnd, rec_settings)
        case "FSV3030":
            load_fsv_receiver_from_config_file(wnd, rec_settings)
    # pomiar
    measure_settings = app_config['measurement']['repeat']
    load_measure_from_config_file(wnd, measure_settings)
    return


def save_fsm100a_transmitter_settings_to_config_file(wnd, values):
    app_config['config']['transmitters'][tr_selected_index]['settings']['power']['value'] = int(values[TR_LEVEL])
    app_config['config']['transmitters'][tr_selected_index]['settings']['att']['mode'] = 'auto' if values[
        TR_ATT_AUTO] else 'manual'
    app_config['config']['transmitters'][tr_selected_index]['settings']['att']['value'] = int(values[TR_ATT_VALUE])
    return


def save_esu_receiver_settings_to_config_file(wnd, values):
    app_config['config']['receivers'][rec_selected_index]['settings']['att']['mode'] = 'auto' if values[
        ESU_ATT_AUTO] else 'manual'
    app_config['config']['receivers'][rec_selected_index]['settings']['att']['value'] = int(values[ESU_ATT_VALUE])
    app_config['config']['receivers'][rec_selected_index]['settings']['coupling']['type'] = \
        'AC' if values[ESU_COUPLING_AC] else 'DC'
    app_config['config']['receivers'][rec_selected_index]['settings']['detector']['type'] = \
        'aver' if values[ESU_DETECTOR_AVER] else 'peak'
    app_config['config']['receivers'][rec_selected_index]['settings']['measure']['input'] = int(values[ESU_INPUT_PORT])
    app_config['config']['receivers'][rec_selected_index]['settings']['measure']['marker'] = int(values[ESU_MARKER])
    app_config['config']['receivers'][rec_selected_index]['settings']['measure']['time']['mode'] = \
        'auto' if values[ESU_MEAS_TIME_AUTO] else 'manual'
    app_config['config']['receivers'][rec_selected_index]['settings']['measure']['time']['value'] = (
        float(str(values[ESU_MEAS_TIME_VALUE]).replace(',', '.')))
    app_config['config']['receivers'][rec_selected_index]['settings']['span']['value'] = (
        float(str(values[ESU_SPAN]).replace(',', '.')))
    app_config['config']['receivers'][rec_selected_index]['settings']['rbw']['mode'] = \
        'auto' if values[ESU_BAND_AUTO] else 'manual'
    app_config['config']['receivers'][rec_selected_index]['settings']['rbw']['value'] = \
        float(str(values[ESU_BAND_VALUE]).replace(',', '.'))
    return


def save_fsv_receiver_settings_to_config_file(wnd, values):
    app_config['config']['receivers'][rec_selected_index]['settings']['att']['mode'] = 'auto' if values[
        FSV_ATT_AUTO] else 'manual'
    app_config['config']['receivers'][rec_selected_index]['settings']['att']['value'] = int(values[FSV_ATT_VALUE])
    app_config['config']['receivers'][rec_selected_index]['settings']['coupling']['type'] = \
        'auto' if values[FSV_COUPLING_AUTO] else ('AC' if values[FSV_COUPLING_AC] else 'DC')
    app_config['config']['receivers'][rec_selected_index]['settings']["preamp"]["mode"] = \
        'off' if values[FSV_PREAMP_OFF] else ('15' if values[FSV_PREAMP_15] else '30')
    """
    app_config['config']["receivers"][rec_selected_index]["settings"]["ref-level"]["mode"] = \
        "auto" if values[FSV_REF_LEVEL_AUTO] else "manual"
    if values[FSV_REF_LEVEL_MANUAL]:
        app_config['config']["receivers"][rec_selected_index]["settings"]["ref-level"]["value"] = \
            float(str(values[FSV_REF_LEVEL_VALUE]).replace(',', '.'))
    """
    app_config['config']["receivers"][rec_selected_index]["settings"]["input"]["value"] = int(values[FSV_INPUT_PORT])
    app_config['config']["receivers"][rec_selected_index]["settings"]["marker"]["value"] = int(values[FSV_MARKER])
    if values[FSV_MTIME_VALUE] != "":
        app_config['config']["receivers"][rec_selected_index]["settings"]["mtime"]["value"] = \
            float(values[FSV_MTIME_VALUE].replace(",", "."))
        app_config['config']["receivers"][rec_selected_index]["settings"]["mtime"]["unit"] = str(values[FSV_MTIME_UNIT])
    if values[FSV_BANDWIDTH_VALUE] != "":
        app_config['config']["receivers"][rec_selected_index]["settings"]["bandwidth"]["value"] = \
            float(values[FSV_BANDWIDTH_VALUE].replace(",", "."))
        app_config['config']["receivers"][rec_selected_index]["settings"]["bandwidth"]["unit"] = str(
            values[FSV_BANDWIDTH_UNIT])
    if values[FSV_SPAN_VALUE] != "":
        app_config['config']["receivers"][rec_selected_index]["settings"]["span"]["value"] = \
            float(values[FSV_SPAN_VALUE].replace(",", "."))
        app_config['config']["receivers"][rec_selected_index]["settings"]["span"]["unit"] = str(
            values[FSV_SPAN_UNIT])
    return


def save_measure_settings_to_config_file(wnd, values):
    state = 'true' if values[MEAS_REPEAT] else 'false'
    app_config['measurement']['repeat']['state'] = state
    app_config['measurement']['repeat']['count'] = int(values[MEAS_REPEAT_COUNT])
    app_config['measurement']['repeat']['trigger'] = (
        float(str(values[MEAS_REPEAT_TRIGGER]).replace(',', '.')))
    return


def save_settings_to_config_file(wnd, values, event):
    # nadajnik
    match tr_selected:
        case "SFM100A":
            save_fsm100a_transmitter_settings_to_config_file(wnd, values)
    # odbiornik
    match rec_selected:
        case "ESU40":
            save_esu_receiver_settings_to_config_file(wnd, values)
        case "FSV3030":
            save_fsv_receiver_settings_to_config_file(wnd, values)
    # pomiar
    save_measure_settings_to_config_file(wnd, values)
    # save to config file
    with open(yaml_file, 'w') as cfg_file:
        yaml.dump(app_config, cfg_file)
    return


def save_last_selected_receiver(wnd):
    rec_stored = app_config["init"]["selected-receiver"]
    print(f"Selected receiver, stored in config file is '{rec_stored}'")
    print(f"Selected receiver on the end of program is '{rec_selected}'")
    if rec_stored != rec_selected:
        print("Saving last selected receiver to the config file")
        app_config["init"]["selected-receiver"] = rec_selected
        with open(yaml_file, 'w') as cfg_file:
            yaml.dump(app_config, cfg_file)
    return


def get_recs_combo_selected_text(wnd):
    return wnd[RECS_COMBO].Values[rec_selected_index]


def set_recs_combo_text(wnd, text):
    wnd[RECS_COMBO].update(value=text)


def set_recs_combo_index(wnd, idx):
    wnd[RECS_COMBO].update(set_to_index=idx)


def schedule_save_results_event(wnd, values, event):
    results_file = values[SAVEFILENAME]
    if wnd[PREFIX_CHK].get():
        file_directory, file_name = os.path.split(results_file)
        prefix = generate_result_filename_prefix()
        results_file = file_directory + "/" + prefix + file_name
    msg = f"Zapis wyników do pliku '{results_file}'"
    print(msg)
    set_status(wnd, msg)
    frequencies = [str(s).replace('.', ',') for s in wnd[FREQ_LB].Values if s]
    voltages = [str(s).replace('.', ',') for s in wnd[RESULTS_LB].Values if s]
    separator = ';' if values[DATA_SEPARATOR][0] == ';' else '\t'
    if len(frequencies) == len(voltages):
        lines = []
        f = open(results_file, "wt")
        if values[DATA_HEADER]:
            lines.append('Częstotliwość, MHz{0}Poziom napięcia [dBuV]\n'.format(separator))
        for n in range(0, len(frequencies)):
            lines.append('{0}{1}{2}\n'.format(frequencies[n], separator, voltages[n]))
        f.writelines(lines)
        f.close()
    return


def schedule_event_frequency_listbox(wnd, values):
    indices = wnd[FREQ_LB].get_indexes()
    if ((len(wnd[FREQ_LB].Values) == len(wnd[RESULTS_LB].Values)) and
            ((len(wnd[RESULTS_LB].get_indexes()) == 0) or (wnd[RESULTS_LB].get_indexes()[0] != indices[0]))):
        wnd[RESULTS_LB].update(set_to_index=indices[0], scroll_to_index=indices[0])
    return


def schedule_event_results_listbox(wnd, values):
    indices = wnd[RESULTS_LB].get_indexes()
    if (len(wnd[RESULTS_LB].Values) == len(wnd[FREQ_LB].Values)) and (
            (len(wnd[FREQ_LB].get_indexes()) == 0) or (wnd[FREQ_LB].get_indexes()[0] != indices[0])):
        wnd[FREQ_LB].update(set_to_index=indices[0], scroll_to_index=indices[0])
    return


def schedule_recs_combo(wnd, values, event):
    idx = recs_list.index(values[event])
    print(f"Combo: selected receiver is '{values[event]}' (at index {idx})")
    print(f"Selecting Tab of TabControl at index {idx} ...")
    wnd[recs_list[idx]].select()
    return


def schedule_recs_tab(wnd, values, event):
    global rec_selected
    global rec_selected_index
    global rec_tab_first_entry
    global receiver_ip
    print(f"Tab: selected tab is '{values[event]}'")
    if rec_tab_first_entry is True:
        rec_tab_first_entry = False
        wnd[rec_selected].select()
        return
    if wnd[RECS_COMBO].get() != values[event]:
        print(f"Selecting '{values[event]}' at receiver Combo ...")
        wnd[RECS_COMBO].update(values[event])
        rec_selected = values[event]
        rec_selected_index = recs_list.index(values[event])
        receiver_ip = app_config['config']['receivers'][rec_selected_index]['ip']
    return


handlers = {
    TR_ATT_AUTO: schedule_sfm_transmitter_attenuator_auto_event,
    TR_ATT_MANUAL: schedule_sfm_transmitter_attenuator_manual_event,

    ESU_ATT_AUTO: schedule_esu_receiver_attenuator_auto_event,
    ESU_ATT_MANUAL: schedule_esu_receiver_attenuator_manual_event,
    ESU_DETECTOR_AVER: schedule_esu_receiver_average_detector_event,
    ESU_DETECTOR_PEAK: schedule_esu_receiver_peak_detector_event,
    ESU_COUPLING_AC: schedule_esu_receiver_coupling_ac_event,
    ESU_COUPLING_DC: schedule_esu_receiver_coupling_dc_event,
    ESU_MEAS_TIME_AUTO: schedule_esu_receiver_measure_time_auto_event,
    ESU_MEAS_TIME_MANUAL: schedule_esu_receiver_measure_time_manual_event,
    ESU_BAND_AUTO: schedule_esu_receiver_bandwidth_auto_event,
    ESU_BAND_MANUAL: schedule_esu_receiver_bandwidth_manual_event,

    FSV_ATT_AUTO: schedule_fsv_receiver_attenuator_auto_event,
    FSV_ATT_MANUAL: schedule_fsv_receiver_attenuator_manual_event,
    FSV_COUPLING_AC: schedule_fsv_receiver_coupling_ac_event,
    FSV_COUPLING_DC: schedule_fsv_receiver_coupling_dc_event,
    FSV_COUPLING_AUTO: schedule_fsv_receiver_coupling_auto_event,
    FSV_PREAMP_OFF: schedule_fsv_receiver_preamp_off_event,
    FSV_PREAMP_15: schedule_fsv_receiver_preamp_15_event,
    FSV_PREAMP_30: schedule_fsv_receiver_preamp_30_event,
    FSV_REF_LEVEL_AUTO: schedule_fsv_receiver_ref_level_auto_event,
    FSV_REF_LEVEL_MANUAL: schedule_fsv_receiver_ref_level_manual_event,

    MEAS_REPEAT: schedule_event_repeat_measure_trigger,
    FREQFILENAME: schedule_browse_frequency_file_event,

    CONFIG_READ: load_settings_from_config_file,
    CONFIG_SAVE: save_settings_to_config_file,

    DATA_HEADER: schedule_event_data_header,

    DO_MEASURE: schedule_measurement_event,

    PREFIX_CHK: schedule_event_filename_prefix,
    SAVEFILENAME: schedule_save_results_event,
    FREQ_LB: schedule_event_frequency_listbox,
    RESULTS_LB: schedule_event_results_listbox,

    RECS_COMBO: schedule_recs_combo,
    RECS_GROUP: schedule_recs_tab,
}


#
# funkcje obslugi zdarzeń z GUI
#
def schedule_event(event, values, wnd):
    msg = 'Processing event {0} ...'.format(event)
    print(msg)
    set_status(wnd, msg)
    return handlers[event](wnd, values, event)


# Funkcje rysowania/czyszczenia wykresu
#
def plot_figure(wnd, x, y):
    # fmt = '.-g'
    plot_config = app_config['plot']
    plot_marker: str = plot_config['format']['marker']
    plot_line_style: str = plot_config['format']['line-style']
    plot_color: str = plot_config['format']['color'][0]
    fmt = plot_marker + plot_line_style + plot_color
    ax.plot(x[:len(y)], y, fmt)
    ax.set_xlim([x[0], x[len(x) - 1]])
    ax.set_xlabel('Częstotliwość, MHz')
    ax.set_ylabel('Napięcie, dBuV')

    canvas = wnd['-CANVAS-'].TKCanvas

    if canvas.children:
        for child in canvas.winfo_children():
            child.destroy()

    figure_canvas_agg = FigureCanvasTkAgg(fig, master=canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='right', fill='both', expand=1)
    return


def clear_figure(wnd):
    ax.cla()

    canvas = wnd['-CANVAS-'].TKCanvas

    if canvas.children:
        for child in canvas.winfo_children():
            child.destroy()

    figure_canvas_agg = FigureCanvasTkAgg(fig, master=canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(fill='both', expand=1, side='top')
    return


# Funkcje aktualizacji kontrolek

def update_results_listbox(wnd, contents):
    wnd[RESULTS_LB].update(contents)
    return


def enable_filesave_button(wnd, enable):
    wnd[FILESAVE_BTN].update(disabled=False if enable else False)
    return


def set_status(wnd, msg):
    wnd[STATMSG].update(msg)
    return


def generate_result_filename_prefix() -> str:
    """
    Funkcja generowania prefiksu nazwy pliku wynikowego
    :return: Wynikiem jest wyrażenie łąńcuchowe postaci RRRRMMDD_HHmmss_, gdzie:
    RRRRR to rok (liczba czterocyfrowa) MM to miesiąc, DD to dzień miesiąca,
    HH to godzina (wartość 24-godzinna), mm - minuty a ss to sekundy
    """
    teraz = dt.datetime.now()
    RRRR = "%04d" % teraz.year
    MM = "%02d" % teraz.month
    DD = "%02d" % teraz.day
    HH = "%02d" % teraz.hour
    mm = "%02d" % teraz.minute
    ss = "%02d" % teraz.second
    prefix = RRRR + MM + DD + "_" + HH + mm + ss + "_"
    return prefix


def blank_frame(title="", size=(200, 200), frame_layout=None, key=None, tooltip=None):
    if frame_layout is None:
        frame_layout = [[]]
    if tooltip is None:
        tooltip = ""
    return sg.Frame(title, layout=frame_layout, size=size, key=key, tooltip=tooltip, expand_x=True, expand_y=True)


def main():
    # user = None
    # print('Hi!') if user is None else print(f'Hi, {user}.')

    """
    Kontrolki SMF100A
    """
    smf_att_layout = [
        [
            sg.Radio('auto', key=TR_ATT_AUTO, default=True, enable_events=True, group_id='tratt', text_color=ON_COLOR)
        ],
        [
            sg.Radio('manual', key=TR_ATT_MANUAL, default=False, enable_events=True, group_id='tratt',
                     text_color=OFF_COLOR),
            sg.Combo(values=list(range(0, 120, 10)), disabled=True, key=TR_ATT_VALUE, default_value=0, size=(6, 1),
                     tooltip='Tłumienie sygnału na wyjściu nadajnika\n'
                             'Wartość z zakresu od 0 do 110 dB\n'
                             'z rozdzielczością 10 dB'
                     ),
            sg.Text(' dB', text_color=OFF_COLOR)
        ]
    ]

    smf_level_layout = [
        sg.Text(text='Poziom napiecia', text_color=OFF_COLOR),
        sg.Input(default_text='77', size=(6, 1), key=TR_LEVEL, text_color=OFF_COLOR, justification='right'),
        sg.Text(text=' dBuV', text_color=OFF_COLOR)
    ]

    smf_transmitter_layout = [
        [
            sg.Frame(title='Tłumik', layout=smf_att_layout)
        ],
        [
            sg.Frame(title='Poziom napięcia', layout=[smf_level_layout],
                     tooltip='Wartość poziomu sygnału\nna wyjściu nadajnika\nwyrażona w dBuV')
        ]
    ]

    """
    Kontrolki ESU40
    """
    esu_att_layout = [
        [sg.Radio('auto', key=ESU_ATT_AUTO, default=True, enable_events=True, group_id='recatt',
                  text_color=ON_COLOR)],
        [sg.Radio('manual', key=ESU_ATT_MANUAL, default=False, enable_events=True, group_id='recatt',
                  text_color=OFF_COLOR),
         sg.Combo(values=list(range(0, 80, 5)), disabled=True, key=ESU_ATT_VALUE, default_value=0, size=(6, 1),
                  tooltip='Tłumienie sygnału na wyjściu odbiornika\n'
                          'Wartość z zakresu od 0 do 75 dB\n'
                          'z rozdzielczością 5 dB'
                  ),
         sg.Text(' dB', text_color=OFF_COLOR)]
    ]

    esu_detector_layout = [
        [sg.Radio("wartość szczytowa", key=ESU_DETECTOR_PEAK, default=False, group_id="det", text_color=OFF_COLOR,
                  enable_events=True)],
        [sg.Radio("wartość średnia", key=ESU_DETECTOR_AVER, default=True, group_id="det", text_color=ON_COLOR,
                  enable_events=True)]
    ]

    esu_span_layout = [
        sg.Text(text='Span', text_color=OFF_COLOR),
        sg.InputText(key=ESU_SPAN, size=(8, 1), text_color=OFF_COLOR, default_text='30', justification='right',
                     tooltip='Wartość z zakresu od 1 kHz do 1 MHz w kHz'),
        sg.Text(text=' kHz', text_color=OFF_COLOR)
    ]

    esu_coupling_layout = [
        [
            sg.Radio("AC", group_id='coupling', enable_events=True, key=ESU_COUPLING_AC, default=True,
                     text_color=ON_COLOR)
        ],
        [
            sg.Radio("DC", group_id='coupling', enable_events=True, key=ESU_COUPLING_DC, default=False,
                     text_color=OFF_COLOR)
        ]
    ]

    esu_measurement_time_layout = [
        # [
        sg.Radio('auto', key=ESU_MEAS_TIME_AUTO, default=True, enable_events=True, group_id='mtime',
                 text_color=ON_COLOR),
        # ],
        # [
        sg.Radio('manual', key=ESU_MEAS_TIME_MANUAL, enable_events=True, default=False, group_id='mtime',
                 text_color=OFF_COLOR),
        sg.Input(default_text='', size=(5, 1), key=ESU_MEAS_TIME_VALUE, justification='right', disabled=True),
        sg.Text(' ms', text_color=OFF_COLOR)
        # ]
    ]

    esu_bandwidth_layout = [
        # [
        sg.Radio('auto', key=ESU_BAND_AUTO, default=True, enable_events=True, group_id='rbw', text_color=ON_COLOR),
        # ],
        # [
        sg.Radio('manual', key=ESU_BAND_MANUAL, default=False, enable_events=True, group_id='rbw',
                 text_color=OFF_COLOR),
        sg.Input(default_text='9', size=(6, 1), key=ESU_BAND_VALUE, justification='right', disabled=True),
        sg.Text(' kHz', text_color=OFF_COLOR)
        # ]
    ]

    esu_input_marker_layout = [
        [
            sg.Text("Wejście RF:", text_color=OFF_COLOR),
            # sg.Input(default_text="1", size=(4, 1), key=REC_INPUT_PORT, justification='right', text_color=OFF_COLOR)
            sg.Combo(values=list(range(1, 3, 1)), disabled=False, key=ESU_INPUT_PORT, default_value=1, size=(4, 1)),
        ],
        [
            sg.Text(text='Marker #     ', text_color=OFF_COLOR),
            # sg.InputText(key=REC_MARKER, size=(8, 1), text_color=OFF_COLOR, default_text='1', justification='right',
            # tooltip='Wartość z zakresu 1..4')
            sg.Combo(values=list(range(1, 5, 1)), disabled=False, key=ESU_MARKER, default_value=1, size=(4, 1)),
        ]
    ]
    esu_receiver_layout = [
        [
            sg.Frame(title="Tłumik", layout=esu_att_layout,
                     tooltip='Tłumienie sygnału na wejściu odbiornika\n'
                             'Wartość z zakresu od 0 do 75 dB\n'
                             'z rozdzielczoscią 5 dB'),
            sg.Frame(title="Detektor", layout=esu_detector_layout),
            sg.Frame(title="Coupling", layout=esu_coupling_layout, tooltip='Sprzężenie'),
            sg.Frame(title='Wejście RF', layout=esu_input_marker_layout)
        ],
        [
            sg.Frame(title="Span", layout=[esu_span_layout],
                     tooltip='Szerokość pasma\nwyświetlana na\nekranie analizatora'),
            sg.Frame(title='Czas pomiaru', layout=[esu_measurement_time_layout]),
            sg.Frame(title='Szerokość pasma', layout=[esu_bandwidth_layout])
        ]
    ]

    """
    Kontrolki pomiaru
    """
    measure_layout = [
        [
            sg.Checkbox('Powtórz', default=False, enable_events=True, text_color=ON_COLOR,
                        key=MEAS_REPEAT),
            sg.Input(key=MEAS_REPEAT_COUNT, size=(2, 1), justification='right', text_color=OFF_COLOR, default_text='3',
                     tooltip='Krotność powtarzania pomiaru', disabled=True),
            sg.Text('razy dla różnicy wartości powyżej ', text_color=OFF_COLOR),
            sg.Input(key=MEAS_REPEAT_TRIGGER, size=(4, 1), disabled=True, default_text='20', justification='right',
                     tooltip=' Pomiar powtarzany jest, jeżeli \n'
                             ' różnica pomiędzy kolejnymi pomiarami \n'
                             ' jest większa niż podana wartość '),
            sg.Text(' dB', text_color=OFF_COLOR),
            sg.Button('Wykonaj pomiar', key=DO_MEASURE)
        ]
    ]

    """
    Kontrolki opcji pomiaru
    """
    frequency_layout = [
        sg.Text("Plik częstotliwości"),
        sg.InputText(size=(45, 1), enable_events=True, key=FREQFILENAME),
        sg.FileBrowse('Otwórz plik', target=FREQFILENAME,
                      file_types=(('Pliki tekstowe', '*.txt'),)
                      )
    ]

    """
    Kontrolki danych
    """
    data_layout = [
        sg.Listbox(size=(20, 15), values=[], expand_y=True, key=FREQ_LB, enable_events=True,
                   select_mode=sg.LISTBOX_SELECT_MODE_SINGLE,
                   tooltip="Czestotliwości dla których wykonywane są pomiary, w MHz")
    ]

    """
    Kontrolki wykresu
    """
    graph_layout = [
        sg.Canvas(key='-CANVAS-',
                  # it's important that you set this size
                  size=(FIGURE_WIDTH, FIGURE_HEIGHT),
                  background_color='#DAE0E6'
                  ),
    ]

    """
    Kontrolki wyników
    """
    results_layout = [
        sg.Listbox(size=(20, 15), values=[], expand_y=True, key=RESULTS_LB, enable_events=True,
                   select_mode=sg.LISTBOX_SELECT_MODE_SINGLE)
    ]

    """
    Kontrolki zapisu wyników
    """
    save_layout = [
        sg.Checkbox('Dodaj prefiks', text_color=ON_COLOR,
                    tooltip="'Prefiks stanowi sygnaturę czasową\n " +
                            "w postaci RRRRMMDD_hhmmss_\ngdzie:\n" +
                            "RRRR - rok\n  MM - miesiąc\n  DD - dzień\n" +
                            "  hh - godzina\n  mm - minuty\n  ss - sekundy",
                    key=PREFIX_CHK, default=True, enable_events=True
                    ),
        sg.InputText(visible=False, enable_events=True, key=SAVEFILENAME),
        sg.FileSaveAs('Zapisz wyniki pomiaru',
                      key=FILESAVE_BTN,
                      default_extension="csv",
                      file_types=(('Plik CSV', '*.csv'), ('Plik tekstowy', '*.txt'),),
                      target=SAVEFILENAME,
                      disabled=True
                      ),
        sg.Text('Separator danych', text_color=OFF_COLOR),
        sg.Combo(values=['; (średnik)', 'tabulator'], size=(12, 1), default_value='; (średnik)', enable_events=True,
                 key=DATA_SEPARATOR),
        sg.Checkbox(text='Wstaw nagłówek', key=DATA_HEADER, default=True, enable_events=True, text_color=ON_COLOR)
    ]

    """
    Kontrolki odczytu/zapisu konfiguracji
    """
    config_layout = [
        sg.Button(button_text='Odczytaj', enable_events=True, key=CONFIG_READ,
                  tooltip='Odczyt ustawień nadajnika i odbiornika\nz pliku konfiguracyjnego aplikacji'),
        sg.Button(button_text='Zapisz', enable_events=True, key=CONFIG_SAVE,
                  tooltip='Zapis ustawień nadajnika i odbiornika\ndo pliku konfiguracyjnego aplikacji')
    ]

    """
    Kontrolki statusu
    """
    status_layout = [
        sg.Text(text_color=OFF_COLOR, background_color=ON_COLOR, text='', size=(120, 1), key=STATMSG)
    ]

    """
    Kontrolki FSV3030
    """
    fsv_att_layout = sg.Frame("Tłumik", [
        [
            sg.Radio("automatyczny", key=FSV_ATT_AUTO, group_id="rec2_att", default=True, text_color=ON_COLOR,
                     enable_events=True)
        ],
        [
            sg.Radio("ręczny", key=FSV_ATT_MANUAL, group_id="rec2_att", text_color=OFF_COLOR, enable_events=True),
            sg.Combo(values=list(range(0, 80, 5)), disabled=True, key=FSV_ATT_VALUE, default_value=0, size=(6, 1),
                     tooltip='Tłumienie sygnału na wyjściu odbiornika.\nWartość z zakresu od 0 do 75 dB\n'
                             'z rozdzielczością 5 dB'),
            sg.Text(' dB', text_color=OFF_COLOR)
        ]
    ]
                              )

    fsv_coupling_layout = sg.Frame("Sprzężenie", [
        [
            sg.Radio("AC", group_id='fsv_coupling', enable_events=True, key=FSV_COUPLING_AC, default=False,
                     text_color=OFF_COLOR, tooltip="Sprzężenie AC stosowane jest dla zakresu \n" +
                                                   "częstotliwości od 10 MHz do 30 GHz "),
            sg.Radio("DC", group_id='fsv_coupling', enable_events=True, key=FSV_COUPLING_DC, default=False,
                     text_color=OFF_COLOR, tooltip="Sprzężenie DC stosowane jest w całym \n" +
                                                   "zakresie częstotliwości (od 10 Hz do 30 GHz) ")
        ],
        [
            sg.Radio("automatyczne", group_id='fsv_coupling', enable_events=True, key=FSV_COUPLING_AUTO, default=True,
                     text_color=ON_COLOR, tooltip="Dla częstotliwości do 10 MHz \n" +
                                                  "stosowane jest sprzężenie DC \n" +
                                                  "powyżej - sprzężenie AC. ")
        ]]
                                   )

    fsv_preamp_layout = sg.Frame("Przedwzmacniacz", [
        [
            sg.Radio("wyłączony", group_id='fsu_preamp', enable_events=True, key=FSV_PREAMP_OFF, default=True,
                     text_color=ON_COLOR)
        ],
        [
            sg.Radio("15 dB", group_id='fsu_preamp', enable_events=True, key=FSV_PREAMP_15, default=False,
                     text_color=OFF_COLOR),
            sg.Radio("30 dB", group_id='fsu_preamp', enable_events=True, key=FSV_PREAMP_30, default=False,
                     text_color=OFF_COLOR)
        ]]
                                 )

    fsv_ref_level_layout = sg.Frame("Poziom odniesienia", [
        [
            sg.Radio("automatyczny", key=FSV_REF_LEVEL_AUTO, group_id="ref_level", default=True, text_color=ON_COLOR,
                     enable_events=True)
        ],
        [
            sg.Radio("ręczny", key=FSV_REF_LEVEL_MANUAL, group_id="ref_level", text_color=OFF_COLOR,
                     enable_events=True),
            sg.Input(disabled=True, key=FSV_REF_LEVEL_VALUE, size=(7, 1), text_color=OFF_COLOR, justification='right'),
            sg.Text(' dBμV', text_color=OFF_COLOR)
        ]
    ])

    fsv_input_marker_layout = sg.Frame("Wejście/Marker", [
        [
            sg.Text("Wejście ", text_color=OFF_COLOR),
            sg.Combo(values=list(range(1, 3, 1)), disabled=False, key=FSV_INPUT_PORT, default_value=1),
        ],
        [
            sg.Text(text="Marker #", text_color=OFF_COLOR),
            sg.Combo(values=list(range(1, 5, 1)), disabled=False, key=FSV_MARKER, default_value=1),
        ]
    ]
                                       )

    fsv_bandwidth_layout = sg.Frame("Szerokość pasma", [
        [
            sg.Text(text="Wartość: ", text_color=OFF_COLOR),
            sg.Input(key=FSV_BANDWIDTH_VALUE, size=(6, 1), text_color=OFF_COLOR,
                     justification='right', default_text="10"),
            sg.Text(text=" ", text_color=OFF_COLOR),
            sg.Combo(key=FSV_BANDWIDTH_UNIT, values=["kHz", "MHz", "GHz"], disabled=False,
                     default_value="kHz")
        ]
    ]
                                    )

    fsv_mtime_layout = sg.Frame("Czas pomiaru", [
        [
            sg.Text(text="Wartość: ", text_color=OFF_COLOR),
            sg.Input(key=FSV_MTIME_VALUE, size=(6, 1), text_color=OFF_COLOR,
                     justification='right', default_text="50"),
            sg.Text(text=" ", text_color=OFF_COLOR),
            sg.Combo(key=FSV_MTIME_UNIT, values=["ms", "s"], disabled=False, default_value="ms")
        ]
    ]
                                )

    fsv_span_layout = sg.Frame("Span", [
        [
            sg.Text(text="Wartość: ", text_color=OFF_COLOR),
            sg.Input(key=FSV_SPAN_VALUE, size=(6, 1), text_color=OFF_COLOR,
                     justification='right', default_text="100"),
            sg.Text(text=" ", text_color=OFF_COLOR),
            sg.Combo(key=FSV_SPAN_UNIT, values=["Hz", "kHz", "MHz"], disabled=False,
                     default_value="kHz")
        ]
    ]
                               )

    fsv_receiver_layout = [
        [fsv_att_layout, fsv_coupling_layout, fsv_preamp_layout, fsv_input_marker_layout],  #, fsv_ref_level_layout],
        [fsv_bandwidth_layout, fsv_mtime_layout, fsv_span_layout]
    ]
    esu_tab = sg.Tab(title=recs_list[0], key=recs_list[0], layout=esu_receiver_layout)
    fsv_tab = sg.Tab(title=recs_list[1], key=recs_list[1], layout=fsv_receiver_layout)

    recs_cb = sg.Combo(values=recs_list, enable_events=True, key=RECS_COMBO, default_value=rec_selected)
    recs_tg = sg.TabGroup([[esu_tab, fsv_tab]], key=RECS_GROUP, enable_events=True, size=(800, 400))

    smf_tab = sg.Tab(title=trs_list[0], key=trs_list[0], layout=smf_transmitter_layout)
    trs_cb = sg.Combo(values=[trs_list[0]], enable_events=True, key=TRS_COMBO, default_value=tr_selected)
    trs_tg = sg.TabGroup([[smf_tab]], key=TRS_GROUP, enable_events=True, size=(300, 400))

    layout = [
        [
            blank_frame("Nadajnik", key="FRAME_TRANSMITTER", frame_layout=[[trs_cb], [trs_tg]]),
            blank_frame("Odbiornik", size=(600,256), key="FRAME_RECEIVER", frame_layout=[[recs_cb], [recs_tg]])
        ],
        [
            blank_frame("Częstotliwość", size=(550, 60), frame_layout=[frequency_layout]),
            blank_frame("Pomiar", size=(550, 60), frame_layout=measure_layout)
        ],
        [
            blank_frame("Dane", size=(200, 340), frame_layout=[data_layout]),
            blank_frame("Wykres", size=(600, 340), frame_layout=[graph_layout]),
            blank_frame("Wyniki", size=(200, 340), frame_layout=[results_layout])
        ],
        [
            blank_frame("Zapis wyników", size=(200, 60), frame_layout=[save_layout]),
            blank_frame("Konfiguracja", size=(40, 60), frame_layout=[config_layout])
        ],
        [
            blank_frame("Status", size=(600, 60), frame_layout=[status_layout])
        ]
    ]

    events = list(handlers.keys())
    window = sg.Window("Pomiar zakłóceń", layout, disable_minimize=not True, no_titlebar=False)
    # Run the event Loop
    while True:
        event, values = window.read()
        print(event, values)
        if event in ('Exit', sg.WIN_CLOSED):
            save_last_selected_receiver(window)
            break
        if event in events:
            schedule_event(event, values, window)

    window.close()


def func():
    print('Lokalizacja pliku : {0}'.format(__file__))
    print('Folder pliku : {0}'.format(os.path.dirname(__file__)))
    print('Folder, plik : {0}'.format(os.path.split(__file__)))

    low_limit = 1
    upper_limit = 1000
    for value in [750, 0.5, 1200]:
        print('Ograniczenie wartości {0} do zakresu [{1},{2}]: {3}'.
              format(value, low_limit, upper_limit, limit_value(value, [low_limit, upper_limit])))
    main()


def limit_value(x, limits):
    return limits[0] if x < limits[0] else (limits[1] if x > limits[1] else x)


# func()
main()
