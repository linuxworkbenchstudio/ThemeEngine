#!/usr/bin/env python3
"""Build the website into site/: a home page with every theme, and one page per theme.

    python3 tools/build_site.py            writes site/ (published by .github/workflows/pages.yml)

Everything comes from the packs: names, taglines, versions, palettes (Dark and Light), the
launcher logo and the wallpapers. A pack whose wallpaper is still placeholder artwork
([theme.site] placeholder_wallpaper = true) gets a hero drawn from its palette instead.
Each theme page follows the reader's light/dark setting, with a switch; it shows the theme's
own Dark or Light colours.
"""
from __future__ import annotations

import html
import json
import shutil
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from engine.colour import contrast  # noqa: E402
from engine.pack import load  # noqa: E402

REPO = "linuxworkbenchstudio/lwbs-themes"
GITHUB = f"https://github.com/{REPO}"
KOFI = "https://ko-fi.com/linuxworkbench"
CONTACT = "linuxworkbenchstudio@gmail.com"
ORDER = ["waypoint", "vice-horizon", "natura", "vacation", "vintage-trail", "core"]
SWATCHES = [("window_bg", "Background"), ("surface_raised", "Surface"), ("button_bg", "Raised"),
            ("text", "Text"), ("text_muted", "Muted"), ("accent", "Accent"),
            ("positive", "Success"), ("neutral", "Warning"), ("negative", "Error")]
FEATURES = [
    ("Global Theme", "Dark and Light, with its own splash screen and wallpapers."),
    ("Plasma Style and colours", "Panels, popups and widgets, colour schemes and window borders."),
    ("Apps", "A Kvantum style for Qt apps and a GTK theme for Firefox, GIMP and Inkscape, switched with the rest."),
    ("Icons and cursors", "About 145 folder types, 600 app tiles and 260 file types; Breeze cursors recoloured."),
    ("Top panel", "Launcher, tasks, a centred clock and system stats, in six looks from Normal to Fancy."),
    ("Terminal", "Konsole colour schemes and profiles, and Fastfetch in the theme's colours."),
    ("One command", "Switch everything between Dark and Light, with a Settings app for the rest."),
    ("COSMIC too", "Dark and Light themes and wallpapers for the COSMIC desktop."),
]

E = html.escape


def rgb_triplet(hexcol: str) -> str:
    return ", ".join(str(int(hexcol[i:i + 2], 16)) for i in (1, 3, 5))


def editions(pack):
    eds = list(pack.editions.values())
    dark = next(e for e in eds if e.template == "dark")
    light = next((e for e in eds if e.template == "light"), dark)
    return dark, light


def css_vars(ed) -> str:
    r = ed.roles
    on_accent = max((r["base_bg"], r["text"], "#FFFFFF", "#000000"), key=lambda c: contrast(c, r["accent"]))
    return (f"--bg: {r['window_bg']}; --deep: {r['base_bg']}; --surface: {r['surface_raised']}; "
            f"--raised: {r['button_bg']}; --line: {r['border']}; --text: {r['text']}; "
            f"--muted: {r['text_muted']}; --accent: {r['accent']}; --on-accent: {on_accent}; "
            f"--accent-rgb: {rgb_triplet(r['accent'])};")


BASE_CSS = """
*, *::before, *::after { box-sizing: border-box; }
html { -webkit-text-size-adjust: 100%; }
body { margin: 0; background: var(--bg); color: var(--text);
  font: 16px/1.6 "Inter", system-ui, -apple-system, "Segoe UI", sans-serif; }
a { color: var(--accent); }
img { max-width: 100%; display: block; }
.wrap { max-width: 1120px; margin: 0 auto; padding: 0 16px; }
header.top { position: sticky; top: 0; z-index: 5; backdrop-filter: blur(12px);
  background: color-mix(in srgb, var(--bg) 82%, transparent); border-bottom: 1px solid var(--line); }
header.top .wrap { display: flex; align-items: center; gap: 16px; height: 56px; }
.brand { color: var(--text); text-decoration: none; font-weight: 650; letter-spacing: .02em; white-space: nowrap; }
@media (max-width: 520px) { .brand small { display: none; } header.top .wrap { gap: 10px; } }
.brand small { color: var(--muted); font-weight: 500; margin-left: 6px; }
.spacer { flex: 1; }
.navlink { color: var(--muted); text-decoration: none; font-size: 14px; }
.navlink:hover { color: var(--text); }
.switch { display: inline-flex; border: 1px solid var(--line); border-radius: 999px; padding: 2px; }
.switch button { font: inherit; font-size: 13px; border: 0; background: none; color: var(--muted);
  padding: 4px 12px; border-radius: 999px; cursor: pointer; }
.switch button[aria-pressed="true"] { background: var(--accent); color: var(--on-accent); }
.btn { display: inline-flex; align-items: center; gap: 8px; padding: 10px 18px; border-radius: 10px;
  font-weight: 600; text-decoration: none; border: 1px solid transparent; }
.btn.primary { background: var(--accent); color: var(--on-accent); }
.btn.ghost { border-color: color-mix(in srgb, currentColor 35%, transparent); color: inherit; }
h1, h2, h3 { line-height: 1.2; margin: 0; }
h2 { font-size: 24px; margin-bottom: 20px; }
section { padding: 56px 0; border-top: 1px solid var(--line); }
footer { padding: 32px 0 48px; color: var(--muted); font-size: 14px; border-top: 1px solid var(--line); }
code, pre { font-family: "JetBrains Mono", ui-monospace, "DejaVu Sans Mono", monospace; font-size: 14px; }
pre { background: var(--deep); border: 1px solid var(--line); border-radius: 10px; padding: 14px 16px;
  overflow-x: auto; margin: 0; }
"""

THEME_CSS = """
.hero { position: relative; min-height: min(78vh, 640px); display: flex; align-items: flex-end;
  color: #fff; background: var(--deep) center / cover no-repeat; overflow: hidden; }
.hero::after { content: ""; position: absolute; inset: 0;
  background: linear-gradient(180deg, rgba(0,0,0,0) 35%, rgba(0,0,0,.62) 100%); }
.hero.drawn { background: radial-gradient(1200px 520px at 70% 10%, rgba(var(--accent-rgb), .35), transparent 60%),
  linear-gradient(160deg, var(--surface), var(--deep)); color: var(--text); }
.hero.drawn::after { display: none; }
.hero .wrap { position: relative; z-index: 1; width: 100%; padding-bottom: 48px; }
.hero .logo { width: 88px; height: 88px; filter: drop-shadow(0 8px 24px rgba(0,0,0,.35)); }
.hero h1 { font-size: clamp(36px, 7vw, 64px); margin: 18px 0 8px; letter-spacing: -.01em; }
.hero p { font-size: 18px; max-width: 560px; margin: 0 0 24px; opacity: .92; }
.hero .actions { display: flex; flex-wrap: wrap; gap: 12px; }
.hero .version { font-size: 13px; opacity: .8; margin-top: 16px; }
.hero:not(.drawn) .btn.ghost { color: #fff; }
.swatches { display: grid; grid-template-columns: repeat(auto-fill, minmax(96px, 1fr)); gap: 10px; }
@media (max-width: 520px) { .sw i { height: 44px; } }
.sw { border: 1px solid var(--line); border-radius: 12px; overflow: hidden; background: var(--surface); }
.sw i { display: block; height: 64px; }
.sw div { padding: 8px 10px; font-size: 13px; }
.sw b { display: block; font-weight: 600; }
.sw span { color: var(--muted); font-family: ui-monospace, monospace; font-size: 12px; }
.features { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 16px; }
.card { background: var(--surface); border: 1px solid var(--line); border-radius: 14px; padding: 18px; }
.card h3 { font-size: 16px; margin-bottom: 6px; }
.card p { margin: 0; color: var(--muted); font-size: 15px; }
.steps { display: grid; gap: 20px; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); }
.steps ol { margin: 0 0 12px; padding-left: 20px; color: var(--muted); }
.steps h3 { font-size: 16px; margin-bottom: 10px; }
.note { color: var(--muted); font-size: 14px; }
"""

HOME_CSS = """
.intro { padding: 72px 0 40px; }
.intro h1 { font-size: clamp(32px, 6vw, 52px); letter-spacing: -.01em; }
.intro p { color: var(--muted); font-size: 18px; max-width: 620px; margin: 14px 0 0; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 20px; padding-bottom: 64px; }
.tile { display: block; text-decoration: none; color: var(--text); border-radius: 16px; overflow: hidden;
  border: 1px solid var(--line); background: var(--surface); transition: transform .15s ease, border-color .15s ease; }
.tile:hover { transform: translateY(-2px); border-color: var(--accent); }
.tile .pic { aspect-ratio: 16 / 9; background: center / cover no-repeat; position: relative; }
.tile .pic img { position: absolute; left: 16px; bottom: 16px; width: 56px; height: 56px;
  filter: drop-shadow(0 6px 16px rgba(0,0,0,.35)); }
.tile .txt { padding: 14px 16px 18px; }
.tile h2 { font-size: 20px; margin: 0 0 4px; }
.badge { font-size: 12px; font-weight: 600; padding: 2px 8px; border-radius: 99px; margin-left: 6px; vertical-align: middle;
  background: color-mix(in srgb, var(--accent) 22%, transparent); color: var(--text); }
.roadmap { color: var(--muted); }
.btn.soon { border-color: color-mix(in srgb, currentColor 45%, transparent); opacity: .85; cursor: default; }
.tile p { margin: 0; color: var(--muted); font-size: 15px; }
.dots { display: flex; gap: 6px; margin-top: 12px; }
.dots i { width: 14px; height: 14px; border-radius: 50%; border: 1px solid rgba(127,127,127,.35); }
"""

SWITCH_JS = """
<script>
(function () {
  var root = document.documentElement, key = "lwbs-mode", saved = null;
  try { saved = localStorage.getItem(key); } catch (e) {}
  function set(mode, keep) {
    var m = mode || (matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark");
    root.setAttribute("data-mode", m);
    document.querySelectorAll("[data-show]").forEach(function (b) { b.setAttribute("aria-pressed", String(b.dataset.show === m)); });
    if (keep) { try { localStorage.setItem(key, m); } catch (e) {} }
  }
  set(saved);
  document.querySelectorAll("[data-show]").forEach(function (b) { b.addEventListener("click", function () { set(b.dataset.show, true); }); });
  matchMedia("(prefers-color-scheme: light)").addEventListener("change", function () { if (!saved) set(null); });
})();
</script>"""


def page(title, description, css, body, head_extra=""):
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(title)}</title>
<meta name="description" content="{E(description)}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;650;700&display=swap" rel="stylesheet">
{head_extra}<style>{css}</style>
</head>
<body>
{body}
</body>
</html>
"""


def wallpaper(pack, dest: Path, which: str) -> str | None:
    """Copy one wallpaper (1600 px wide) next to the page; None for placeholder artwork."""
    if pack.raw.get("theme", {}).get("site", {}).get("placeholder_wallpaper"):
        return None
    src = pack.root / "art" / "wallpaper" / ("images_dark" if which == "dark" else "images") / "1920x1080.jpg"
    if not src.is_file():
        return None
    name = f"wallpaper-{which}.jpg"
    Image.open(src).convert("RGB").resize((1600, 900), Image.LANCZOS).save(dest / name, quality=82, optimize=True, progressive=True)
    return name


def theme_page(pack, out: Path):
    dest = out / pack.id
    dest.mkdir(parents=True)
    dark, light = editions(pack)
    shutil.copyfile(pack.root / f"art/hicolor/scalable/apps/{pack.command}-launcher.svg", dest / "logo.svg") \
        if (pack.root / f"art/hicolor/scalable/apps/{pack.command}-launcher.svg").is_file() else \
        shutil.copyfile(pack.root / f"art/hicolor/256x256/apps/{pack.command}-launcher.png", dest / "logo.png")
    logo = "logo.svg" if (dest / "logo.svg").is_file() else "logo.png"
    walls = {m: wallpaper(pack, dest, m) for m in ("dark", "light")}
    shots = {}   # packs/<id>/art/screenshots/<dark|light>-<kde|cosmic>.jpg, shown under the hero
    for m in ("dark", "light"):
        for k in ("kde", "cosmic"):
            f = pack.root / "art" / "screenshots" / f"{m}-{k}.jpg"
            if f.is_file():
                shutil.copyfile(f, dest / f"screenshot-{m}-{k}.jpg")
                shots[(m, k)] = f"screenshot-{m}-{k}.jpg"
    def shots_html(m):
        figs = "".join(f'<figure><a href="{shots[(m, k)]}"><img src="{shots[(m, k)]}" alt="{E(pack.name)} {m} on {lab}" loading="lazy"></a>'
                       f"<figcaption>{lab}</figcaption></figure>"
                       for k, lab in (("kde", "KDE Plasma 6"), ("cosmic", "COSMIC")) if (m, k) in shots)
        return f'<div class="shots only-{m}">{figs}</div>'
    shots_block = ('<section><div class="wrap"><h2>Screenshots</h2>' + shots_html("dark") + shots_html("light")
                   + "</div></section>\n") if shots else ""
    tagline = pack.raw.get("theme", {}).get("programs", {}).get("tagline",
                                                                 f"A {pack.name} theme for KDE Plasma 6, in Dark and Light.")
    css = (BASE_CSS + THEME_CSS
           + f":root, :root[data-mode='dark'] {{ {css_vars(dark)} }}\n"
           + f"@media (prefers-color-scheme: light) {{ :root:not([data-mode='dark']) {{ {css_vars(light)} }} }}\n"
           + f":root[data-mode='light'] {{ {css_vars(light)} }}\n"
           + "".join(f":root{sel} .hero {{ background-image: url('{walls[m]}'); }}\n"
                     for m, sel in (("dark", ""), ("light", "[data-mode='light']")) if walls[m])
           + (f"@media (prefers-color-scheme: light) {{ :root:not([data-mode='dark']) .hero {{ background-image: url('{walls['light']}'); }} }}\n"
              if walls["light"] else ""))
    hero_cls = "hero" if walls["dark"] else "hero drawn"
    soon = pack.raw.get("theme", {}).get("site", {}).get("status") == "coming-soon"
    folder = f"{pack.name.replace(' ', '-')}-{pack.version}"
    slug = pack.name.replace(" ", "-")
    INSTALL_BLOCK = f"""<section><div class="wrap">
  <h2>Install</h2>
  <div class="steps">
    <div><h3>KDE Plasma 6</h3>
      <ol><li>Download <code>{E(folder)}.zip</code> and unzip it.</li><li>Run the installer: a guided setup in the terminal. Nothing changes until you press Install.</li></ol>
      <pre>cd {E(folder)}
./install.sh</pre>
      <p class="note">Afterwards, <code>{E(pack.command)} dark</code> or <code>{E(pack.command)} light</code> switches everything.</p></div>
    <div><h3>COSMIC</h3>
      <ol><li>Download <code>{E(slug)}-COSMIC-{E(pack.version)}.zip</code> (a separate download) and unzip it.</li><li>Run <code>./install.sh</code>: it puts the two theme files and the wallpapers in place. Nothing in COSMIC changes by itself.</li><li>Open COSMIC Settings › Desktop › Appearance, choose Dark or Light, then Import, and pick the matching <code>.ron</code> file.</li><li>Pick the wallpaper in Settings › Desktop › Wallpaper › Add image.</li></ol></div>
  </div>
  <h2>Needs (KDE panel)</h2>
  <p class="note">The top panel uses two widgets made by other people. {E(pack.name)} doesn't bundle or change them, so you choose how to install them. The installer checks for both and asks before it fetches anything: from the AUR if you use yay or paru, otherwise from the KDE Store, installed for your user only (no password). Or exit, install them yourself, and come back. Without them the theme still installs and the panel is plainer.</p>
  <div class="steps">
    <div><h3>Panel Colorizer</h3><p class="note">by Luis Bocanegra. Gives the panel its look (not needed for the Standard look). Arch: <code>paru -S plasma6-applets-panel-colorizer</code>. Fedora and openSUSE: <code>plasma-panel-colorizer</code> from the author's repository. Any distro: right-click the panel › Add or manage widgets › Get new widgets, or <a href="https://store.kde.org/p/2130967">the KDE Store</a>.</p></div>
    <div><h3>KVitals</h3><p class="note">by Yassine Amjad. CPU, RAM, GPU and network stats on the panel (needs lm_sensors). Arch: <code>paru -S plasma6-applets-kvitals-git</code>. Any distro: Get new widgets › KVitals, or <a href="https://github.com/yassine20011/kvitals">GitHub</a>.</p></div>
  </div>
</div></section>
"""
    SOON_BLOCK = f"""<section><div class="wrap">
  <h2>Coming soon</h2>
  <p>{E(pack.name)} is not released yet. It is still being tested on real desktops. The first release will be on <a href="{GITHUB}/releases">GitHub Releases</a>; follow the repository or <a href="{KOFI}">Ko-fi</a> to hear when it lands.</p>
</div></section>
"""

    def swatches(ed):
        return "".join(f'<div class="sw"><i style="background:{ed.roles[k]}"></i><div><b>{E(label)}</b>'
                       f'<span>{ed.roles[k]}</span></div></div>' for k, label in SWATCHES)

    body = f"""<header class="top"><div class="wrap">
  <a class="brand" href="../">The Linux Workbench <small>themes</small></a>
  <span class="spacer"></span>
  <div class="switch" role="group" aria-label="Edition"><button data-show="dark" aria-pressed="true">Dark</button><button data-show="light" aria-pressed="false">Light</button></div>
  <a class="navlink" href="../customiser/">Customiser</a> <a class="navlink" href="{GITHUB}">GitHub</a>
</div></header>
<main>
<div class="{hero_cls}"><div class="wrap">
  <img class="logo" src="{logo}" alt="{E(pack.name)} logo" width="88" height="88">
  <h1>{E(pack.name)}</h1>
  <p>{E(tagline)}</p>
  <div class="actions">
    {'<span class="btn soon">Coming soon</span>' if soon else f'<a class="btn primary" href="{GITHUB}/releases?q={E(pack.name)}">Download</a>'}
    <a class="btn ghost" href="{GITHUB}/tree/main/packs/{pack.id}">Source</a>
  </div>
  <div class="version">{'Coming soon' if soon else 'Version ' + E(pack.version)} · KDE Plasma 6 and COSMIC · {E(pack.license)}</div>
</div></div>

{shots_block}<section><div class="wrap">
  <h2>Palette</h2>
  <div class="swatches" data-for="dark">{swatches(dark)}</div>
</div></section>

<section><div class="wrap">
  <h2>What you get</h2>
  <div class="features">{''.join(f'<div class="card"><h3>{E(t)}</h3><p>{E(d)}</p></div>' for t, d in FEATURES)}</div>
</div></section>

{SOON_BLOCK if soon else INSTALL_BLOCK}
</main>
<footer><div class="wrap">{E(pack.name)} by The Linux Workbench · Code {E(pack.license)}, wallpapers all rights reserved (free to use as wallpapers) · <a href="../">All themes</a> · <a href="mailto:{CONTACT}">{CONTACT}</a> · <a href="{KOFI}">Support on Ko-fi</a></div></footer>
{SWITCH_JS}"""
    # the swatches follow the edition shown
    body = body.replace(f'<div class="swatches" data-for="dark">{swatches(dark)}</div>',
                        f'<div class="swatches only-dark">{swatches(dark)}</div><div class="swatches only-light">{swatches(light)}</div>')
    css += (".shots { display: grid; gap: 18px; } .shots figure { margin: 0; } .shots img { width: 100%; height: auto; display: block; border-radius: 10px; border: 1px solid var(--line); }\n"
            ".shots figcaption { margin-top: 6px; font-size: 13px; color: var(--muted); }\n"
            ".only-light { display: none; }\n"
            ":root[data-mode='light'] .only-light { display: grid; } :root[data-mode='light'] .only-dark { display: none; }\n"
            "@media (prefers-color-scheme: light) { :root:not([data-mode='dark']) .only-light { display: grid; }"
            " :root:not([data-mode='dark']) .only-dark { display: none; } }\n")
    (dest / "index.html").write_text(page(f"{pack.name} — The Linux Workbench",
                                          f"{pack.name}: {tagline}", css, body), encoding="utf-8")
    return {"id": pack.id, "name": pack.name, "tagline": tagline, "logo": f"{pack.id}/{logo}",
            "wall": f"{pack.id}/{walls['dark']}" if walls["dark"] else None,
            "dots": [dark.roles[k] for k in ("window_bg", "surface_raised", "accent", "text")],
            "soon": soon, "deep": dark.roles["base_bg"], "surface": dark.roles["surface_raised"], "accent": dark.roles["accent"]}


def home(cards, out: Path):
    neutral_dark = ("--bg: #15171c; --deep: #0f1115; --surface: #1d2027; --raised: #262a33; --line: #2c3039; "
                    "--text: #eef0f4; --muted: #a2a8b4; --accent: #9db8ff; --on-accent: #0f1115; --accent-rgb: 157, 184, 255;")
    neutral_light = ("--bg: #f6f6f4; --deep: #ecece8; --surface: #ffffff; --raised: #f0f0ed; --line: #e1e1dc; "
                     "--text: #1d2027; --muted: #5d6370; --accent: #3e63c9; --on-accent: #ffffff; --accent-rgb: 62, 99, 201;")
    css = (BASE_CSS + HOME_CSS + f":root {{ {neutral_dark} }}\n"
           f"@media (prefers-color-scheme: light) {{ :root {{ {neutral_light} }} }}\n")
    now = ", ".join(c["name"] for c in cards if not c["soon"])
    later = ", ".join(c["name"] for c in cards if c["soon"]) or "more themes"
    tiles = []
    for c in cards:
        bg = (f"background-image: url('{c['wall']}');" if c["wall"] else
              f"background: radial-gradient(600px 260px at 75% 0%, {c['accent']}55, transparent 60%), "
              f"linear-gradient(160deg, {c['surface']}, {c['deep']});")
        tiles.append(f"""<a class="tile" href="{c['id']}/"><div class="pic" style="{bg}"><img src="{c['logo']}" alt="" width="56" height="56"></div>
<div class="txt"><h2>{E(c['name'])}{' <span class="badge">Coming soon</span>' if c['soon'] else ''}</h2><p>{E(c['tagline'])}</p>
<div class="dots">{''.join(f'<i style="background:{d}"></i>' for d in c['dots'])}</div></div></a>""")
    body = f"""<header class="top"><div class="wrap">
  <a class="brand" href="./">The Linux Workbench <small>themes</small></a>
  <span class="spacer"></span><a class="navlink" href="customiser/">Customiser</a> <a class="navlink" href="{GITHUB}">GitHub</a>
</div></header>
<main class="wrap">
  <div class="intro"><h1>Desktop themes for workstations</h1>
  <p>Six complete themes for KDE Plasma 6 and COSMIC, each in Dark and Light: colours, apps, icons, cursors, panel, terminal and wallpapers, switched with one command.</p>
  <p class="roadmap"><b>Out now:</b> {E(now)}. <b>Coming next:</b> {E(later)}. Questions or problems? Use <a href="{GITHUB}/issues">GitHub Issues</a> the comments on KDE-look.org, or email <a href="mailto:{CONTACT}">{CONTACT}</a>.</p></div>
  <div class="grid">{''.join(tiles)}</div>
</main>
<footer><div class="wrap">The Linux Workbench · <a href="{GITHUB}">Source on GitHub</a> · <a href="{GITHUB}/issues">Report a problem</a> · <a href="mailto:{CONTACT}">{CONTACT}</a> · <a href="{KOFI}">Support on Ko-fi</a></div></footer>"""
    (out / "index.html").write_text(page("The Linux Workbench themes",
                                         "Six desktop themes for KDE Plasma 6 and COSMIC, in Dark and Light.", css, body),
                                    encoding="utf-8")


CUSTOMISER_CSS = """
.cz { display: grid; grid-template-columns: minmax(280px, 380px) 1fr; gap: 28px; align-items: start; margin: 28px 0 48px; }
@media (max-width: 820px) { .cz { grid-template-columns: 1fr; } }
.cz h1 { font-size: 34px; margin: 28px 0 6px; } .cz-lead { color: var(--muted); max-width: 70ch; }
.cz .panel { background: var(--surface); border: 1px solid var(--line); border-radius: 12px; padding: 16px; }
.cz label.sel { display: block; font-size: 13px; color: var(--muted); margin: 0 0 10px; }
.cz select { width: 100%; margin-top: 4px; padding: 8px; border-radius: 8px; border: 1px solid var(--line); background: var(--raised); color: var(--text); font: inherit; }
.cz .row { display: flex; align-items: center; gap: 10px; padding: 7px 0; border-top: 1px solid var(--line); }
.cz .row input[type=color] { width: 38px; height: 30px; border: 1px solid var(--line); border-radius: 6px; background: none; padding: 0; cursor: pointer; }
.cz .row span { flex: 1; font-size: 14px; } .cz .row code { font-size: 12px; color: var(--muted); }
.cz .warn { color: #e0a030; font-size: 13px; margin: 8px 0 0; }
.cz .btns { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 14px; }
.cz button.b { padding: 9px 14px; border-radius: 8px; border: 1px solid var(--line); background: var(--raised); color: var(--text); font: inherit; cursor: pointer; }
.cz button.b.primary { background: var(--accent); color: var(--on-accent); border-color: transparent; font-weight: 600; }
.cz .win { border-radius: 10px; overflow: hidden; border: 1px solid rgba(128,128,128,.35); margin-bottom: 18px; font-size: 14px; }
.cz .win .tb { padding: 8px 12px; font-weight: 600; } .cz .win .bd { padding: 14px; display: grid; gap: 10px; }
.cz .win .view { padding: 10px; border-radius: 6px; } .cz .win .sel { padding: 6px 10px; border-radius: 6px; display: inline-block; }
.cz .win .btn2 { padding: 6px 12px; border-radius: 6px; display: inline-block; margin-right: 8px; }
.cz .term { border-radius: 10px; padding: 14px; font: 13px/1.5 ui-monospace, "JetBrains Mono", monospace; white-space: pre; overflow: auto; }
.cz .how { font-size: 14px; color: var(--muted); } .cz .how code { background: var(--raised); padding: 1px 5px; border-radius: 4px; }
"""

CUSTOMISER_JS = r"""
const D = __DATA__;
const $ = id => document.getElementById(id);
const ROLES = [["Window","BackgroundNormal","Window background"],["View","BackgroundNormal","Content background"],
  ["Button","BackgroundNormal","Buttons"],["Header","BackgroundNormal","Title bar"],["Selection","BackgroundNormal","Accent (selection)"],
  ["Window","ForegroundNormal","Text"],["Window","ForegroundInactive","Muted text"],["Window","DecorationFocus","Focus ring"],
  ["Window","ForegroundLink","Links"],["Selection","ForegroundNormal","Text on accent"]];
let cur, map = {};
const hex = rgb => "#" + rgb.split(",").map(n => (+n).toString(16).padStart(2,"0")).join("");
const rgb = h => [1,3,5].map(i => parseInt(h.slice(i,i+2),16)).join(",");
function get(text, group, key) {
  const m = text.match(new RegExp("\\[Colors:" + group + "\\]([^\\[]*)")); if (!m) return null;
  const k = m[1].match(new RegExp("^" + key + "=(\\d+,\\d+,\\d+)", "m")); return k ? k[1] : null;
}
function apply(text) {
  return text.replace(/(=)(\d+,\d+,\d+)(?=\s|$)/g, (all, eq, c) => map[c] ? eq + map[c] : all);
}
function lum(c) { const v = c.split(",").map(n => { n/=255; return n<=.03928 ? n/12.92 : Math.pow((n+.055)/1.055,2.4); }); return .2126*v[0]+.7152*v[1]+.0722*v[2]; }
function ratio(a,b) { const x = lum(a), y = lum(b); return (Math.max(x,y)+.05)/(Math.min(x,y)+.05); }
function load() {
  cur = D[$("theme").value][$("ed").value]; map = {};
  const groups = {};   // original colour -> labels
  ROLES.forEach(([g,k,label]) => { const c = get(cur.colors, g, k); if (c) (groups[c] = groups[c] || []).push(label); });
  $("rows").innerHTML = "";
  Object.entries(groups).forEach(([c, labels]) => {
    const r = document.createElement("div"); r.className = "row";
    r.innerHTML = `<input type="color" value="${hex(c)}" aria-label="${labels.join(", ")}"><span>${labels.join(" / ")}</span><code>${hex(c)}</code>`;
    r.querySelector("input").oninput = e => { map[c] = rgb(e.target.value); r.querySelector("code").textContent = e.target.value; render(); };
    $("rows").appendChild(r);
  });
  render();
}
function render() {
  const t = apply(cur.colors), c = (g,k) => "rgb(" + get(t,g,k) + ")";
  const w = $("win"); w.style.background = c("Window","BackgroundNormal"); w.style.color = c("Window","ForegroundNormal");
  w.querySelector(".tb").style.background = c("Header","BackgroundNormal"); w.querySelector(".tb").style.color = c("Header","ForegroundNormal");
  const v = w.querySelector(".view"); v.style.background = c("View","BackgroundNormal"); v.style.color = c("View","ForegroundNormal");
  const s = w.querySelector(".sel"); s.style.background = c("Selection","BackgroundNormal"); s.style.color = c("Selection","ForegroundNormal");
  w.querySelectorAll(".btn2").forEach(b => { b.style.background = c("Button","BackgroundNormal"); b.style.color = c("Button","ForegroundNormal"); });
  w.querySelector("a").style.color = c("Window","ForegroundLink");
  const k = apply(cur.konsole), kc = n => { const m = k.match(new RegExp("\\[" + n + "\\]\\s*Color=(\\d+,\\d+,\\d+)")); return "rgb(" + (m ? m[1] : "0,0,0") + ")"; };
  const tm = $("term"); tm.style.background = kc("Background"); tm.style.color = kc("Foreground");
  tm.innerHTML = `$ <span style="color:${kc("Color2")}">ls</span> ~/themes\n<span style="color:${kc("Color4")}">waypoint</span>  <span style="color:${kc("Color3")}">natura</span>  <span style="color:${kc("Color1")}">error.log</span>\n$ <span style="color:${kc("Color5")}">echo</span> "Hello"`;
  const pairs = [["Window","ForegroundNormal","BackgroundNormal","text on window"],["View","ForegroundNormal","BackgroundNormal","text in content area"],
    ["Selection","ForegroundNormal","BackgroundNormal","text on accent"],["Button","ForegroundNormal","BackgroundNormal","text on buttons"]];
  const bad = pairs.map(([g,f,b,l]) => [l, ratio(get(t,g,f), get(t,g,b))]).filter(x => x[1] < 4.5);
  $("warn").textContent = bad.length ? "Low contrast: " + bad.map(x => x[0] + " (" + x[1].toFixed(1) + ":1, aim for 4.5 or more)").join("; ") : "";
}
function save(text, name) {
  const a = document.createElement("a"); a.href = URL.createObjectURL(new Blob([text], {type: "text/plain"})); a.download = name; a.click();
}
function download(kind) {
  const label = cur.name + " Custom";
  if (kind === "colors") {
    let t = apply(cur.colors).replace(/^ColorScheme=.*$/m, "ColorScheme=" + label.replace(/ /g, "")).replace(/^Name=.*$/m, "Name=" + label);
    save(t, label.replace(/ /g, "-") + ".colors");
  } else {
    let t = apply(cur.konsole).replace(/^Description=.*$/m, "Description=" + label);
    save(t, label.replace(/ /g, "-") + ".colorscheme");
  }
}
Object.keys(D).forEach(id => { const o = document.createElement("option"); o.value = id; o.textContent = D[id].name; $("theme").appendChild(o); });
$("theme").onchange = $("ed").onchange = () => { cur = null; load(); };
$("reset").onclick = load; $("dl-colors").onclick = () => download("colors"); $("dl-konsole").onclick = () => download("konsole");
function fixNames() { /* names per edition come from the data */ }
load();
"""


def customiser(out: Path):
    """site/customiser/: change a released theme's colours in the browser, download a KDE colour scheme and a Konsole
    scheme. Everything is built here from the engine's own output, so the files match the real themes."""
    from engine.parts.kde_colors import color_scheme
    from engine.parts.konsole import colorscheme
    data = {}
    for pid in ORDER:
        pack = load(ROOT / "packs" / pid)
        if pack.raw.get("theme", {}).get("site", {}).get("status") == "coming-soon":
            continue
        data[pid] = {"name": pack.name}
        for ed in pack.editions.values():
            data[pid][ed.id] = {"name": pack.display(ed), "colors": color_scheme(pack, ed), "konsole": colorscheme(pack, ed)}
    neutral_dark = ("--bg: #15171c; --deep: #0f1115; --surface: #1d2027; --raised: #262a33; --line: #2c3039; "
                    "--text: #eef0f4; --muted: #a2a8b4; --accent: #9db8ff; --on-accent: #0f1115; --accent-rgb: 157, 184, 255;")
    neutral_light = ("--bg: #f6f6f4; --deep: #ecece8; --surface: #ffffff; --raised: #f0f0ed; --line: #e1e1dc; "
                     "--text: #1d2027; --muted: #5d6370; --accent: #3e63c9; --on-accent: #ffffff; --accent-rgb: 62, 99, 201;")
    css = (BASE_CSS + HOME_CSS + CUSTOMISER_CSS + f":root {{ {neutral_dark} }}\n"
           f"@media (prefers-color-scheme: light) {{ :root {{ {neutral_light} }} }}\n")
    body = f"""<header class="top"><div class="wrap">
  <a class="brand" href="../">The Linux Workbench <small>themes</small></a>
  <span class="spacer"></span><a class="navlink" href="{GITHUB}">GitHub</a>
</div></header>
<main class="wrap cz-main">
<h1>Colour customiser</h1>
<p class="cz-lead">Start from a released theme, change its colours, and download a KDE colour scheme and a Konsole colour scheme of your own. It runs in your browser: nothing is uploaded. It changes colours only; icons, the panel, the Plasma Style and the wallpapers stay as in the theme.</p>
<div class="cz">
  <div class="panel">
    <label class="sel">Theme<select id="theme"></select></label>
    <label class="sel">Edition<select id="ed"><option value="dark">Dark</option><option value="light">Light</option></select></label>
    <div id="rows"></div>
    <p class="warn" id="warn"></p>
    <div class="btns"><button class="b primary" id="dl-colors">Download colour scheme</button>
    <button class="b primary" id="dl-konsole">Download Konsole scheme</button><button class="b" id="reset">Reset</button></div>
  </div>
  <div>
    <div class="win" id="win"><div class="tb">Preview: a window</div><div class="bd">
      <div class="view">Content area <a href="#" onclick="return false">a link</a></div>
      <div><span class="sel">Selected item</span></div>
      <div><span class="btn2">Button</span><span class="btn2">Another</span></div></div></div>
    <div class="term" id="term"></div>
    <p class="how"><b>Use it.</b> Colour scheme: put the file in <code>~/.local/share/color-schemes/</code>, then pick it in System Settings › Colors &amp; Themes › Colors. Konsole scheme: put the file in <code>~/.local/share/konsole/</code>, then choose it in Konsole's profile settings › Appearance.</p>
  </div>
</div>
</main>
<footer><div class="wrap">The Linux Workbench · Made with <a href="{GITHUB}">The Linux Workbench theme engine</a> · <a href="{GITHUB}/issues">Report a problem</a> · <a href="mailto:{CONTACT}">{CONTACT}</a> · <a href="{KOFI}">Support on Ko-fi</a></div></footer>
<script>{CUSTOMISER_JS.replace("__DATA__", json.dumps(data))}</script>"""
    d = out / "customiser"
    d.mkdir(parents=True)
    (d / "index.html").write_text(page("Colour customiser — The Linux Workbench",
                                       "Change a theme's colours in your browser and download your own KDE and Konsole colour schemes.",
                                       css, body), encoding="utf-8")


def build(out: Path = ROOT / "site") -> Path:
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    cards = [theme_page(load(ROOT / "packs" / pid), out) for pid in ORDER]
    home(cards, out)
    customiser(out)
    (out / ".nojekyll").write_text("")
    (out / "themes.json").write_text(json.dumps([{k: c[k] for k in ("id", "name", "tagline")} for c in cards], indent=1) + "\n")
    return out


if __name__ == "__main__":
    print("wrote", build())
