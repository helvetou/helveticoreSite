# Helveticore — Site statique

Site web de **Helveticore OÜ** (Tallinn, Estonie). Statique, sans framework ni étape de
build : HTML + CSS + JavaScript uniquement, prêt à être publié tel quel sur
**Cloudflare Pages**.

Le contenu reflète l'état courant du référentiel [`../EdgeStream-GW`](../EdgeStream-GW)
à la date de génération. Aucune donnée n'est inventée : les fiches projet, KPIs, exigences,
décisions et jalons sont extraits de ce dépôt.

## Structure

```text
.
├── index.html                     Accueil (entreprise, triptyque, état courant, contact)
├── methode.html                   Méthodologie CMMI Level 3
├── projet-edgestream-gw.html      EdgeStream-GW — état courant détaillé
├── projet-fog-crypto-core.html    Fog-Crypto Core
├── projet-netsentry-iot.html      NetSentry-IoT
├── assets/
│   ├── css/style.css              Feuille de style unique (design « Swiss minimal », sombre auto)
│   └── js/main.js                 JS léger : nav mobile, thème, année (progressive enhancement)
├── favicon.svg                    Favicon
├── robots.txt                     Robots + pointeur de sitemap
├── sitemap.xml                    Sitemap (domaine helveticore.ee)
└── _headers                       En-têtes de sécurité / cache (Cloudflare Pages)
```

## Aperçu local

Aucun build requis. Servir le dossier avec un simple serveur statique :

```bash
cd helveticoreSite
python3 -m http.server 8000
# puis ouvrir http://localhost:8000
```

Le JavaScript est entièrement optionnel : le site reste navigable sans JS
(navigation, contenu et liens fonctionnent). Le mode sombre suit `prefers-color-scheme`
et propose un basculement manuel persistant.

## Déploiement sur Cloudflare Pages

Deux options, toutes deux sans configuration serveur :

### Option A — Connexion Git (recommandée)

1. Pousser ce dossier dans un dépôt Git (GitHub / GitLab).
2. Dans le tableau de bord Cloudflare : **Workers & Pages → Create → Pages → Connect to Git**.
3. Sélectionner le dépôt, la branche de production, puis :
   - **Build command** : *(laisser vide)*
   - **Build output directory** : `/` (racine du dépôt)
4. Déployer. Le fichier `_headers` est appliqué automatiquement.

### Option B — Téléversement direct

```bash
npm install -g wrangler
wrangler pages deploy . --project-name=helveticore
```

### Domaine

Ajouter le domaine `helveticore.ee` (ou un sous-domaine `*.pages.dev`) dans
**Pages → Custom domains**, puis suivre les instructions DNS.

## Maintenir le site à jour

Le site décrit l'état du portfolio. Quand le référentiel `EdgeStream-GW` évolue,
mettre à jour en priorité :

- les badges de statut (`Phase : …`) sur chaque page projet ;
- la section « État actuel du référentiel » de `index.html` ;
- les KPIs, jalons et décisions si de nouveaux artefacts CMMI sont rédigés.

Toute modification de contenu doit rester fidèle au dépôt source — c'est la règle de
transparence du site.
