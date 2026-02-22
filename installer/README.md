# OpenMetro Installer

A Metro-styled single-file installer for OpenMetro. `openmetro.exe` is bundled inside the installer — just one file to distribute.

## Build order

**1. Build the client first:**
```
cd openmetro
pyinstaller openmetro.spec
```

**2. Then build the installer:**
```
cd installer
pyinstaller installer.spec
```

Output: `installer/dist/openmetro-setup.exe`

The installer spec references `..dist/openmetro.exe` and bundles it automatically.

## What it does

1. Extracts `openmetro.exe` from the bundle to `%LOCALAPPDATA%\OpenMetro\`
2. Creates a Start Menu shortcut under `Programs\OpenMetro\`
3. Optionally adds OpenMetro to Windows startup
4. Offers to launch OpenMetro immediately after install
