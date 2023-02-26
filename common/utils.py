import sys
import json
import multiprocessing
import threading
import subprocess
from tkinter import *

def kubectl_command(command):
  result = subprocess.run(command.split(' ') + ["-o", "json"], capture_output=True, shell=True)
  error = result.stderr.decode()
  if error != "":
    return { "stdout": result.stdout.decode(), "stderr": result.stderr.decode()}
  else:
    return { "stdout": json.loads(result.stdout), "stderr": result.stderr.decode()}

def generic_command(command):
  result = subprocess.run(command.split(' '), capture_output=True, shell=True)
  error = result.stderr.decode()
  return { "stdout": result.stdout.decode(), "stderr": result.stderr.decode()}

class StdoutRedirector():
  def __init__(self,text_widget):
      self.text_space = text_widget
  def write(self,string):
      self.text_space.insert('end', string)
      self.text_space.see('end')
  def flush(self):
      self.text_space.update()

def subcommandOutputRedirect(process, stderr=False, decode_error_replacement="", queue=None):
  while True:
    try:
      if stderr: out = process.stderr.read(1).decode()
      else: out = process.stdout.read(1).decode()
    except UnicodeDecodeError:
      out = decode_error_replacement
    if out == '' and process.poll() != None:
      break
    if out != '':
      if queue != None: queue.put(out)
      else:
        sys.stdout.write(out)
        sys.stdout.flush()

def redirectOutputCommand(command, stderr=False, decode_error_replacement="", queue=None):
  process = subprocess.Popen(command, shell=True, stderr=subprocess.PIPE)
  threading.Thread(target=subcommandOutputRedirect, args=(process,stderr,decode_error_replacement,queue)).start()

def outputRedirectedPopup(style, title):

  frame_secondary_window = Toplevel()

  frame_secondary_window.title(title)
  frame_secondary_window.geometry(style.getPopupGeometry())
  frame_secondary_window.iconbitmap(style.icon_path)

  frame_content = Frame(frame_secondary_window)
  frame_content.pack(fill=BOTH, expand=TRUE,padx=5*style.multiplier, pady=5*style.multiplier)

  scroll_v = Scrollbar(frame_content)
  scroll_v.pack(side=RIGHT,fill=Y)
  text = Text(frame_content, yscrollcommand= scroll_v.set, wrap="word", font=style.getTextFont01(), foreground=style.text_font01_color)
  text.pack(fill=BOTH, expand=TRUE)
  scroll_v.config(command = text.yview)

  sys.stdout = StdoutRedirector(text)
  
  return frame_secondary_window

def subprocessOutputRedirect(process, queue):
  wait = True
  while wait or queue.qsize() != 0:
    if not process.is_alive():
      wait = False
    if queue.qsize() != 0:
      sys.stdout.write(queue.get())
      sys.stdout.flush()

def subprocessRun(target_function, args: tuple):
  queue = multiprocessing.Queue()
  process = multiprocessing.Process(target=target_function, args=args, kwargs={"queue": queue})
  process.start()
  threading.Thread(target=subprocessOutputRedirect, args=(process,queue)).start()
  return process

def terminateFrameProcesses(frame, processes: list):
  for process in processes: process.terminate()
  frame.destroy()