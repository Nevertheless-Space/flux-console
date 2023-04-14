# Changelog

All notable changes to this project are documented in this file.

## 0.7.1

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