# LMS Helveticore

Learning Management System pour vendre les cours produits par Helveticore OÜ (Estonie).

## Statut

- Socle TDD en place : logique métier pure testée (prix/TVA/coupons, rôles, guardianship,
  inscriptions, catalogue de cours, auth).
- Application SvelteKit scaffoldée (adapter-cloudflare), schéma D1 et auth serveur en place.

## Prérequis

- Node ≥ 20, npm ≥ 9

## Commandes

```bash
npm install        # installer les dépendances
npm run dev        # serveur de dev
npm run build      # build SvelteKit (adapter-cloudflare)
npm run check      # svelte-check (typage de l'app et du serveur)
npm test           # tests Vitest (logique métier)
npm run test:watch
npm run typecheck  # typage de la logique métier (tsc)
```

## Base de données locale (D1)

```bash
npx wrangler d1 execute DB --local --file migrations/0001_init.sql
npx wrangler d1 execute DB --local --file migrations/0002_sessions.sql
SEED_ADMIN_EMAIL=admin@example.com SEED_ADMIN_PASSWORD=changeme npx tsx scripts/seed-admin.ts
npx tsx scripts/seed-demo.ts   # données de démo (tuteur/apprenant/cours)
```

## Déploiement (Cloudflare)

Le Worker est déployé avec Wrangler (`main = .svelte-kit/cloudflare/_worker.js`).
Le build SvelteKit doit **obligatoirement** tourner avant `wrangler deploy`
(c'est lui qui génère `.svelte-kit/cloudflare/_worker.js`).

1. **Authentification** : `npx wrangler login` (ou `CLOUDFLARE_API_TOKEN`).
2. **Base D1 distante** (une seule fois) :
   ```bash
   npx wrangler d1 create geberlms
   # copier le database_id renvoyé dans wrangler.toml (remplacer le placeholder)
   for f in migrations/*.sql; do npx wrangler d1 execute geberlms --remote --file "$f"; done
   SEED_ADMIN_EMAIL=admin@example.com SEED_ADMIN_PASSWORD=changeme npx tsx scripts/seed-admin.ts --remote
   ```
3. **Déploiement** :
   ```bash
   npm run deploy   # = npm run build && npx wrangler deploy
   ```

Dans Cloudflare Pages, utiliser comme « Deploy command » :
`npm run deploy` (ou configurer « Build command » = `npm run build` avant la
commande de déploiement).

## Structure

```
docs/spec/           Spécifications (CMMI L3)
migrations/          Migrations SQL D1
src/lib/domain/      Logique métier pure (testée)
src/lib/server/      Couche serveur (D1/Drizzle, auth)
src/routes/          Pages SvelteKit (login, admin…)
tests/domain/        Tests Vitest
```

## Documentation

- `docs/spec/01-exigences.md` — exigences fonctionnelles et non fonctionnelles
- `docs/spec/02-architecture.md` — architecture technique et décisions
- `docs/spec/03-processus-cmmi3.md` — processus, TDD, revues, risques, traçabilité
