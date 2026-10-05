import ctypes
import time
import random

user32 = ctypes.windll.user32

MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010


def set_cursor_pos(x, y):
    user32.SetCursorPos(int(x), int(y))


def mouse_down(button='left'):
    if button == 'left':
        user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    else:
        user32.mouse_event(MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)


def mouse_up(button='left'):
    if button == 'left':
        user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    else:
        user32.mouse_event(MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)


def click_at(x, y, dwell_min=20, dwell_max=50, random_offset=5):
    offset_x = random.randint(-random_offset, random_offset)
    offset_y = random.randint(-random_offset, random_offset)
    tx = int(x) + offset_x
    ty = int(y) + offset_y
    set_cursor_pos(tx, ty)
    time.sleep(random.uniform(dwell_min, dwell_max) / 1000.0)
    mouse_down('left')
    time.sleep(random.uniform(dwell_min, dwell_max) / 1000.0)
    mouse_up('left')


def get_cursor_pos():
    class POINT(ctypes.Structure):
        _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]
    pt = POINT()
    user32.GetCursorPos(ctypes.byref(pt))
    return pt.x, pt.y
