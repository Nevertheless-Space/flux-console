import sys
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
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

  sources = None
  kustomizations = None
  helmreleases = None
  imageautomations = None

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
    self.menubar_main.add_cascade(label="Appearance", menu=self.menubar_apparance)

    self.menubar_main.add_command(label="Kubeconfig Reload", command=self.kubeconfigReload)

  def deleteContent(self, frame):
    for widget in frame.winfo_children():
      widget.destroy()

  def initTabs(self, frame):

    self.deleteContent(frame)

    tabs = ttk.Notebook(frame)
    tabs.pack(fill=BOTH, expand=TRUE)

    sources_frame = ttk.Frame(tabs)
    sources_frame.pack(fill=BOTH, expand=TRUE)
    self.sources = SourcesFrame(sources_frame, self.style)
    tabs.add(sources_frame, text="Sources")

    kustomizations_frame = ttk.Frame(tabs)
    kustomizations_frame.pack(fill=BOTH, expand=TRUE)
    self.kustomizations = KustomizationsFrame(kustomizations_frame, self.style)
    tabs.add(kustomizations_frame, text="Kustomizations")

    helmreleases_frame = ttk.Frame(tabs)
    helmreleases_frame.pack(fill=BOTH, expand=TRUE)
    self.helmreleases = HelmReleasesFrame(helmreleases_frame, self.style)
    tabs.add(helmreleases_frame, text="HelmReleases")

    images_frame = ttk.Frame(tabs)
    images_frame.pack(fill=BOTH, expand=TRUE)
    self.imageautomations = ImageAutomationFrame(images_frame, self.style)
    tabs.add(images_frame, text="Image Automation")

  def initDashboard(self, frame):

    self.deleteContent(frame)

    frame_top = Frame(frame)
    frame_top.pack(fill=X, expand=FALSE, side=TOP)
    self.kustomizations = KustomizationsFrame(frame_top, self.style)

    frame_bottom = Frame(frame)
    frame_bottom.pack(fill=BOTH, expand=TRUE, side=BOTTOM)
    self.helmreleases = HelmReleasesFrame(frame_bottom, self.style)

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
        utils.redirectOutputCommand(command, stderr=True, decode_error_replacement=".")
    except: pass

  def reconcileGitRepositories_popup(self):
    popup_frame = utils.outputRedirectedPopup(title="All GitRepository Reconciliation", style=self.style)
    self.reconcileGitRepositories()
    popup_frame.mainloop()

  def kubeconfigReload(self):
    try:
      if self.sources != None: self.sources.k8s.clientInit()
      if self.kustomizations != None: self.kustomizations.k8s.clientInit()
      if self.helmreleases != None: self.helmreleases.k8s.clientInit()
      if self.imageautomations != None: self.imageautomations.k8s.clientInit()
    except Exception as e:
      messagebox.showerror(title="Kubebernetes API Error", message=e)