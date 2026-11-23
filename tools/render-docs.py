#!/usr/bin/env python3
"""Render docs/edgestream-gw/*.md into styled HTML previews.

Self-contained (no external markdown library). Re-run whenever the source
markdown documents change: it overwrites each matching .html next to its .md.
"""
import html as _html
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs" / "edgestream-gw"

HEADER = """<header class="site-header">
  <div class="container header-inner">
    <a class="brand" href="../../index.html" aria-label="Helveticore — home">
      <span class="brand-mark" aria-hidden="true">◈</span>
      <span class="brand-name">Helveticore</span>
      <span class="brand-sub">Consulting · IoT · IIoT</span>
    </a>
    <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-nav">
      <span class="nav-toggle-label">Menu</span>
      <span class="nav-toggle-icon" aria-hidden="true"></span>
    </button>
    <nav class="site-nav" id="site-nav" aria-label="Main navigation">
      <ul>
        <li><a href="../../index.html">Home</a></li>
        <li><a href="../../projet-edgestream-gw.html">EdgeStream-GW</a></li>
        <li><a href="../../projet-smart-maintenance.html">Smart Maintenance</a></li>
        <li><a href="../../projet-netsentry-iot.html">NetSentry-IoT</a></li>
        <li><a href="../../projet-fog-crypto-core.html">Fog-Crypto</a></li>
        <li><a href="../../blog/index.html">Blog</a></li>
        <li><a href="../../methode.html">Method</a></li>
        <li><a href="../../documentation.html" aria-current="page">Docs</a></li>
      </ul>
    </nav>
    <button class="theme-toggle" type="button" aria-label="Toggle theme (light / dark)">
      <svg class="icon-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>
      <svg class="icon-moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>
    </button>
  </div>
</header>"""

FOOTER = """<footer class="site-footer">
  <div class="container">
    <div class="footer-grid">
      <div class="footer-col">
        <h3>Helveticore OÜ</h3>
        <p class="muted">Technology consulting for industrial IoT &amp; IIoT — edge gateways, smart maintenance and edge security. Registered in Tallinn
          (Estonia).</p>
        <p class="faint">Registry: 17526982 · Founded in 2026</p>
      </div>
      <div class="footer-col">
        <h3>Contact</h3>
        <ul>
          <li>Harju county, Tallinn,<br>Kesklinn district,<br>Tartu mnt 67/1-13b, 10115</li>
        </ul>
      </div>
      <div class="footer-col">
        <h3>Navigation</h3>
        <ul>
          <li><a href="../../index.html">Home</a></li>
          <li><a href="../../projet-edgestream-gw.html">EdgeStream-GW</a></li>
          <li><a href="../../projet-smart-maintenance.html">Smart Maintenance</a></li>
          <li><a href="../../projet-netsentry-iot.html">NetSentry-IoT</a></li>
          <li><a href="../../projet-fog-crypto-core.html">Fog-Crypto Core</a></li>
          <li><a href="../../blog/index.html">Blog</a></li>
          <li><a href="../../methode.html">Method</a></li>
          <li><a href="../../documentation.html">Documentation</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <span><span id="year">2026</span> Helveticore OÜ — Tallinn, Estonia.</span>
      <span>Static HTML/CSS/JS site · Cloudflare Pages</span>
    </div>
  </div>
</footer>

<script src="../../assets/js/main.js"></script>"""


# --------------------------------------------------------------------------
# Inline formatting
# --------------------------------------------------------------------------
_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")

# Source-repo document names -> published file names (same folder).
_LINK_MAP = {
    "REQ-11nov2026": "EdgeStreamGWREQ-11nov2026",
    "RTM-11nov2026": "EdgeStreamGWRTM-11nov2026",
    "SDD-11nov2026": "EdgeStreamGWSDD-11nov2026",
    "decision-log-11nov2026": "EdgeStreamGWdecision-log-11nov2026",
    "decision-log": "EdgeStreamGWdecision-log-11nov2026",
    "SBOM-11nov2026": "EdgeStreamGWSBOM-11nov2026",
    "volume_reduction_report-11nov2026": "EdgeStreamGWvolume_reduction_report-11nov2026",
    "tutorial-milestone-1-11nov2026": "EdgeStreamGWtutorial-milestone-1-11nov2026",
    "RTM": "EdgeStreamGWRTM-11nov2026",
}


def _inline(text: str) -> str:
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)

    def link_repl(m):
        label = m.group(1)
        url = m.group(2)
        stem = pathlib.PurePosixPath(url.split("#")[0].split("?")[0]).stem
        if stem in _LINK_MAP:
            url = _LINK_MAP[stem] + ".html"
        elif url.endswith(".md"):
            url = url[:-3] + ".html"
        if url.startswith(("http://", "https://")):
            return f'<a href="{url}" target="_blank" rel="noopener">{label}</a>'
        if url.endswith(".html"):
            return f'<a href="{url}">{label}</a>'
        # relative non-document reference (e.g. source-repo data file): keep the
        # text but do not emit a dead link on the published site.
        return f"<code>{label}</code>"

    text = _LINK_RE.sub(link_repl, text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", text)
    return text


# --------------------------------------------------------------------------
# Block parsing
# --------------------------------------------------------------------------
_UL_RE = re.compile(r"^[-*+]\s+")
_OL_RE = re.compile(r"^\d+[.)]\s+")
_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
_HR_RE = re.compile(r"^(-{3,}|\*{3,}|_{3,})$")
_SEP_CELL_RE = re.compile(r"^:?-{3,}:?$")


def _is_list(s):
    return bool(_UL_RE.match(s) or _OL_RE.match(s))


def _is_ol(s):
    return bool(_OL_RE.match(s))


def _indent(raw):
    return len(raw) - len(raw.lstrip())


def _split_row(s):
    s = s.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    return [c.strip() for c in s.split("|")]


def _is_table_sep(s):
    if "|" not in s:
        return False
    cells = _split_row(s)
    return bool(cells) and all(_SEP_CELL_RE.match(c) for c in cells)


def _is_block_start(line):
    s = line.strip()
    if not s:
        return True
    if s.startswith("```"):
        return True
    if _HEADING_RE.match(s):
        return True
    if _HR_RE.match(s):
        return True
    if s.startswith(">"):
        return True
    if _is_list(s):
        return True
    return False


def _parse_list(lines, i, indent):
    ordered = _is_ol(lines[i].strip())
    tag = "ol" if ordered else "ul"
    items = []

    while i < len(lines):
        raw = lines[i]
        s = raw.strip()
        if not s:
            break
        cur_indent = _indent(raw)
        if cur_indent < indent:
            break

        if cur_indent == indent and _is_list(s):
            if _is_ol(s) != ordered:
                break
            if ordered:
                content = _OL_RE.sub("", s)
            else:
                content = _UL_RE.sub("", s)
            i += 1

            inner = []
            while i < len(lines) and lines[i].strip():
                nxt = lines[i]
                ns = nxt.strip()
                n_indent = _indent(nxt)
                if n_indent > indent:
                    if _is_list(ns):
                        sub_html, i = _parse_list(lines, i, n_indent)
                        inner.append(sub_html)
                        continue
                    inner.append(_inline(ns))
                    i += 1
                    continue
                break

            item_html = _inline(content)
            if inner:
                item_html += "\n" + "\n".join(inner)
            items.append(f"<li>{item_html}</li>")
        elif cur_indent > indent:
            # stray deeper non-marker text: attach to last item
            if items:
                items[-1] = items[-1][:-5] + _inline(s) + "</li>"
            i += 1
        else:
            break

    body = "\n".join(items)
    return f"<{tag}>\n{body}\n</{tag}>", i


def render_md(md: str) -> str:
    lines = md.split("\n")
    out = []
    i = 0
    n = len(lines)

    while i < n:
        s = lines[i].strip()

        if not s:
            i += 1
            continue

        # fenced code block
        if s.startswith("```"):
            lang = s[3:].strip()
            i += 1
            buf = []
            while i < n and not lines[i].strip().startswith("```"):
                buf.append(lines[i])
                i += 1
            i += 1  # skip closing fence
            code = "\n".join(buf).strip("\n")
            cls = f' class="language-{lang}"' if lang else ""
            out.append(f"<pre><code{cls}>{_html.escape(code)}</code></pre>")
            continue

        # table
        if "|" in s and i + 1 < n and _is_table_sep(lines[i + 1].strip()):
            header = _split_row(s)
            i += 2
            rows = []
            while i < n and lines[i].strip() and "|" in lines[i]:
                rows.append(_split_row(lines[i].strip()))
                i += 1
            thead = "<thead><tr>" + "".join(f"<th>{_inline(c)}</th>" for c in header) + "</tr></thead>"
            tbody = "<tbody>" + "".join(
                "<tr>" + "".join(f"<td>{_inline(c)}</td>" for c in r) + "</tr>" for r in rows
            ) + "</tbody>"
            out.append(f'<div class="table-wrap"><table>{thead}{tbody}</table></div>')
            continue

        # heading
        m = _HEADING_RE.match(s)
        if m:
            level = len(m.group(1))
            out.append(f"<h{level}>{_inline(m.group(2))}</h{level}>")
            i += 1
            continue

        # horizontal rule
        if _HR_RE.match(s):
            out.append("<hr>")
            i += 1
            continue

        # blockquote
        if s.startswith(">"):
            buf = []
            while i < n and lines[i].strip().startswith(">"):
                buf.append(lines[i].strip()[1:].strip())
                i += 1
            out.append("<blockquote>" + _inline(" ".join(buf)) + "</blockquote>")
            continue

        # list
        if _is_list(s):
            html, i = _parse_list(lines, i, _indent(lines[i]))
            out.append(html)
            continue

        # paragraph
        buf = []
        while i < n and lines[i].strip() and not _is_block_start(lines[i]):
            buf.append(lines[i].strip())
            i += 1
        out.append("<p>" + _inline(" ".join(buf)) + "</p>")

    return "\n".join(out)


# --------------------------------------------------------------------------
# Page generation
# --------------------------------------------------------------------------
def _first_heading(md: str) -> str:
    for line in md.split("\n"):
        m = _HEADING_RE.match(line.strip())
        if m:
            return m.group(2)
    return "Document"


def build_page(stem: str, md: str) -> str:
    title = _first_heading(md)
    content = render_md(md)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title} · Helveticore Docs</title>
  <meta name="description" content="EdgeStream-GW technical document — {title}, rendered from the source markdown.">
  <link rel="icon" href="../../favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="../../assets/css/style.css">
</head>
<body>
{HEADER}

<main>
  <section class="section">
    <div class="container">
      <div class="doc">
        <a class="article-back" href="../../documentation.html">← Back to documentation</a>
{content}
        <p class="faint doc-source">Source: <a href="{stem}.md">raw markdown</a> — published as-is from the source repository.</p>
      </div>
    </div>
  </section>
</main>

{FOOTER}
</body>
</html>
"""


def main():
    md_files = sorted(DOCS.glob("*.md"))
    for p in md_files:
        md = p.read_text(encoding="utf-8")
        html = build_page(p.stem, md)
        out = p.with_suffix(".html")
        out.write_text(html, encoding="utf-8")
        print(f"rendered {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
