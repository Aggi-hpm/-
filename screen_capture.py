import mss
import numpy as np
from PIL import Image


class ScreenCapture:
    def __init__(self):
        self.sct = mss.mss()

    def capture_region(self, x, y, w, h):
        monitor = {"left": int(x), "top": int(y), "width": int(w), "height": int(h)}
        img = self.sct.grab(monitor)
        return Image.frombytes("RGB", img.size, img.bgra, "raw", "BGRX")

    def capture_full(self):
        monitor = self.sct.monitors[0]
        img = self.sct.grab(monitor)
        return Image.frombytes("RGB", img.size, img.bgra, "raw", "BGRX")
