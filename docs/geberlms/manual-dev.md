# Manuel de test — GeberLMS v0.1.0

Test manuel de la version 0.1.0 en environnement **local** (D1 locale via Wrangler).

---

## 1. Prérequis

- Node ≥ 20, npm ≥ 9
- Dépôt cloné + `npm install` effectué

## 2. Mise en place de la base locale

Exécuter dans l'ordre, à la racine du dépôt :

```bash
# 1. appliquer toutes les migrations (0001 → 0006)
for f in migrations/*.sql; do npx wrangler d1 execute DB --local --file "$f"; done

# 2. créer l'admin
SEED_ADMIN_EMAIL=admin@example.com SEED_ADMIN_PASSWORD=changeme npx tsx scripts/seed-admin.ts

# 3. créer les données de démo (tuteur + apprenant + 1 cours + 1 inscription)
npx tsx scripts/seed-demo.ts
```

## 3. Démarrage

```bash

npm run dev
```

Ouvrir : **http://localhost:5173**

## 4. Comptes de test

- **Admin** — `admin@example.com` / `changeme`
- **Tuteur** — `tutor@demo.ee` / `DemoTutor123!`
- **Apprenant** — `learner@demo.ee` / `DemoLearner123!`

> ⚠️ Ces mots de passe sont volontairement faibles (démo, dépôt public). Ne pas réutiliser en production.

## 5. Vérifications automatiques (optionnel)

```bash
npm test            # 206 tests domaine (Vitest)
npm run typecheck   # typage de la logique métier pure (tsconfig.domain.json)
npm run check       # svelte-check (typage app + serveur, tsconfig.json)
npm run build       # build adapter-cloudflare
```

> Note : `tsconfig.json` (racine) étend `.svelte-kit/tsconfig.json` et couvre l'app
> (Svelte + serveur). `tsconfig.domain.json` couvre uniquement `src/lib/domain` + `tests`.

## 5.1 Frontend — shadcn-svelte + Tailwind v4

- UI construite sur **shadcn-svelte** (primitives `bits-ui`) + **Tailwind CSS v4** (config
  CSS-first dans `src/app.css` via `@theme` — pas de `tailwind.config.ts`).
- `components.json` : base `stone`, style `nova`, icônes `lucide`, alias `$lib`.
- Composants générés dans `src/lib/components/ui/` (38 composants) — ajout :
  `npx shadcn-svelte@latest add <composant>`.
- Derniers ajouts : `carousel` (embla-carousel-svelte), `chart` (layerchart),
  `calendar`, `resizable` (paneforge), `toggle`.
- Polices : Inter Variable (`--font-sans`) + Sora (`--font-display`) via Fontsource.
- Thème clair/sombre via `mode-watcher` (variante `.dark`).
- Layout App Shell (Sidebar + Topbar) dans `src/lib/components/layout/`.

---

## 6. Scénarios de test

### 6.1 Global / transversal

- Se connecter, puis vérifier l'aiguillage par rôle :
  - admin → `/admin/courses`
  - tuteur → `/tutor`
  - apprenant → `/learner`
- **Langue** : sélecteur en haut à droite — FR / EN / AR / DE.
  - En **arabe**, l'interface passe en **RTL** (direction droite→gauche).
- **Thème** : bascule clair/sombre (icône soleil/lune dans la topbar).
- **Sidebar** : navigation adaptée au rôle (items différents admin/tuteur/apprenant).
- **Déconnexion** : menu avatar (en haut à droite) → « Déconnexion » → retour `/login`.
- **Erreur de connexion** : identifiants invalides → alerte rouge sur la page login.

### 6.2 Admin — Gestion des cours (`/admin/courses`)

- Créer un cours : titre, slug, langue (fr/en/ar/de), prix **en centimes** (0 = gratuit).
- Renommer, **masquer/afficher** (visibilité), supprimer un cours.
- Dans un cours : ajouter des **modules** (titre + position), des **leçons** (type video / text / quiz), des **ressources** (titre).
- Renommer / masquer / supprimer modules, leçons, ressources.
- La suppression d'un cours avec des inscriptions est refusée (message d'erreur).

### 6.3 Admin — Utilisateurs (`/admin/users`)

- Créer un compte : email, nom, mot de passe, rôle (apprenant / tuteur), option « self-payer ».
- Rappel FR-03 : pas d'inscription publique — seul l'admin crée les comptes.

### 6.4 Admin — Inscription (`/admin/enroll`)

- Inscrire un apprenant (par son email) à un cours.
- Coupon optionnel : le prix affiché intègre remise + TVA.

### 6.5 Admin — Coupons (`/admin/coupons`)

- Créer un coupon : code, type (**%** ou **montant**), valeur, date d'expiration, nombre max d'utilisations.
- Lister les coupons, activer/désactiver.

### 6.6 Admin — Paiements (`/admin/payments`)

- Lister les inscriptions et paiements.
- « Marquer comme payé (Payoneer) » → confirme le paiement et génère un numéro de facture (TVA).

### 6.7 Admin — Quiz (`/admin/quizzes`)

- Lister les leçons de type **quiz** (avec leur cours/module).
- Ajouter une question : énoncé, réponses (une par ligne), index de la bonne réponse (0 = première), points.
- « Générer (IA) » : génération de questions via Workers AI (nécessite le binding `AI`).

### 6.8 Tuteur (`/tutor`)

- Tableau de bord : liste des apprenants **financés** (liens de tutelle) et leur progression par cours/leçon.

### 6.9 Apprenant (`/learner`)

- Tableau de bord : cours inscrits, leçons et progression (x/y leçons).
- « Marquer comme terminé » sur une leçon → met à jour la progression.
- Répondre à un **quiz** (QCM) → score affiché (correct/total + %).
- **Upload** de documents (stockage R2), rattachés optionnellement à une leçon.

---

## 7. Données de démo incluses (`seed-demo.ts`)

- Utilisateurs : `tutor@demo.ee` (tuteur), `learner@demo.ee` (apprenant).
- 1 lien de tutelle tuteur → apprenant.
- 1 cours « Français débutant » (fr, 100,00 € HT, public), 1 module, 1 leçon (type **text**), 1 inscription active.

> Le seed de démo ne contient **pas** de quiz : pour tester le quiz apprenant, créer d'abord une leçon de type `quiz` + des questions côté admin (6.7).

---

## 8. Limitations connues de la v0.1.0

- **Refonte frontend en cours** (blueprint validé 2026-10-09) : catalogue public,
  lecteur de cours et dashboard apprenant à implémenter sur la base des composants
  shadcn-svelte générés (38 composants, dont carousel/chart/calendar/resizable/toggle).
- Le lien **« Catalogue »** de la sidebar apprenant pointe vers `/catalog`, route
  **pas encore créée** → 404 (prévue dans le blueprint, à venir).
- Seule la page **login** a le design shadcn « premium » ; les autres pages sont encore
  l'ancien markup (à l'intérieur du nouveau shell sidebar/topbar).
- Les champs catalogue ajoutés en base (migration 0006 : description, vignette, catégorie,
  niveau, visibilité publique, tuteur) ne sont **pas encore exposés** dans l'UI admin.
- **Non implémenté** : anti-copie (NFR-10), RGPD (NFR-08 : consentement/effacement),
  suivi budget LLM (NFR-06).
- La génération de quiz par IA (Workers AI) peut entraîner des coûts et nécessite
  l'accès au binding `AI`.
