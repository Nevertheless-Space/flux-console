# Changelog

All notable changes to this project are documented in this file.

## 0.9.0

- New features:
  - `HelmRelease` deletion in the `Danger` context menu
  - New `Revision` column for the `HelmReleases` section
  - Search results counter
- UI tuning
- Bug fixing:
  - Failures due to additional spaces are now handled without impacting the returned results
  - The scenarios in which autoreload was active but the autoreload routine had failed have been handled, now the autoreload checkbox faithfully reproduces the state of the underlying routine

## 0.8.2

- Events without namespace and message fixed

## 0.8.1

- Events tab UI improved for 1080p resolution

## 0.8.0

- New Events Tab
- Column search improved with partial search and exclusion
- Minor improvements

## 0.7.1

- `ImageUpdateAutomation` Resources missing in the `Image Automation` tab: fixed
- Manifests for Image Automation Resources are not shown after the click in the context menu: fixed
- Minor improvements

## 0.7.0

- The availability of a new version has been added in the title of the main window
- Build script improvement: pinning build venv

## 0.6.5

- Current status fix: now the `Status` and `Message` column is taken from the condition with `type: Ready`

## 0.6.4

- Status Column of Flux Resources has been fixed: some failure conditions were not detected correctly

## 0.6.3

- Fix for when not all resources in the same API-Group support all versions of the Group
- Word wrap for the content of the context menu `Status` field

## 0.6.2

- Delete icon failure silenced

## 0.6.1

- Autoreload mutex and exception management
- Helm Values multi windows support fix

## 0.6.0

- `KUBECONFIG` Contexts multi-keyword search
- `status.conditions` missing error handled
- The Kubeconfig Reload now will update also the `KUBECONFIG` Contexts
- Startup issues with the `KUBECONFIG` file handled
- Utility to get always the latest versions added: `utils/get-latest-version.ps1`

## 0.5.0

- Exception handling during the Auto Reload
- Last column sorting honored on reload
- `KUBECONFIG` Contexts switch dropdown menu
- Minor improvements

## 0.4.1

- Fixing `Menu > Reconcile > All GitRepository` output concurrency making the operations in sequence
- Trying to fix the closing window issue, handling the icon removal exceptions
- Fixing the Helm Values Revisions header size issue
- Helm get values and uninstall improvements and bug fixing

## 0.4.0

- Changelog added
- Flux Reconcile commands are now separate processes
- Dynamic icon generation
- Minor improvements