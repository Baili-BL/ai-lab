#!/usr/bin/env python3
"""Extract static inline SVGs into icons.js sprite and retarget HTML/JS to <use href="#i-…">."""
import hashlib, json, re
from pathlib import Path

ROOT = Path("/Users/kevin/WorkBuddy/2026-07-30-15-34-17")
FILES = [
    "chart-builder.html",
    "data-source.html",
    "indicator-center.html",
    "manual-data.html",
    "chart-gallery.html",
    "add-indicator-dialog.html",
]
SVG_RE = re.compile(r"<svg\b[^>]*>.*?</svg>", re.S)
ATTR_RE = re.compile(r'([\w:.-]+)="([^"]*)"')
DYN_RE = re.compile(r"""(?:'\s*\+|\+\s*'|"\s*\+|\+\s*"|`\s*\+|\$\{)""")

PREFIX_NAMES = [
    ("M3.5 2L7 5L3.5 8", "chevron-right"),
    ("M2.5 4.5L6 8L9.5 4.5", "chevron-down"),
    ("M2.5 4L5 6.5L7.5 4", "caret-down"),
    ("M6.5 2L3 5l3.5 3", "chevron-left"),
    ("M8.5 8.5L11 11", "search"),
    ("M3 4.5L6 7.5L9 4.5", "caret-down-12"),
    ("M2.5 6.2L5 8.7 9.5 3.5", "check"),
    ("M3.5 4.8h9M6.2 4.8V3.4h3.6v1.4M5 4.8v7.4h6V4.8", "trash"),
    ("M840.4 300H183.6", "caret-fill"),
    ("M1.5 5.5h11M4.5 1v3M9.5 1v3", "calendar"),
    ("M7 4.5v5M4.5 7h5", "plus-14"),
    ("M1.5 3.5a1 1 0 0 1 1-1h3l1.5 1.7h4.5", "folder"),
    ("M8 5v6M5 8h6", "plus-16"),
    ('x="1.5" y="8" width="3" height="6"', "nav-bi"),
    ("M3.5 1.5h6l3 3v10h-9z", "nav-report"),
    ("M6 14.5h4", "nav-ppt"),
    ("M2.5 12l3.5-3 2.5 2 3-3 2 2.5", "nav-gallery"),
    ("M8 1v2M8 13v2M1 8h2M13 8h2", "nav-indicator"),
    ("M1.5 6h13M6 6v7.5", "nav-table"),
    ("M2 3.5v9c0 1.1 2.7 2 6 2s6-.9 6-2v-9", "nav-datasource"),
    ("M6.5 9.5l3-3M4.5 11.5l-1.8 1.8", "nav-link"),
    ("M2 4h12M2 8h12M2 12h12", "menu"),
    ("M11.2 2.6l2.2 2.2L5.2 13H3v-2.2L11.2 2.6z", "edit"),
    ("M9.5 3.5l3 3L5.5 13H2.5v-3z", "edit-fill"),
    ("M6.5 2.5L3 6l3.5 3.5M10 2.5L6.5 6 10 9.5", "chevrons-left"),
    ("M3.2 3.2l7.6 7.6M10.8 3.2l-7.6 7.6", "close-14"),
    ("M2 13.5L6 8l3 2.5L14 4", "trend"),
    ("M6.2 9.8a2.6 2.6 0 0 1 0-3.6l1.5-1.5", "unlink"),
    ("M9 2a5 5 0 0 0-5 5v3.2L2.6 12", "bell"),
    ("M2 4.5h7M2 9.5h7M9.5 2l2.5 2.5L9.5 7", "swap"),
    ("M7 2v7M4.5 6.5 7 9l2.5-2.5M2.5 11.5h9", "download"),
    ("M4 3.5h8v9H4z", "copy"),
    ("M3 5h8M3 11h8M11 2.5l2.5 2.5L11 7.5", "swap-16"),
    ("M836.032 131.392", "close-1024"),
    ("M396.8 896h550.4", "rte-indent"),
    ("M923.136 43.739429", "rte-image"),
    ("M76.8 552h870.4", "rte-hr"),
    ("M517.771636 41.890909", "rte-field"),
    ("M599.625143 676.132571", "rte-clear"),
    ("M697.8 481.4c33.6-35", "rte-bold"),
    ("M798 160H366c-4.4 0-8 3.6-8 8v64", "rte-italic"),
    ("M824 804H200c-4.4 0-8 3.4-8 7.6v60.8", "rte-underline"),
    ("M904 816H120c-4.4 0-8 3.6-8 8v80", "rte-font-color"),
    ("M766.4 744.3c43.7 0 79.4-36.2", "rte-highlight"),
    ("M120 230h496c4.4 0 8-3.6 8-8v-56", "rte-align"),
    ("M912 192H328c-4.4 0-8 3.6-8 8v56", "rte-ul"),
    ("M920 760H336c-4.4 0-8 3.6-8 8v56", "rte-ol"),
    ("M574 665.4a8.03 8.03 0 00-11.3 0", "rte-link"),
    ("M928 160H96c-17.7 0-32 14.3-32 32v640", "rte-table"),
    ("M840 836H184c-4.4 0-8 3.6-8 8v60", "rte-line-height"),
    ("M512 64C264.6 64 64 264.6 64 512", "info-circle"),
    ("M947.2 128a12.8 12.8 0 0 1 12.8 12.8v742.4", "line-type"),
    ("M8 1.5l1.2 3.2L12.5 6 9.2 7.3 8 10.5", "sparkle"),
    ("M8 3v10M3 8h10", "plus"),
    ("M2.5 3.5h5.5M2.5 8h5.5M2.5 12.5h5.5M11 4.5 8.5 8 11 11.5", "panel-collapse"),
    ("M8 1.5l1.1 2.9L12 5.5 9.1 6.6 8 9.5", "ai-spark"),
    ("M3 8h9M8.5 4.5 12.5 8l-4 3.5", "send"),
    ("M3 4.5h10M3 8h10M3 11.5h7", "filter"),
    ("M8.5 3 4.5 7l4 4", "back"),
    ("M2 3.5h10M4 3.5v7.5M10 3.5v7.5M2 11h10", "excel"),
    ("M3.5 3.5l7 7M10.5 3.5l-7 7", "close"),
    ("M9.3 9.3 12 12", "search-14"),
    ('cx="7" cy="3.2" r="1.1"', "more"),
    ("M6 2v8M2 6h8", "plus-12"),
    ("M2 9.5L5 5.5l2 1.8L10 3", "mini-chart"),
    ("M2.2 1.6h7.6c.7 0 1.2.5 1.2 1.2v4.4", "monitor"),
    ("M7.5 2.5L4 6l3.5 3.5", "chevron-left-12"),
    ("M0.6.4h6.8L4 5.6z", "caret-tiny"),
    ("M2 12.5L6 7l3 2.5L14 4", "chart-line"),
    ("M2 12.5L6 7l3 2.5L14 4v8.5H2z", "chart-area"),
    ("M2 13l3-3 3 2 6-5v6H2z", "chart-stack-area"),
    ("M2 14h12V3.5L10 7 7 5.5 2 9.5V14z", "chart-stack-pct"),
    ('x="2" y="7" width="3" height="7"', "chart-bar"),
    ('x="2.5" y="8.5" width="4" height="5.5"', "chart-stack-col"),
    ('x="2" y="2.5" width="9" height="3"', "chart-hbar"),
    ("M8 2a6 6 0 1 0 6 6H8V2z", "chart-pie"),
    ('cx="4" cy="11" r="1.6"', "chart-scatter"),
    ("M2 6l4-2.5L9.5 5 14 2", "chart-combo"),
    ("M3 16.5l5.2-6.2 3.6 2.8L21 5.5", "vis-line"),
    ("M3 18l5.2-6.2 3.6 2.8L21 6.2V18H3z", "vis-area"),
    ("M3 18l4.2-3.2 4.6 2 9.2-5.4V18H3z", "vis-stack-area"),
    ("M3 19h18V5.2L15 9.4 11.2 7.6 3 12.2V19z", "vis-stack-pct"),
]


def parse_open_attrs(svg):
    open_tag = svg[: svg.find(">") + 1]
    return dict(ATTR_RE.findall(open_tag)), open_tag


def inner_html(svg):
    inner = re.sub(r"^<svg\b[^>]*>", "", svg, count=1)
    inner = re.sub(r"</svg>\s*$", "", inner)
    return inner.strip()


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def is_dynamic(svg):
    return bool(DYN_RE.search(svg))


def is_use_wrapper(svg):
    inner = inner_html(svg)
    return inner.startswith("<use ") and "<path" not in inner and "<rect" not in inner


def fingerprint(inner, vb, fill):
    return hashlib.md5(f"{vb}|{fill}|{norm(inner)}".encode()).hexdigest()


def pick_name(inner, used):
    blob = norm(inner)
    base = None
    for prefix, name in PREFIX_NAMES:
        if prefix in blob:
            base = name
            break
    if not base:
        base = "g-" + hashlib.md5(blob.encode()).hexdigest()[:8]
    name = base
    i = 2
    while name in used:
        name = f"{base}-{i}"
        i += 1
    used.add(name)
    return name


def collect(files_text):
    used = set()
    icons = {}  # fp -> {name, vb, fill, inner}
    order = []
    for text in files_text:
        for m in SVG_RE.finditer(text):
            raw = m.group(0)
            if is_dynamic(raw) or is_use_wrapper(raw):
                continue
            attrs, _ = parse_open_attrs(raw)
            inner = inner_html(raw)
            if not inner or "' +" in inner or '" +' in inner:
                continue
            if re.search(r"</?(?:button|span|div|header|nav|svg)\b", inner, re.I):
                continue
            vb = attrs.get("viewBox", "0 0 16 16")
            fill = attrs.get("fill", "")
            fp = fingerprint(inner, vb, fill)
            if fp not in icons:
                name = pick_name(inner, used)
                extra = []
                for k in ("stroke", "stroke-width", "stroke-linecap", "stroke-linejoin"):
                    if k in attrs:
                        extra.append(f'{k}="{attrs[k]}"')
                icons[fp] = {
                    "name": name,
                    "vb": vb,
                    "fill": fill,
                    "inner": inner,
                    "extra": " ".join(extra),
                }
                order.append(fp)
    return icons, order


def to_use_tag(raw, name):
    attrs, open_tag = parse_open_attrs(raw)
    keep = []
    cls = attrs.get("class", "").strip()
    classes = (cls + " i").strip() if cls else "i"
    keep.append(f'class="{classes}"')
    for k in ("width", "height", "style", "title", "role", "id", "aria-label", "aria-hidden", "opacity"):
        if k in attrs and k != "class":
            keep.append(f'{k}="{attrs[k]}"')
    if "aria-hidden" not in attrs and "aria-label" not in attrs:
        keep.append('aria-hidden="true"')
    return "<svg " + " ".join(keep) + f'><use href="#i-{name}"></use></svg>'


def replace_in_text(text, icons):
    def repl(m):
        raw = m.group(0)
        if is_dynamic(raw) or is_use_wrapper(raw):
            return raw
        attrs, _ = parse_open_attrs(raw)
        inner = inner_html(raw)
        if not inner:
            return raw
        vb = attrs.get("viewBox", "0 0 16 16")
        fill = attrs.get("fill", "")
        fp = fingerprint(inner, vb, fill)
        if fp not in icons:
            return raw
        return to_use_tag(raw, icons[fp]["name"])

    return SVG_RE.sub(repl, text)


def ensure_script(text):
    if re.search(r'<script[^>]+src=["\']icons\.js["\']', text):
        return text
    return re.sub(r"(<body[^>]*>)", r'\1\n<script src="icons.js"></script>', text, count=1, flags=re.I)


def build_sprite(icons, order):
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" id="icon-sprite" style="position:absolute;width:0;height:0;overflow:hidden" aria-hidden="true">'
    ]
    for fp in order:
        ic = icons[fp]
        fill_attr = f' fill="{ic["fill"]}"' if ic["fill"] else ""
        extra = f' {ic["extra"]}' if ic["extra"] else ""
        parts.append(f'<symbol id="i-{ic["name"]}" viewBox="{ic["vb"]}"{fill_attr}{extra}>{ic["inner"]}</symbol>')
    parts.append("</svg>")
    return "".join(parts)


def main():
    texts = []
    for fn in FILES:
        texts.append((fn, (ROOT / fn).read_text(encoding="utf-8")))

    icons, order = collect([t for _, t in texts])
    sprite = build_sprite(icons, order)

    js = (
        "/* Shared SVG sprite. Pages load this first in <body>; icons use <use href=\"#i-name\">. */\n"
        "(function(){\n"
        "  document.write(" + json.dumps(sprite, ensure_ascii=False) + ");\n"
        "  window.icon = function(name, w, h){\n"
        "    w = w || 16; h = h || w;\n"
        "    return '<svg class=\"i\" width=\"'+w+'\" height=\"'+h+'\" aria-hidden=\"true\"><use href=\"#i-'+name+'\"></use></svg>';\n"
        "  };\n"
        "})();\n"
    )
    (ROOT / "icons.js").write_text(js, encoding="utf-8")

    for fn, text in texts:
        new = ensure_script(replace_in_text(text, icons))
        (ROOT / fn).write_text(new, encoding="utf-8")

    link = ROOT / "static-html/b00318272f13c358/icons.js"
    if link.exists() or link.is_symlink():
        link.unlink()
    link.symlink_to("../../icons.js")

    print("icons", len(order))
    print("names", ", ".join(icons[fp]["name"] for fp in order[:40]), "...")
    leftover = 0
    for fn in FILES:
        t = (ROOT / fn).read_text(encoding="utf-8")
        for m in SVG_RE.finditer(t):
            raw = m.group(0)
            if is_dynamic(raw) or is_use_wrapper(raw):
                continue
            leftover += 1
            print(" leftover", fn, raw[:80].replace("\n", " "))
    print("leftover_static", leftover)


if __name__ == "__main__":
    main()
