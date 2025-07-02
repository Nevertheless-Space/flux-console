import sys
import json
import threading
import subprocess
import shutil
import os
from tkinter import *

def find_kubectl():
  kubectl_path = shutil.which('kubectl')
  if kubectl_path:
    return kubectl_path
  common_paths = [
    '/usr/local/bin/kubectl',
    '/opt/homebrew/bin/kubectl',
    '/usr/bin/kubectl',
    os.path.expanduser('~/.local/bin/kubectl')
  ]
  for path in common_paths:
    if os.path.isfile(path) and os.access(path, os.X_OK):
      return path
  return 'kubectl'

def find_flux():
  flux_path = shutil.which('flux')
  if flux_path:
    return flux_path
  common_paths = [
    '/usr/local/bin/flux',
    '/opt/homebrew/bin/flux',
    '/usr/bin/flux',
    os.path.expanduser('~/.local/bin/flux')
  ]
  for path in common_paths:
    if os.path.isfile(path) and os.access(path, os.X_OK):
      return path
  return 'flux'

KUBECTL_PATH = find_kubectl()
FLUX_PATH = find_flux()

def kubectl_command(command):
  if command.startswith('kubectl'):
    command = command.replace('kubectl', KUBECTL_PATH, 1)
  elif command.startswith('flux'):
    command = command.replace('flux', FLUX_PATH, 1)
  result = subprocess.run(command + " -o json", capture_output=True, shell=True)
  error = result.stderr.decode()
  if error != "":
    return { "stdout": result.stdout.decode(), "stderr": result.stderr.decode()}
  else:
    return { "stdout": json.loads(result.stdout), "stderr": result.stderr.decode()}

def generic_command(command):
  if command.startswith('kubectl'):
    command = command.replace('kubectl', KUBECTL_PATH, 1)
  elif command.startswith('flux'):
    command = command.replace('flux', FLUX_PATH, 1)
  result = subprocess.run(command, capture_output=True, shell=True)
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
  if command.startswith('kubectl'):
    command = command.replace('kubectl', KUBECTL_PATH, 1)
  elif command.startswith('flux'):
    command = command.replace('flux', FLUX_PATH, 1)
  process = subprocess.Popen(command, shell=True, stderr=subprocess.PIPE)
  thread = threading.Thread(target=subcommandOutputRedirect, args=(process,stderr,decode_error_replacement,queue))
  thread.start()
  return thread

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
  while True:
    try:
      output = process.stdout.read(1).decode()
      if output == '' and process.poll() is not None:
        break
      if output != '':
        sys.stdout.write(output)
        sys.stdout.flush()
    except:
      break

def subprocessRun(target_function, args: tuple):
  thread = threading.Thread(target=target_function, args=args)
  thread.start()
  return thread

def terminateFrameProcesses(frame, processes: list):
  frame.destroy()