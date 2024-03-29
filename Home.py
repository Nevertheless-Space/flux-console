import sys
import threading
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from common import utils, k8s
from flux.KustomizationsFrame import KustomizationsFrame
from flux.HelmReleasesFrame import HelmReleasesFrame
from flux.SourcesFrame import SourcesFrame
from flux.ImageAutomationFrame import ImageAutomationFrame
from flux.EventsFrame import EventsFrame

class Home():

  style = None

  menubar = None
  menubar_main = None
  menubar_reconcile = None
  menubar_apparance = None

  kubecontexts = []
  kubecontexts_combobox = None

  sources = None
  kustomizations = None
  helmreleases = None
  imageautomations = None
  events = None

  def __init__(self, frame, style):
    self.style = style

    frame_topbar = Frame(frame, height=50, padx=self.style.fringe_padding, pady=self.style.fringe_padding)
    frame_topbar.pack(fill=X, side=TOP)
    frame_divider = ttk.Separator(frame, orient='horizontal')
    frame_divider.pack(fill=X, side=TOP)
    frame_content = Frame(frame)
    frame_content.pack(fill=BOTH, expand=TRUE, side=BOTTOM)

    self.initMenuBar(frame=frame, frame_content=frame_content)
    self.initTopBar(frame=frame_topbar)
    try: self.initDashboard(frame_content)
    except k8s.KubernetesAPI as e:
      messagebox.showerror(title="Kubernetes API Error", message=e)
      return
  
  def initMenuBar(self, frame, frame_content):
    self.menubar = Menu(frame)
    frame.config(menu=self.menubar)

    self.menubar_main = Menu(self.menubar, tearoff=0)
    self.menubar.add_cascade(label="Menu", menu=self.menubar_main)

    self.menubar_reconcile = Menu(self.menubar_main, tearoff=0)
    self.menubar_reconcile.add_command(label="Flux-System", command=lambda: threading.Thread(target=self.reconcilefluxsystem_popup).start())
    self.menubar_reconcile.add_command(label="All GitRepository", command=lambda: threading.Thread(target=self.reconcileallgitrepository_popup).start())
    self.menubar_reconcile.add_command(label="All ImageRepository", command=lambda: threading.Thread(target=self.reconcileallimagerepository_popup).start())
    self.menubar_main.add_cascade(label="Reconcile", menu=self.menubar_reconcile)

    self.menubar_apparance = Menu(self.menubar_main, tearoff=0)
    self.menubar_apparance.add_command(label="Dashboard", command=lambda: self.initDashboard(frame_content))
    self.menubar_apparance.add_command(label="Tabs", command=lambda: self.initTabs(frame_content))
    self.menubar_main.add_cascade(label="Appearance", menu=self.menubar_apparance)

    self.menubar_main.add_command(label="Kubeconfig Reload", command=self.kubeconfigReload)

  def initTopBar(self, frame):
    self.selected_kubecontext = StringVar()

    label = ttk.Label(frame, text="Kubeconfig Context:")
    label.pack(side=LEFT)
    self.kubecontexts_combobox = ttk.Combobox(frame, textvariable=self.selected_kubecontext, font=self.style.getMainFont())
    frame.option_add('*TCombobox*Listbox.font', self.style.getMainFont())

    self.initKubecontexts()

    self.kubecontexts_combobox.bind('<<ComboboxSelected>>', lambda event: self.kubecontextSelected())
    self.kubecontexts_combobox.bind('<Return>', self.kubecontextsFilter)
    self.kubecontexts_combobox.pack(fill=X, expand=FALSE, padx=[self.style.fringe_padding, self.style.fringe_padding*3])

  def initKubecontexts(self):
    contexts_result = utils.generic_command("kubectl config view -o=jsonpath='{.contexts[*].name}'")
    if contexts_result["stderr"] != '':
      messagebox.showerror(title="Kubectl Error", message=contexts_result["stderr"])
      return
    self.kubecontexts = contexts_result["stdout"].replace("'","").split(" ")
    self.setCurrentContext()
    self.kubecontexts_combobox["values"] = [f'{context}' for context in self.kubecontexts]

  def setCurrentContext(self):
    current_context_result = utils.generic_command("kubectl config view -o=jsonpath='{.current-context}'")
    if current_context_result["stderr"] != '':
        messagebox.showerror(title="Kubectl Error", message=current_context_result["stderr"])
        return
    self.selected_kubecontext.set(current_context_result["stdout"].replace("'",""))

  def kubecontextSelected(self):
    context = self.selected_kubecontext.get()
    result = utils.generic_command(f"kubectl config use-context {context}")
    if result["stderr"] != '':
        messagebox.showerror(title="Kubectl Error", message=result["stderr"])
        return
    self.kubeconfigReload()

  def kubecontextsFilter(self, event):
    value = event.widget.get()
    if value == '':
      self.kubecontexts_combobox['values'] = self.kubecontexts
    else:
      data = []
      for item in self.kubecontexts:
        matched = True
        for keyword in value.lower().split(' '):
          if matched and keyword in item.lower(): continue
          else:
            matched = False
            break
        if matched: data.append(item)
      self.kubecontexts_combobox['values'] = data
    self.kubecontexts_combobox.event_generate('<Down>')

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

    events_frame = ttk.Frame(tabs)
    events_frame.pack(fill=BOTH, expand=TRUE)
    self.events = EventsFrame(events_frame, self.style)
    tabs.add(events_frame, text="Events")

  def initDashboard(self, frame):

    self.deleteContent(frame)

    frame_top = Frame(frame)
    frame_top.pack(fill=X, expand=FALSE, side=TOP)
    self.kustomizations = KustomizationsFrame(frame_top, self.style)

    frame_divider = ttk.Separator(frame, orient='horizontal')
    frame_divider.pack(fill=X, side=TOP, padx=[self.style.fringe_padding, 4*self.style.fringe_padding])

    frame_bottom = Frame(frame)
    frame_bottom.pack(fill=BOTH, expand=TRUE, side=BOTTOM)
    self.helmreleases = HelmReleasesFrame(frame_bottom, self.style)

  def reconcilefluxsystem_popup(self):
    popup_frame = utils.outputRedirectedPopup(title="Flux-System Reconciliation", style=self.style)
    try:
      command = f'flux reconcile source git -n flux-system flux-system'
      print(command)
      result = utils.generic_command(command)
      print(result["stderr"])
      popup_frame.mainloop()
    except:
      pass

  def reconcileallgitrepository_popup(self):
    popup_frame = utils.outputRedirectedPopup(title="All GitRepository Reconciliation", style=self.style)
    k8_client = k8s.FluxClient()
    gitrepositories = k8_client.getAllSources(plurals=["gitrepositories"])
    try:
      for gitrepository in gitrepositories:
        command = f'flux reconcile source git -n {gitrepository["metadata"]["namespace"]} {gitrepository["metadata"]["name"]}'
        print(command)
        result = utils.generic_command(command)
        print(result["stderr"])
      popup_frame.mainloop()
    except:
      pass

  def reconcileallimagerepository_popup(self):
    popup_frame = utils.outputRedirectedPopup(title="All ImageRepository Reconciliation", style=self.style)
    k8_client = k8s.FluxClient()
    imagerepositories = k8_client.getAllImages(plurals=["imagerepositories"])
    try:
      for imagerepository in imagerepositories:
        command = f'flux reconcile image repository -n {imagerepository["metadata"]["namespace"]} {imagerepository["metadata"]["name"]}'
        print(command)
        result = utils.generic_command(command)
        print(result["stderr"])
      popup_frame.mainloop()
    except:
      pass

  def kubeconfigReload(self):
    try:
      if self.sources != None: self.sources.k8s.clientInit()
      if self.kustomizations != None: self.kustomizations.k8s.clientInit()
      if self.helmreleases != None: self.helmreleases.k8s.clientInit()
      if self.imageautomations != None: self.imageautomations.k8s.clientInit()
      if self.events != None: self.events.k8s.clientInit()
      self.initKubecontexts()
    except Exception as e:
      messagebox.showerror(title="Kubernetes API Error", message=e)