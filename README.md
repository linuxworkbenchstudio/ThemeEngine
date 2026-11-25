# The Linux Workbench themes

Complete desktop themes for **KDE Plasma 6** and **COSMIC**, each in Dark and Light: colours, apps, icons, cursors, panel, terminal and wallpapers, switched with one command. Made by The Linux Workbench.

**Website:** https://linuxworkbenchstudio.github.io/lwbs-themes/ · **Downloads:** [Releases](https://github.com/linuxworkbenchstudio/lwbs-themes/releases)

## Themes

| Theme | Look | Status |
|---|---|---|
| [**Waypoint**](packs/waypoint) | Graphite and machined amber | Out now (0.1.2) |
| [**Vice Horizon**](packs/vice-horizon) | A sunset palette | Out now (0.1.2) |
| [**Natura**](packs/natura) | Ink, sage and vermillion | Out now (0.1.2) |
| **Vacation** | Ocean, lagoon teal and warm sand | Coming soon |
| **Vintage Trail** | Charcoal, sage, canvas and brass | Coming soon |
| **Core** | Platinum, midnight and soft blue | Coming soon |

### Waypoint

| KDE Plasma 6 | COSMIC |
|---|---|
| ![Waypoint Dark on KDE](packs/waypoint/art/screenshots/dark-kde.jpg) | ![Waypoint Dark on COSMIC](packs/waypoint/art/screenshots/dark-cosmic.jpg) |
| ![Waypoint Light on KDE](packs/waypoint/art/screenshots/light-kde.jpg) | ![Waypoint Light on COSMIC](packs/waypoint/art/screenshots/light-cosmic.jpg) |

### Vice Horizon

| KDE Plasma 6 | COSMIC |
|---|---|
| ![Vice Horizon Dark on KDE](packs/vice-horizon/art/screenshots/dark-kde.jpg) | ![Vice Horizon Dark on COSMIC](packs/vice-horizon/art/screenshots/dark-cosmic.jpg) |
| ![Vice Horizon Light on KDE](packs/vice-horizon/art/screenshots/light-kde.jpg) | ![Vice Horizon Light on COSMIC](packs/vice-horizon/art/screenshots/light-cosmic.jpg) |

### Natura

| KDE Plasma 6 | COSMIC |
|---|---|
| ![Natura Dark on KDE](packs/natura/art/screenshots/dark-kde.jpg) | ![Natura Dark on COSMIC](packs/natura/art/screenshots/dark-cosmic.jpg) |
| ![Natura Light on KDE](packs/natura/art/screenshots/light-kde.jpg) | ![Natura Light on COSMIC](packs/natura/art/screenshots/light-cosmic.jpg) |

## Install

**KDE Plasma 6:** download the theme's full zip from [Releases](https://github.com/linuxworkbenchstudio/lwbs-themes/releases), unzip it, and run `./install.sh`. It is a guided setup in the terminal, and nothing changes until you press Install. Afterwards `<theme> dark` or `<theme> light` switches everything.

**COSMIC:** download the theme's COSMIC zip and run `./install.sh`, then open Settings › Desktop › Appearance, choose Dark or Light, press Import and pick the matching `.ron` file.

Check a download: `sha256sum -c --ignore-missing CHECKSUMS.sha256`

### Needs (KDE panel)

The top panel uses two widgets made by other people. The themes don't bundle or change them; the installer checks for both and asks before it fetches anything (AUR with yay or paru, otherwise the KDE Store, for your user only). Without them the theme still installs and the panel is plainer.

- **Panel Colorizer** by Luis Bocanegra: gives the panel its look. [KDE Store](https://store.kde.org/p/2130967) · [GitHub](https://github.com/luisbocanegra/plasma-panel-colorizer)
- **KVitals** by Yassine Amjad: CPU, RAM, GPU and network stats (needs lm_sensors). [KDE Store](https://store.kde.org/p/2347917) · [GitHub](https://github.com/yassine20011/kvitals)

## Help

Questions or problems: [GitHub Issues](https://github.com/linuxworkbenchstudio/lwbs-themes/issues). Code is GPL-3.0-or-later; wallpapers are all rights reserved (free to use as wallpapers).

---

## For developers: how the themes are made

**Experimental, no support.** The engine is published as is, under GPL-3.0-or-later. The pack format is still changing, so expect breaking changes, and issues about building your own packs may go unanswered. The themes above are the supported product.

All themes come from one small engine: each theme is a *pack* (colours, names, artwork) and the engine writes every file from it, so a fix reaches every theme at once. `DESIGN.md` has the plan and the decisions.

```
python3 -m engine check packs/waypoint             # check a pack: palette, contrast, ids, parts
python3 -m engine build packs/waypoint --out dist  # write the theme's files
python3 -m engine compare packs/waypoint           # how much of the released theme the engine reproduces
python3 -m unittest discover -s tests -t . -v      # tests
python3 tools/build_site.py                         # the website, into site/ (needs Pillow)
```

Python 3.11 or newer, nothing to install.

## References

`compare` checks the engine against each theme's last release, kept in `references/<pack>/`
(not in the repository: tens of megabytes of icons). Fill it with:

```
python3 tools/import_reference.py vice-horizon Vice-Horizon-source.zip     # 1.8.2 source tree
python3 tools/import_reference.py waypoint     Waypoint-KDE-0.5.0.zip      # the release zip
```

## Status

Parts made by the engine: KDE colour schemes, Konsole colour schemes and profiles (Waypoint:
identical to the release). The other parts move over one at a time; see `DESIGN.md`.
