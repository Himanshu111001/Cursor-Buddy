"""
Media and Video Playback Detector for Windows.
Prevents the desktop companion from awakening or dismisses it automatically
when the user is watching videos, listening to media, or playing fullscreen games.
"""

import ctypes
from ctypes import HRESULT, POINTER, Structure, byref, c_float, c_void_p, wintypes
import time
import win32api
import win32con
import win32gui


class GUID(Structure):
    _fields_ = [
        ("Data1", ctypes.c_uint32),
        ("Data2", ctypes.c_uint16),
        ("Data3", ctypes.c_uint16),
        ("Data4", ctypes.c_uint8 * 8),
    ]


ole32 = ctypes.oledll.ole32


def _parse_guid(guid_str: str) -> GUID:
    g = GUID()
    ole32.IIDFromString(ctypes.c_wchar_p(guid_str), byref(g))
    return g


CLSID_MMDeviceEnumerator = _parse_guid("{BCDE0395-E52F-467C-8E3D-C4579291692E}")
IID_IMMDeviceEnumerator = _parse_guid("{A95664D2-9614-4F35-A746-DE8DB63617E6}")
IID_IAudioMeterInformation = _parse_guid("{C02216F6-8C67-4B5B-9D00-D008E73E0064}")


class MediaDetector:
    PEAK_THRESHOLD = 0.005  # Lower threshold to filter out digital silence/ground noise
    HOLD_TIME = 6.0         # Seconds to bridge dialogues, pauses, and quiet scenes
    CACHE_DURATION = 0.3    # Throttle checks to 3-4 times per second

    def __init__(self):
        try:
            ole32.CoInitialize(None)
        except Exception:
            pass
        self._meter = None
        self._get_peak_func = None
        self._last_audio_activity = 0.0
        self._ignore_audio_until = 0.0
        self._last_check_time = 0.0
        self._cached_audio = False
        self._cached_fullscreen = False

    def notify_internal_sound(self, duration: float = 0.8):
        """Ignore audio output produced by Cursor Buddy's own chimes."""
        self._ignore_audio_until = time.time() + duration

    def _init_audio_meter(self):
        try:
            p_enum = c_void_p()
            hr = ole32.CoCreateInstance(
                byref(CLSID_MMDeviceEnumerator),
                None,
                1,  # CLSCTX_INPROC_SERVER
                byref(IID_IMMDeviceEnumerator),
                byref(p_enum),
            )
            if hr != 0 or not p_enum.value:
                return

            vtable = ctypes.cast(p_enum, POINTER(POINTER(c_void_p))).contents
            # IMMDeviceEnumerator::GetDefaultAudioEndpoint (index 4)
            GetDefaultAudioEndpoint = ctypes.WINFUNCTYPE(
                HRESULT, c_void_p, wintypes.DWORD, wintypes.DWORD, POINTER(c_void_p)
            )(vtable[4])

            p_device = c_void_p()
            # eRender = 0, eMultimedia = 1
            hr = GetDefaultAudioEndpoint(p_enum, 0, 1, byref(p_device))

            # Release enumerator (IUnknown::Release is index 2)
            ctypes.WINFUNCTYPE(wintypes.ULONG, c_void_p)(vtable[2])(p_enum)

            if hr != 0 or not p_device.value:
                return

            dev_vtable = ctypes.cast(p_device, POINTER(POINTER(c_void_p))).contents
            # IMMDevice::Activate (index 3)
            Activate = ctypes.WINFUNCTYPE(
                HRESULT, c_void_p, POINTER(GUID), wintypes.DWORD, c_void_p, POINTER(c_void_p)
            )(dev_vtable[3])

            p_meter = c_void_p()
            hr = Activate(p_device, byref(IID_IAudioMeterInformation), 1, None, byref(p_meter))
            ctypes.WINFUNCTYPE(wintypes.ULONG, c_void_p)(dev_vtable[2])(p_device)

            if hr == 0 and p_meter.value:
                self._meter = p_meter
                meter_vtable = ctypes.cast(p_meter, POINTER(POINTER(c_void_p))).contents
                # IAudioMeterInformation::GetPeakValue (index 3)
                self._get_peak_func = ctypes.WINFUNCTYPE(
                    HRESULT, c_void_p, POINTER(c_float)
                )(meter_vtable[3])
        except Exception:
            self._meter = None
            self._get_peak_func = None

    def is_audio_playing(self) -> bool:
        """Returns True if any application is currently playing sound/media through default speakers."""
        now = time.time()
        if now < self._ignore_audio_until:
            return False

        if not self._meter or not self._get_peak_func:
            self._init_audio_meter()
            if not self._meter or not self._get_peak_func:
                return False

        try:
            peak = c_float(0.0)
            hr = self._get_peak_func(self._meter, byref(peak))
            if hr != 0:
                # Audio device or stream state changed; reset for re-enumeration
                self._meter = None
                return False

            if peak.value > self.PEAK_THRESHOLD:
                self._last_audio_activity = now
                return True
        except Exception:
            self._meter = None
            return False

        # Keep active state alive through speech pauses and quiet movie scenes
        return (now - self._last_audio_activity) < self.HOLD_TIME

    def is_fullscreen_active(self) -> bool:
        """Returns True if the user is in a fullscreen video, presentation, or game."""
        # 1. Official Windows Notification State check
        try:
            state = ctypes.c_int()
            if ctypes.windll.shell32.SHQueryUserNotificationState(ctypes.byref(state)) == 0:
                # 3 = QUNS_RUNNING_D3D_FULL_SCREEN, 4 = QUNS_PRESENTATION_MODE
                if state.value in (3, 4):
                    return True
        except Exception:
            pass

        # 2. Geometry check on active foreground window
        try:
            hwnd = win32gui.GetForegroundWindow()
            if not hwnd or not win32gui.IsWindow(hwnd) or not win32gui.IsWindowVisible(hwnd):
                return False

            cls = win32gui.GetClassName(hwnd)
            # Ignore standard desktop elements
            if cls in ("Progman", "WorkerW", "Shell_TrayWnd", "Button"):
                return False

            hmon = win32api.MonitorFromWindow(hwnd, win32con.MONITOR_DEFAULTTONEAREST)
            mon_info = win32api.GetMonitorInfo(hmon)
            mon_rect = mon_info["Monitor"]
            win_rect = win32gui.GetWindowRect(hwnd)

            # True fullscreen window spans or exceeds the entire monitor
            if (
                win_rect[0] <= mon_rect[0]
                and win_rect[1] <= mon_rect[1]
                and win_rect[2] >= mon_rect[2]
                and win_rect[3] >= mon_rect[3]
            ):
                return True
        except Exception:
            pass

        return False

    def is_media_active(self, check_audio: bool = True, check_fullscreen: bool = True) -> bool:
        """Throttled composite check combining audio playback and fullscreen detection."""
        now = time.time()
        if now - self._last_check_time >= self.CACHE_DURATION:
            self._last_check_time = now
            self._cached_audio = self.is_audio_playing() if check_audio else False
            self._cached_fullscreen = self.is_fullscreen_active() if check_fullscreen else False

        if check_fullscreen and self._cached_fullscreen:
            return True
        if check_audio and self._cached_audio:
            return True
        return False
