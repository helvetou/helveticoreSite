# LMS Helveticore — Spécification des exigences

Document de spécification des exigences. Numéro : SPEC-001. Version : 0.1.
Statut : **Brouillon pour revue**. Méthodologie : CMMI-DEV niveau 3 (processus défini).

---

## 1. Objet et périmètre

Le LMS Helveticore est une plateforme de vente de cours produits par l'exploitant,
exploités via **Helveticore OÜ** (Estonie). Elle permet de :

- vendre des cours à deux catégories de clients (apprenant financé, apprenant auto-payeur) ;
- gérer des codes promo (réduction totale ou partielle) ;
- suivre la progression académique ;
- proposer de l'e-testing et de la génération de quiz par LLM.

**Hors périmètre (v1)** : application mobile native, marché multi-vendeurs, visioconférence intégrée.

---

## 2. Contexte métier

- **Fiscalité** : déclarations en Estonie. Facturation en EUR.
- **Paiement** : Payoneer (compte Helveticore déjà validé), retrait des fonds vers un compte Revolut (IBAN) de récupération.
- **TVA** : taux du pays de l'acheteur (régime OSS pour les consommateurs UE). Hors UE : pas de TVA UE.
- **Langues des cours** : une langue parmi FR, EN, AR, DE (cours monolingue).
- **Volume cible au lancement** : quelques dizaines d'utilisateurs.
- **Budget LLM** : ≤ 100 € / mois.

---

## 3. Acteurs et rôles

| Rôle | Description |
|------|-------------|
| **Admin** | Exploitant. Gère cours, ressources, coupons, comptes. |
| **Apprenant** | Suit les cours. Soit financé par un tuteur, soit auto-payeur (flag `self_payer`). |
| **Tuteur** | Finance un ou plusieurs apprenants et suit leur progression. |

Un apprenant peut être financé par un tuteur ; un apprenant auto-payeur se finance lui-même.
Chaque inscription (course enrollment) est financée par **un seul payeur**.

---

## 4. Exigences fonctionnelles

Identifiants uniques `FR-xx`. Chaque exigence est testable et tracée (voir matrice de traçabilité).

### 4.1 Comptes et accès

- **FR-01** — Le système distingue trois rôles : admin, apprenant, tuteur.
- **FR-02** — L'apprenant est auto-payeur si `self_payer = true`, sinon il est financé.
- **FR-03** — Aucune auto-inscription publique. Les comptes apprenant et tuteur sont créés par l'admin (via un script / tableau de bord) après paiement.
- **FR-04** — L'admin associe un ou plusieurs apprenants à un tuteur.
- **FR-05** — Un apprenant peut être inscrit à plusieurs cours.
- **FR-06** — Chaque inscription est financée par un unique payeur (tuteur ou l'apprenant lui-même).
- **FR-07** — Le tuteur voit uniquement les apprenants qu'il finance (et non ceux des autres tuteurs).

### 4.2 Structure des cours

- **FR-10** — Un cours est structuré en modules → leçons → ressources.
- **FR-11** — L'admin peut ajouter, modifier, cacher et supprimer un cours, un module, une leçon ou une ressource.
- **FR-12** — Une ressource peut être cachée sans être supprimée (visibilité réversible).
- **FR-13** — Le contenu est mixte : vidéo, texte, quiz.
- **FR-14** — Un cours est monolingue (FR / EN / AR / DE).

### 4.3 Suivi et progression

- **FR-20** — Le système enregistre la progression académique par apprenant et par leçon.
- **FR-21** — Le tableau de bord tuteur affiche, pour chaque apprenant financé : les cours, la progression et les résultats.
- **FR-22** — Le tableau de bord apprenant affiche ses cours, sa progression et ses dépôts de documents.
- **FR-23** — Chaque action sensible (connexion, consultation, dépôt, correction, paiement) est journalisée (logging).
- **FR-24** — L'apprenant peut déposer (uploader) un document dans le cadre d'un cours ou d'une leçon.

### 4.4 Évaluation

- **FR-30** — Le système fournit de l'e-testing : quiz, chronométrage optionnel, correction automatique.
- **FR-31** — L'admin peut générer des quiz automatiquement via un LLM (défaut : Workers AI / Gemini ; option : DeepSeek).

### 4.5 Paiement et coupons

- **FR-40** — Le paiement passe par Payoneer (demande de paiement ou checkout) ; aucune donnée carte n'est hébergée par le LMS.
- **FR-41** — À la confirmation de l'encaissement Payoneer, l'accès est activé et le compte apprenant peut être créé par l'admin.
- **FR-42** — L'admin crée des coupons : réduction en pourcentage (0–100) ou en montant fixe (EUR).
- **FR-43** — Un coupon de 100 % correspond à une gratuité totale.
- **FR-44** — Un coupon peut être limité (date d'expiration, nombre d'utilisations).
- **FR-45** — Les coupons s'appliquent aux apprenants financés comme aux auto-payeurs.
- **FR-46** — Le système calcule le prix : remise sur le net, puis TVA au taux du pays de l'acheteur.
- **FR-47** — Le système génère une facture (TVA) pour chaque inscription payante.

---

## 5. Exigences non fonctionnelles

- **NFR-01 (Plateforme)** — Déploiement sur Cloudflare (Workers/Pages, D1, R2, KV).
- **NFR-02 (Performance)** — Structure légère ; temps de réponse page cible < 1,5 s (p95).
- **NFR-03 (Sécurité)** — Pas de données carte côté LMS (Payoneer) ; contrôle d'accès strict par rôle ; secrets hors du code.
- **NFR-04 (Testabilité)** — TDD ; logique métier en modules purs sans dépendance à l'infrastructure.
- **NFR-05 (Maintenabilité)** — Code typé (TypeScript strict), modulaire, documenté.
- **NFR-06 (Coût)** — Génération LLM ≤ 100 € / mois.
- **NFR-07 (Échelle)** — Dimensionné pour quelques dizaines d'utilisateurs au lancement.
- **NFR-08 (Conformité)** — TVA/OSS ; RGPD (données personnelles, consentement, effacement).
- **NFR-09 (Traçabilité)** — Journal d'audit des actions admin et académiques.
- **NFR-10 (Anti-copie)** — Difficulté d'extraction en masse du contenu (voir architecture, §5).

---

## 6. Règles métier (BR)

- **BR-01** — Montants manipulés en centimes (entiers) ; aucune arithmétique flottante sur l'argent.
- **BR-02** — Remise appliquée sur le prix net, TVA calculée sur le montant remisé.
- **BR-03** — Hors UE : taux de TVA UE = 0.
- **BR-04** — Une remise ne peut jamais rendre le total négatif.
- **BR-05** — Les taux de TVA sont des données versionnées, re-validées avant mise en production.

---

## 7. Traçabilité

Chaque exigence est reliée à au moins un test et un module (voir `03-processus-cmmi3.md`, §5).
Le suivi se fait par la matrice exigences → tests → code.
