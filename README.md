# Helveticore — Static site

Website for **Helveticore OÜ** (Tallinn, Estonia). Static, framework-free, no build step:
plain HTML + CSS + JavaScript only, ready to be published as-is on **Cloudflare Pages**.

The site positions Helveticore as an **IoT & IIoT** consultancy: edge gateways
(EdgeStream-GW), industrial AI for smart maintenance, IIoT security (NetSentry-IoT) and FPGA
acceleration (Fog-Crypto Core). Project content is extracted from the source repositories —
nothing is invented.

## Structure

```text
.
├── index.html                        Home (IoT & IIoT positioning, use cases, contact)
├── methode.html                      CMMI Level 3 methodology
├── projet-edgestream-gw.html         EdgeStream-GW — IoT gateway & edge analytics
├── projet-smart-maintenance.html     Smart Maintenance — industrial AI (showcase)
├── projet-fog-crypto-core.html       Fog-Crypto Core — FPGA accelerator
├── projet-netsentry-iot.html         NetSentry-IoT — cybersecurity probe
├── documentation.html                Technical reports & source documents
├── blog/                             Blog — technical notes, LinkedIn-style
│   ├── index.html                    Article index
│   └── <slug>.html                   Individual articles
├── assets/
│   ├── css/style.css                 Single stylesheet ("Swiss minimal" design, auto dark mode)
│   └── js/main.js                    Lightweight JS: mobile nav, theme, year (progressive enhancement)
├── docs/
│   └── edgestream-gw/                Published EdgeStream-GW documents (11/2026 snapshots)
├── favicon.svg                       Favicon
├── robots.txt                        Robots + sitemap pointer
├── sitemap.xml                       Sitemap (helveticore.com domain)
└── _headers                          Security / cache headers (Cloudflare Pages)
```

## Local preview

No build required. Serve the folder with a simple static server:

```bash
cd helveticoreSite
python3 -m http.server 8000
# then open http://localhost:8000
```

JavaScript is entirely optional: the site remains navigable without JS (navigation, content
and links work). Dark mode follows `prefers-color-scheme` and offers a persistent manual
toggle.

## Deploying to Cloudflare Pages

Two options, both without server configuration:

### Option A — Git connection (recommended)

1. Push this folder to a Git repository (GitHub / GitLab).
2. In the Cloudflare dashboard: **Workers & Pages → Create → Pages → Connect to Git**.
3. Select the repository and the production branch, then:
   - **Build command**: *(leave empty)*
   - **Build output directory**: `/` (repository root)
4. Deploy. The `_headers` file is applied automatically.

### Option B — Direct upload

```bash
npm install -g wrangler
wrangler pages deploy . --project-name=helveticore
```

### Domain

Add the `helveticore.com` domain (or a `*.pages.dev` subdomain) in
**Pages → Custom domains**, then follow the DNS instructions.

## Keeping the site up to date

The site describes the state of the portfolio. When a source repository evolves, update in
priority:

- the status badges (`Phase: …`) on each project page;
- the KPIs, milestones and decisions when new CMMI artifacts are written;
- the published documents in `docs/edgestream-gw/` (snapshots are dated);
- the blog articles when a build reaches a new, verifiable milestone.

Any content change must stay faithful to the source repository — that is the site's
transparency rule.
