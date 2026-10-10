# LMS Helveticore — Architecture technique

Document d'architecture / solution technique. Numéro : SPEC-002. Version : 0.1.

---

## 1. Décisions de haut niveau

| Décision | Choix | Justification |
|----------|-------|---------------|
| Runtime | Cloudflare Workers + Pages/Static Assets | Déploiement cible imposé ; faible coût, edge. |
| Framework | SvelteKit (adapter-cloudflare) | Full-stack, léger, SSR/SSG, excellent support Workers. |
| Langage | TypeScript (strict) | Typage, testabilité, maintenabilité (NFR-05). |
| Base de données | Cloudflare D1 (SQLite) via Drizzle ORM | Léger, gratuit au départ, schéma versionné. |
| Fichiers | Cloudflare R2 | Uploads d'apprenants et ressources. |
| Auth | Sessions sur Workers + comptes en D1 | Contrôle total, zéro coût par utilisateur. |
| Paiement | Payoneer (compte Helveticore validé) + retrait Revolut | Déjà validé pour l'exploitant ; flux semi-manuel compatible avec la création de compte par l'admin. |
| LLM | Workers AI (Gemini) par défaut, DeepSeek en option | Couche d'abstraction pour changer de provider. |
| Tests | Vitest (logique métier) | TDD, rapide, sans infra. |

---

## 2. Composants

```
Navigateur ──► Cloudflare (SvelteKit SSR/edge)
                 │
                 ├─ D1 (utilisateurs, cours, inscriptions, coupons, factures, logs)
                 ├─ R2 (vidéos, documents déposés)
                 ├─ KV (sessions, cache léger)
                 ├─ Payoneer (encaissement, retrait vers Revolut)
                 └─ LLM (Workers AI / DeepSeek) — génération de quiz
```

- **`src/lib/domain`** : logique métier pure (prix, TVA, coupons, progression). Aucune dépendance framework/infra → testable en isolation (TDD).
- **`src/lib/server`** : adaptateurs Cloudflare (D1, R2, Payoneer, LLM) et routes API.
- **`src/routes`** : pages SvelteKit (apprenant, tuteur, admin).

---

## 3. Modèle de données (entités principales)

- **User** — `id`, `role` (admin|learner|tutor), `self_payer`, `email`, `name`, `locale`, `status`.
- **Guardianship** — `tutor_id`, `learner_id` (lien tuteur ↔ apprenant).
- **Course** — `id`, `slug`, `title`, `language` (fr|en|ar|de), `status`.
- **Module** — `id`, `course_id`, `position`, `title`, `status`.
- **Lesson** — `id`, `module_id`, `position`, `title`, `type` (video|text|quiz), `content_ref`, `status`.
- **Resource** — `id`, `lesson_id`, `type`, `r2_key`, `visibility` (visible|hidden).
- **Enrollment** — `id`, `learner_id`, `course_id`, `payer_id`, `payment_ref`, `coupon_id`, `status`, montants (`net`, `vat`, `total`).
- **Payment** — `id`, `stripe_ref`, `amount`, `currency`, `status`.
- **Coupon** — `id`, `code`, `type` (percent|amount), `value`, `scope`, `expires_at`, `max_uses`, `used_count`, `enabled`.
- **Progress** — `id`, `enrollment_id`, `lesson_id`, `status`, `score`, horodatages.
- **Attempt** — `id`, `quiz`, `answers`, `score`, horodatage.
- **Upload** — `id`, `learner_id`, `lesson_id`, `r2_key`, métadonnées.
- **Invoice** — `id`, `enrollment_id`, `number`, `pdf_ref`, montants, `vat_rate`.
- **ActivityLog** — `id`, `actor_id`, `action`, `target`, `meta`, horodatage.

Tous les montants sont en **centimes entiers** (BR-01).

---

## 4. Flux de paiement

1. L'acheteur (tuteur ou auto-payeur) choisit un cours, applique éventuellement un coupon.
2. Le LMS calcule le prix (remise + TVA au pays de l'acheteur) via `domain/pricing`.
3. L'admin émet une **demande de paiement Payoneer** à l'acheteur (ou checkout Payoneer si disponible) ; aucune carte n'est saisie côté LMS.
4. Payoneer notifie l'encaissement → le LMS (ou l'admin) active l'inscription.
5. L'admin crée le compte apprenant via script/tableau de bord après paiement.
6. La facture TVA est générée par le système et archivée.
7. Hors LMS : les fonds sont retirés du solde Payoneer vers le compte Revolut de récupération (voir `PayoneerToRevolutHelveticore.png`).

> ⚠️ **À confirmer** : le mode d'intégration exact (demande de paiement semi-manuelle vs Payoneer Checkout automatisé) et la disponibilité pour un commerçant estonien doivent être validés. Le flux semi-manuel correspond bien au modèle « compte créé par l'admin après paiement ». Point de risque R-01.

---

## 5. Stratégie anti-copie

L'anti-copie **absolue n'existe pas sur le web** (capture d'écran, photographie). On vise la difficulté d'extraction *massive* :

- Pas d'export PDF/EPUB du cours complet.
- Rendu du contenu à la volée, paginé (jamais de page « tout le cours »).
- Contenu mixte vidéo + texte court + interactif (moins de texte long plat à copier).
- Désactivation du glisser-copier en masse sur les zones de cours (mesure dissuasive, pas de sécurité).
- Filigrane sur les documents/vidéos.
- Quotas d'accès et journalisation (FR-23) pour détecter des comportements anormaux.

---

## 6. Stratégie LLM

- Couche d'abstraction `llm/generateQuiz(course, lesson)`.
- Défaut : **Workers AI (Gemini)** — reste dans Cloudflare, facturation unifiée.
- Option : **DeepSeek** via API externe, même interface.
- Budget suivi : alerte si la dépense mensuelle approche 100 € (NFR-06).
- Les quiz générés sont **revus/validés par l'admin** avant publication (jamais publiés automatiquement).

---

## 7. Internationalisation (i18n)

- Interface : français au lancement, puis EN / AR / DE (NFR lié).
- Contenu de cours : monolingue (FR / EN / AR / DE) — un cours = une langue.
- Support RTL prévu pour l'arabe.

---

## 8. Registre des décisions (ADR)

- **ADR-001** — SvelteKit plutôt que React : bundle léger, SSR edge, productivité solo.
- **ADR-002** — D1 plutôt que Postgres : gratuit au départ, suffisant pour le volume cible.
- **ADR-003** — Montants en centimes entiers (pas de flottant).
- **ADR-004** — Logique métier isolée dans `src/lib/domain` pour TDD.
- **ADR-005** — Payoneer (déjà validé Helveticore, lié à Revolut) plutôt que Stripe, pour éviter une nouvelle procédure de vérification.
- **ADR-006** — Épinglage Vite 6 / vite-plugin-svelte 5 / vitest 3 (au lieu du bleeding-edge Vite 8) pour une résolution de dépendances stable et compatible.
- **ADR-007** — Chaîne Cloudflare cohérente : adapter-cloudflare 7 + wrangler 4 + workers-types 5 (l'adapter 4.x était incompatible avec wrangler 4).
