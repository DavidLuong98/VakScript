# built-in
from ctypes import windll
from collections import namedtuple
from gc import collect as del_mem
from time import sleep
from datetime import datetime
import time

# ext
from pyMeow import open_process, get_module
from pyMeow import r_int, r_float, r_uint64
from win32api import GetSystemMetrics, GetCursorPos, GetAsyncKeyState

# own
from data import Offsets, Info, VK_CODES
from world_to_screen import World
from utils import send_key, debug_info
from entities import AttributesReader

"""
TODO:
    - Fix Username API Request or read in memory instead.

"""


class Asmite:

    def __init__(self, settings):
        self.settings = settings

        self.obj_health = Offsets.obj_health
        self.obj_spawn_count = Offsets.obj_spawn_count
        self.obj_x = Offsets.obj_x
        self.obj_y = Offsets.obj_y
        self.obj_z = Offsets.obj_z

    def get_settings(self):
        return VK_CODES[self.settings['smite']]

    def _read_attr(self, process, address, nt):
        attributes = nt(
            health=r_float(process, address + self.obj_health),
            alive=r_int(process, address + self.obj_spawn_count) % 2 == 0,
            x=r_float(process, address + self.obj_x),
            y=r_float(process, address + self.obj_y),
            z=r_float(process, address + self.obj_z)
        )

        return attributes


# Workaround : Not actually autosmite, rather twisted fate card picker. Reason : adding an external script under
# scripts folder caused a hardware limitation issue. For some reason, autosmite never raised that exception.
def autosmite(terminate, settings, jungle_pointers, on_window):
    w_key = VK_CODES['w']
    e_key = VK_CODES['e']
    t_key = VK_CODES['t']
    three_key = VK_CODES['3']
    key_card = {e_key: 'goldcardlock', t_key: "redcardlock", three_key: 'bluecardlock'}
    MAX_LOOP_DURATION = 6

    while not terminate.value:
        if on_window.value:
            del_mem()

            user_selected_card_name = "";
            if GetAsyncKeyState(three_key):
                send_key(w_key)
                user_selected_card_name = key_card[three_key]
            elif GetAsyncKeyState(e_key):
                send_key(w_key)
                user_selected_card_name = key_card[e_key]
            elif GetAsyncKeyState(t_key):
                send_key(w_key)
                user_selected_card_name = key_card[t_key]

            if user_selected_card_name != "":
                start_time = time.time()
                while True:
                    try:
                        process = open_process(process=Info.game_name_executable)
                        base_address = get_module(process, Info.game_name_executable)['base']
                        local_player = r_uint64(process, base_address + Offsets.local_player)
                        attr_reader = AttributesReader(process, base_address)

                        card_name = attr_reader.read_spells(local_player)[1]['name'].lower()
                        if card_name == user_selected_card_name:
                            send_key(w_key)
                            break
                        else :
                            elapsed_time = time.time() - start_time
                            if elapsed_time > MAX_LOOP_DURATION :
                                break;
                            else:
                                time.sleep(0.1)

                    except Exception as e:
                        print("Error in selectCard:", e)

            if user_selected_card_name != "":
                user_selected_card_name = ""

