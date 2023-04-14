from ctypes import windll
windll.shcore.SetProcessDpiAwareness(1)

from multiprocessing import freeze_support
from tkinter import *
import common.icon as icon
import common.style as style
import requests
import semver
from Home import Home

def getTitle():
  current_version = "0.0.0"
  url = "https://github.com/Nevertheless-Space/flux-console/releases/latest"
  response = requests.head(url=url)
  latest_version = response.next.url.split("/")[-1]

  title_base = f"NTL Flux Console v{current_version}"
  if semver.Version.parse(latest_version) > semver.Version.parse(current_version):
    return f"{title_base} [v{latest_version} available]"
  else:
    return title_base

def closeWindow(frame, style):
  try: icon.deleteIconFile(style.icon_path)
  finally: frame.destroy()

if __name__ == '__main__':

  freeze_support() # for pyinstaller on Windows
  frame_main = Tk()
  main_style = style.MainStyle(frame_main.winfo_screenwidth(), frame_main.winfo_screenheight())

  frame_main.title(getTitle())
  frame_main.geometry(main_style.getMainGeometry())
  frame_main.iconbitmap(main_style.icon_path)

  Home(frame=frame_main, style=main_style)

  frame_main.protocol("WM_DELETE_WINDOW", func=lambda: closeWindow(frame_main, main_style))
  frame_main.mainloop()