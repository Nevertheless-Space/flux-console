from ctypes import windll
windll.shcore.SetProcessDpiAwareness(1)

from multiprocessing import freeze_support
from tkinter import *
import common.icon as icon
import common.style as style
from Home import Home

if __name__ == '__main__':

  freeze_support() # for pyinstaller on Windows
  frame_main = Tk()
  main_style = style.MainStyle(frame_main.winfo_screenwidth(), frame_main.winfo_screenheight())

  frame_main.title("NTL Flux Console v{{version}}")
  frame_main.geometry(main_style.getMainGeometry())
  frame_main.iconbitmap(main_style.icon_path)

  Home(frame=frame_main, style=main_style)

  frame_main.protocol("WM_DELETE_WINDOW", func=lambda: (icon.deleteIconFile(main_style.icon_path), frame_main.destroy()))
  frame_main.mainloop()