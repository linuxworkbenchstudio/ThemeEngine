# Changelog

## 0.1.1 — widgets are no longer bundled
- Panel Colorizer (Luis Bocanegra) and KVitals (Yassine Amjad) are not included in the zip any more.
  The installer checks for them, installs from the AUR if you use yay or paru, and otherwise lists
  where to get them (KDE Store, the authors' repositories). You can exit the installer, install them
  yourself, and run it again. The theme installs without them; the panel is plainer.
- Removed `<command> widget` and the `--widgets` option.

## 0.1.0 — first release by The Linux Workbench (was Vice Horizon 1.8.2)
- Now built by The Linux Workbench theme engine, with Waypoint and Natura: fixes and new features
  reach every theme. Global Themes are `org.thelinuxworkbench.vicehorizon.dark|light`; an
  install of 1.8 (`org.digitalcohesion.vicehorizon.*`) is moved over when you agree.
- The top panel is 32 px (was 36); Cards has no bar behind the cards, like Pills.
- Konsole keeps unlimited scrollback.
- The Fastfetch tool and the Konsole switch recognise every The Linux Workbench theme.
- Licence texts in every installed folder.
- Icons readable in the panel: up to 32 px, app tiles use a bigger glyph (and no bar); tiles have
  no light edge; the top panel's margins are slimmer, so Task Manager icons are bigger.
