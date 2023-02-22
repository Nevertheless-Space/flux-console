import sys
from tkinter import *
from tkinter import ttk
from common import utils, k8s
from flux.KustomizationsFrame import KustomizationsFrame
from flux.HelmReleasesFrame import HelmReleasesFrame
from flux.SourcesFrame import SourcesFrame
from flux.ImageAutomationFrame import ImageAutomationFrame

class Home():

  style = None

  menubar = None
  menubar_main = None
  menubar_reconcile = None
  menubar_apparance = None

  def __init__(self, frame, style):
    self.style = style

    frame_content = Frame(frame)
    frame_content.pack(fill=BOTH, expand=TRUE, side=BOTTOM)

    self.initMenuBar(frame=frame, frame_content=frame_content)
    self.initDashboard(frame_content)
  
  def initMenuBar(self, frame, frame_content):
    self.menubar = Menu(frame)
    frame.config(menu=self.menubar)

    self.menubar_main = Menu(self.menubar, tearoff=0)
    self.menubar.add_cascade(label="Menu", menu=self.menubar_main)

    self.menubar_reconcile = Menu(self.menubar_main, tearoff=0)
    self.menubar_reconcile.add_command(label="All GitRepository", command=self.reconcileGitRepositories_popup)
    self.menubar_main.add_cascade(label="Reconcile", menu=self.menubar_reconcile)

    self.menubar_apparance = Menu(self.menubar_main, tearoff=0)
    self.menubar_apparance.add_command(label="Dashboard", command=lambda: self.initDashboard(frame_content))
    self.menubar_apparance.add_command(label="Tabs", command=lambda: self.initTabs(frame_content))
    self.menubar_main.add_cascade(label="Apparence", menu=self.menubar_apparance)

  def deleteContent(self, frame):
    for widget in frame.winfo_children():
      widget.destroy()

  def initTabs(self, frame):

    self.deleteContent(frame)

    tabs = ttk.Notebook(frame)
    tabs.pack(fill=BOTH, expand=TRUE)

    sources_frame = ttk.Frame(tabs)
    sources_frame.pack(fill=BOTH, expand=TRUE)
    SourcesFrame(sources_frame, self.style)
    tabs.add(sources_frame, text="Sources")

    kustomizations_frame = ttk.Frame(tabs)
    kustomizations_frame.pack(fill=BOTH, expand=TRUE)
    KustomizationsFrame(kustomizations_frame, self.style)
    tabs.add(kustomizations_frame, text="Kustomizations")

    helmreleases_frame = ttk.Frame(tabs)
    helmreleases_frame.pack(fill=BOTH, expand=TRUE)
    HelmReleasesFrame(helmreleases_frame, self.style)
    tabs.add(helmreleases_frame, text="HelmReleases")

    images_frame = ttk.Frame(tabs)
    images_frame.pack(fill=BOTH, expand=TRUE)
    ImageAutomationFrame(images_frame, self.style)
    tabs.add(images_frame, text="Image Automation")

  def initDashboard(self, frame):

    self.deleteContent(frame)

    frame_top = Frame(frame)
    frame_top.pack(fill=X, expand=FALSE, side=TOP)
    KustomizationsFrame(frame_top, self.style)

    frame_bottom = Frame(frame)
    frame_bottom.pack(fill=BOTH, expand=TRUE, side=BOTTOM)
    HelmReleasesFrame(frame_bottom, self.style)

  def reconcileGitRepositories(self):
    k8_client = k8s.FluxClient()
    gitrepositories = k8_client.getAllSources(plurals=["gitrepositories"])

    first = True
    try:
      for gitrepository in gitrepositories:
        command = f'flux reconcile source git -n {gitrepository["metadata"]["namespace"]} {gitrepository["metadata"]["name"]}'
        if not first: print()
        else: first = False
        print(f"{command}:")
        utils.stderr_command(command, decode_error_replacement=".")
    except:
      pass

  def reconcileGitRepositories_popup(self):

    frame_secondary_window = Toplevel()

    frame_secondary_window.title("All GitRepository Reconciliation")
    frame_secondary_window.geometry(self.style.getPopupGeometry())
    frame_secondary_window.iconbitmap(self.style.icon_path)

    frame_content = Frame(frame_secondary_window)
    frame_content.pack(fill=BOTH, expand=TRUE,padx=5*self.style.multiplier, pady=5*self.style.multiplier)

    scroll_v = Scrollbar(frame_content)
    scroll_v.pack(side=RIGHT,fill=Y)
    text = Text(frame_content, yscrollcommand= scroll_v.set, wrap="word", font=self.style.getTextFont01(), foreground=self.style.text_font01_color)
    text.pack(fill=BOTH, expand=TRUE)
    scroll_v.config(command = text.yview)

    sys.stdout = utils.StdoutRedirector(text)
    self.reconcileGitRepositories()

    frame_secondary_window.mainloop()