# LMS Helveticore — Processus (CMMI-DEV niveau 3)

Document de processus. Numéro : SPEC-003. Version : 0.1.

---

## 1. Objet

Ce document définit le **processus standard** de développement du projet, aligné sur
l'esprit CMMI-DEV niveau 3 : processus documenté, standardisé, adaptable, avec revues
par les pairs, traçabilité et mesure. La méthodologie d'implémentation est le **TDD**.

---

## 2. Cycle de vie standard

```
Exigence ──► Conception ──► Implémentation (TDD) ──► Vérification ──► Validation ──► Livraison
                │                    │                    │               │              │
             revue               revue code           tests verts     revue métier   déploiement
```

Chaque exigence traverse l'ensemble du cycle. Rien n'est « fait » tant que la vérification
(tests) n'est pas passée et que la revue n'est pas tracée.

---

## 3. TDD — règles de travail

Boucle stricte : **Rouge → Vert → Refactor**.

1. Écrire un test qui exprime le comportement attendu (il échoue : *rouge*).
2. Écrire le minimum de code pour faire passer le test (*vert*).
3. Refactoriser sans changer le comportement (les tests restent verts).
4. Commit par incrément validé.

Règles :

- Pas de code de production sans test qui le couvre.
- Logique métier dans `src/lib/domain`, testée par Vitest sans infrastructure.
- Un test exprime un comportement, pas une implémentation.
- La suite de tests fait partie de la définition du « terminé » (DoD).

Exemple déjà en place : `domain/pricing`, `domain/coupon`, `domain/vat` + 23 tests verts.

---

## 4. Portes de revue (gates)

| Porte | Quand | Critère de sortie |
|-------|-------|-------------------|
| G1 Exigences | fin de SPEC-001 | exigences identifiées, testables, tracées |
| G2 Conception | avant codage | architecture + modèle de données approuvés |
| G3 Code | fin d'une exigence | tests verts + revue par les pairs |
| G4 Vérification | avant livraison | suite complète verte, typecheck propre |
| G5 Validation | avant prod | scénarios métier validés par l'exploitant |

Toute porte bloquante est documentée et doit être levée avant de continuer.

---

## 5. Matrice de traçabilité

Chaque exigence est reliée à son implémentation et à ses tests. Extrait initial :

| Exigence | Module | Tests |
|----------|--------|-------|
| FR-01 / FR-03 | `src/lib/domain/roles.ts` | `tests/domain/roles.test.ts` |
| FR-02 | `src/lib/domain/user.ts` | `tests/domain/user.test.ts` |
| FR-04 / FR-07 | `src/lib/domain/guardianship.ts` | `tests/domain/guardianship.test.ts` |
| FR-05 / FR-06 | `src/lib/domain/enrollment.ts` | `tests/domain/enrollment.test.ts` |
| FR-13 / FR-14 | `src/lib/domain/content.ts` | `tests/domain/content.test.ts` |
| FR-10 / FR-11 / FR-12 | `src/lib/domain/catalog.ts` | `tests/domain/catalog.test.ts` |
| FR-42 / FR-43 / FR-44 | `src/lib/domain/coupon.ts` | `tests/domain/coupon.test.ts` |
| FR-46 / BR-01 / BR-02 / BR-03 / BR-04 | `src/lib/domain/pricing.ts` | `tests/domain/pricing.test.ts` |
| NFR-08 / BR-05 | `src/lib/domain/vat.ts` | `tests/domain/vat.test.ts` |
| FR-03 | `src/lib/domain/authz.ts` | `tests/domain/authz.test.ts` |
| NFR-03 (auth) | `src/lib/domain/password.ts`, `session.ts` | `tests/domain/password.test.ts`, `session.test.ts` |
| FR-20 | `src/lib/domain/progress.ts` | `tests/domain/progress.test.ts` |
| FR-21 | `src/lib/domain/dashboard.ts` | `tests/domain/dashboard.test.ts` |
| FR-22 | `src/lib/domain/dashboard.ts` | `tests/domain/dashboard.test.ts` |
| FR-23 | `src/lib/domain/activity.ts` | `tests/domain/activity.test.ts` |
| FR-24 | `src/lib/domain/upload.ts` | `tests/domain/upload.test.ts` |
| FR-30 | `src/lib/domain/quiz.ts` | `tests/domain/quiz.test.ts` |
| FR-31 | `src/lib/domain/quiz.ts` | `tests/domain/quiz.test.ts` |
| FR-40 / FR-41 | `src/lib/domain/payment.ts`, `enrollment.ts` | `tests/domain/payment.test.ts`, `enrollment.test.ts` |
| FR-47 | `src/lib/domain/invoice.ts` | `tests/domain/invoice.test.ts` |

La matrice complète est tenue à jour à chaque ajout d'exigence.

---

## 6. Gestion des risques (registre initial)

| Id | Risque | Gravité | Mitigation |
|----|--------|---------|------------|
| R-01 | Mode d'intégration Payoneer à confirmer (demande de paiement semi-manuelle vs checkout automatisé) et disponibilité pour un commerçant estonien | Moyenne | Valider le produit Payoneer exact ; le flux semi-manuel convient au modèle « compte créé par l'admin ». |
| R-02 | Taux de TVA UE inexacts/obsolètes (OSS) | Haute | Table versionnée + re-validation officielle avant prod. |
| R-03 | Coût LLM hors budget | Moyenne | Suivi mensuel, alerte à 80 €, cache des générations. |
| R-04 | Anti-copie contournée (capture) | Moyenne | Dissuasion + journalisation ; pas de fausse promesse d'imperméabilité. |
| R-05 | Fuite d'accès entre tuteurs | Haute | Contrôle d'accès par payeur testé systématiquement. |
| R-06 | Non-conformité RGPD | Moyenne | Consentement, minimisation, droit à l'effacement. |

---

## 7. Mesures et indicateurs

- Couverture des tests du domaine (objectif : ≥ 80 % sur `domain`).
- Nombre de défauts par livraison.
- Temps de cycle (exigence → livrée).
- Dépense LLM mensuelle (seuil : 100 €).
- Temps de réponse p95 (seuil : 1,5 s).

---

## 8. Gestion de configuration

- Code sous Git (branche `main` protégée, commits atomiques).
- Versionnement sémantique.
- Secrets hors du dépôt (`.env`, `.dev.vars`, jamais commités).
- Documents de spec versionnés avec le code.
