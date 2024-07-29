import speedtest
import subprocess
from typing import List
import urllib.request as ur
from urllib.error import URLError


class NetworkUtil:
    @staticmethod
    def isnetworkconnected() -> bool:
        try:
            ur.urlopen("https://github.com/codesrg/srutil")
            return True
        except URLError:
            return False

    @staticmethod
    def downloadspeed():
        """
        will return download speed in Mbps
        """
        return round(speedtest.Speedtest().download() / 1_000_000, 2)

    @staticmethod
    def uploadspeed():
        """
        will return upload speed in Mbps
        """
        return round(speedtest.Speedtest().upload() / 1_000_000, 2)

    @staticmethod
    def wifisiconnectedto() -> List[str]:
        """only for Windows OS"""
        winfo = subprocess.check_output(['netsh', 'wlan', 'show', 'profiles']).decode('utf-8').split('\n')
        ssid_list = [i.split(':')[1][1:-1] for i in winfo if 'All User Profile' in i]
        return ssid_list

    @staticmethod
    def getpasswordofwifiiconnectedto(ssid: str) -> str:
        """only for Windows OS"""
        winfo = subprocess.check_output(['netsh', 'wlan', 'show', 'profile', ssid, 'key=clear']).decode('utf-8')
        key_content = [info.split(':')[1][1:-1] for info in winfo.split("\n") if 'Key Content' in info]
        return key_content.pop(0) if len(key_content) > 0 else "no password"
