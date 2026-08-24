# Rapport de préparation — Loi 25

**Site:** https://pepiniere-renard-bleu.example
**Date:** 2026-08-24

> **Avis important** — Ce rapport est une autoévaluation de préparation produite par un outil automatisé. Il ne constitue pas un avis juridique, ne rend aucun verdict de conformité et ne remplace pas la consultation d'un professionnel du droit. Chaque constat indique le niveau d'autorité de sa base légale (LOI / CAI / INTERPRÉTATION).

## Si vous ne lisez qu'un paragraphe

**30 points vérifiés** : Atteint 3 · Partiel 7 · Non atteint 8 · Sans objet 4 · Indéterminé 8.

**Priorités :**
1. **La personne responsable, affichée et joignable.** Publier le titre et un moyen de contact du responsable sur le site.
2. **Le registre des incidents.** Créer le registre (8 éléments prescrits) et brancher le processus de réponse dessus.
3. **Vos données chez des fournisseurs hors Québec.** Inventorier les fournisseurs hors Québec, puis ÉFVP + entente écrite pour chacun.

Un constat « Indéterminé » est un point à clarifier ensemble, pas un échec.

## Posture par domaine

- **Transparence** — Atteint: 2, Partiel: 2, Indéterminé: 5
- **Gouvernance** — Partiel: 3, Indéterminé: 3, Non atteint: 6, Atteint: 1
- **Incidents** — Non atteint: 1
- **Fournisseurs et transferts** — Non atteint: 1, Partiel: 1
- **Catégories particulières** — Sans objet: 4, Partiel: 1

## Constats

### A1 — Politique de confidentialité publiée sur le site web

- **Statut:** Atteint
- **Base légale:** s. 8.2 [LOI]
- **Éléments observés:**
  - https://pepiniere-renard-bleu.example/politique-de-confidentialite.html
- **Raisonnement:** Une page dédiée à la politique de confidentialité a été trouvée.

### A2 — Politique en termes simples et clairs, couvrant fins, droits, tiers et communication hors Québec

- **Statut:** Indéterminé
- **Base légale:** ss. 8, 8.2 + guide CAI [LOI]
- **Raisonnement:** Moteur sémantique non configuré (clé ANTHROPIC_API_KEY absente); cette vérification de jugement n'a pas été évaluée.

### A3 — Titre et coordonnées du responsable de la protection des renseignements personnels publiés

- **Statut:** Partiel
- **Base légale:** s. 3.1 [LOI]
- **Éléments observés:**
  - https://pepiniere-renard-bleu.example/politique-de-confidentialite.html
  - « …e en tout temps grâce au lien présent dans chaque courriel. responsable de la protection des renseignements personnels la direction de la pépinière agit comme responsable de la p… »
- **Raisonnement:** Responsable mentionné, mais aucun moyen de contact détecté à proximité.

### A4 — Information détaillée sur les politiques de gouvernance publiée

- **Statut:** Indéterminé
- **Base légale:** s. 3.2 [LOI]
- **Raisonnement:** Moteur sémantique non configuré (clé ANTHROPIC_API_KEY absente); cette vérification de jugement n'a pas été évaluée.

### A5 — Témoins non essentiels inactifs avant consentement; bannière avec refus accessible

- **Statut:** Partiel
- **Base légale:** s. 8.1 + Lignes directrices 2023-1 [CAI] *(interprétation contestée)*
- **Éléments observés:**
  - https://pepiniere-renard-bleu.example/
  - traceurs / trackers: Google Analytics / GTM
- **Raisonnement:** Scripts de traceurs dans le contenu initial sans plateforme de consentement détectée. Indicateur d'activation avant consentement (attente du régulateur, niveau contesté); une confirmation à l'exécution est recommandée.

### A6 — Technologies de repérage, localisation ou profilage divulguées, avec moyens d'activation

- **Statut:** Indéterminé
- **Base légale:** s. 8.1 [LOI]
- **Raisonnement:** Moteur sémantique non configuré (clé ANTHROPIC_API_KEY absente); cette vérification de jugement n'a pas été évaluée.

### A7 — Version française du site, de la politique et des conditions (français d'abord pour les contrats d'adhésion)

- **Statut:** Atteint
- **Base légale:** Charte de la langue française, art. 52, 55 [INTERPRÉTATION] *(interprétation contestée)*
- **Éléments observés:**
  - https://pepiniere-renard-bleu.example/
  - html lang=fr
  - version fr / fr alternate: non/no
- **Raisonnement:** Le site se présente en français (exposition faible à l'art. 52 de la Charte). Les versions françaises de la politique et des conditions restent à vérifier page par page.

### A8 — Formulaires : consentement par finalité, en termes clairs, demandé distinctement

- **Statut:** Indéterminé
- **Base légale:** s. 14 [LOI]
- **Raisonnement:** Moteur sémantique non configuré (clé ANTHROPIC_API_KEY absente); cette vérification de jugement n'a pas été évaluée.

### A9 — Pratique d'avis de modification de la politique

- **Statut:** Indéterminé
- **Base légale:** s. 8.2 [LOI]
- **Raisonnement:** Moteur sémantique non configuré (clé ANTHROPIC_API_KEY absente); cette vérification de jugement n'a pas été évaluée.

### A10 — Formulaires : aucun refus de biens ou services pour refus de fournir des RP non nécessaires

- **Statut:** Indéterminé
- **Base légale:** s. 9 [LOI]
- **Raisonnement:** Moteur sémantique non configuré (clé ANTHROPIC_API_KEY absente); cette vérification de jugement n'a pas été évaluée.

### B1 — Registre des incidents de confidentialité (8 éléments prescrits, conservation 5 ans) et processus de réponse

- **Statut:** Non atteint
- **Base légale:** ss. 3.5-3.8 + Règlement sur les incidents [LOI]
- **Éléments observés:**
  - réponse / answer: non, on note les pépins dans un cahier quand on y pense, mais il n'y a pas de registre officiel ni de marche à suivre.
- **Raisonnement:** Autodéclaré dans le questionnaire; les documents à l'appui n'ont pas été vérifiés de façon indépendante.

### B2 — EFVP pour tout système d'information acquis, développé ou refondu impliquant des RP

- **Statut:** Non atteint
- **Base légale:** s. 3.3 [LOI]
- **Éléments observés:**
  - réponse / answer: non, on n'a jamais fait ça. La boutique en ligne a été montée par notre neveu en 2021.
- **Raisonnement:** Autodéclaré dans le questionnaire; les documents à l'appui n'ont pas été vérifiés de façon indépendante.

### B3 — EFVP et entente écrite pour toute communication hors Québec (incluant chaque SaaS hébergé aux É.-U.)

- **Statut:** Non atteint
- **Base légale:** s. 17 [LOI]
- **Éléments observés:**
  - réponse / answer: non. On utilise Shopify pour la boutique et Mailchimp pour l'infolettre, mais personne n'a évalué ça ni signé d'entente particulière.
  - Hébergement aux États-Unis pour les deux outils.
- **Raisonnement:** Autodéclaré dans le questionnaire; les documents à l'appui n'ont pas été vérifiés de façon indépendante.

### B4 — Contrats écrits avec les mandataires et fournisseurs de services

- **Statut:** Partiel
- **Base légale:** s. 18.3 [LOI]
- **Éléments observés:**
  - réponse / answer: partiellement. On a les contrats standards des fournisseurs, mais on ne sait pas s'ils contiennent les clauses dont vous parlez.
- **Raisonnement:** Autodéclaré dans le questionnaire; les documents à l'appui n'ont pas été vérifiés de façon indépendante.

### B5 — Politiques internes : rôles du cycle de vie, conservation/destruction, traitement des plaintes

- **Statut:** Non atteint
- **Base légale:** s. 3.2 [LOI]
- **Éléments observés:**
  - réponse / answer: non, rien d'écrit. On garde les factures sept ans pour l'impôt, c'est pas mal tout.
- **Raisonnement:** Autodéclaré dans le questionnaire; les documents à l'appui n'ont pas été vérifiés de façon indépendante.

### B6 — Systèmes biométriques : consentement exprès et déclaration à la CAI 60 jours avant la mise en service

- **Statut:** Sans objet
- **Base légale:** LCCJTI, art. 44-45 [LOI]
- **Éléments observés:**
  - réponse / answer: pas de biométrie ici.
- **Raisonnement:** Déclaré sans objet dans le questionnaire (la pratique visée par cette vérification n'est pas utilisée).

### B7 — Décisions fondées exclusivement sur un traitement automatisé : information et droit de faire des observations

- **Statut:** Sans objet
- **Base légale:** s. 12.1 [LOI]
- **Éléments observés:**
  - réponse / answer: non, toutes les décisions passent par un humain.
- **Raisonnement:** Déclaré sans objet dans le questionnaire (la pratique visée par cette vérification n'est pas utilisée).

### B8 — Mineurs de moins de 14 ans : consentement du titulaire de l'autorité parentale

- **Statut:** Sans objet
- **Base légale:** s. 4.1 [LOI]
- **Éléments observés:**
  - réponse / answer: on ne vise pas les enfants, nos clients sont des adultes.
- **Raisonnement:** Déclaré sans objet dans le questionnaire (la pratique visée par cette vérification n'est pas utilisée).

### B9 — Traitement des demandes de portabilité (format technologique structuré et couramment utilisé)

- **Statut:** Indéterminé
- **Base légale:** s. 27 [LOI]
- **Éléments observés:**
  - réponse / answer: incertain. Shopify doit bien pouvoir exporter quelque chose, mais on n'a jamais essayé.
- **Raisonnement:** Autodéclaré dans le questionnaire; les documents à l'appui n'ont pas été vérifiés de façon indépendante.

### B10 — Renseignements sensibles : consentement exprès pour l'utilisation et la communication

- **Statut:** Sans objet
- **Base légale:** ss. 12-13 [LOI]
- **Éléments observés:**
  - réponse / answer: rien de sensible, des commandes de plantes.
- **Raisonnement:** Déclaré sans objet dans le questionnaire (la pratique visée par cette vérification n'est pas utilisée).

### B11 — Formation et sensibilisation du personnel à la protection des RP

- **Statut:** Non atteint
- **Base légale:** attente de la CAI (guides) [CAI]
- **Éléments observés:**
  - réponse / answer: non, jamais eu de formation là-dessus.
- **Raisonnement:** Autodéclaré dans le questionnaire; les documents à l'appui n'ont pas été vérifiés de façon indépendante.

### B12 — Mesures de sécurité proportionnées (sensibilité, finalité, quantité, répartition, support)

- **Statut:** Partiel
- **Base légale:** s. 10 [LOI]
- **Éléments observés:**
  - réponse / answer: partiellement. Les mots de passe sont dans un cahier au bureau; l'ordinateur de la caisse a un antivirus.
- **Raisonnement:** Autodéclaré dans le questionnaire; les documents à l'appui n'ont pas été vérifiés de façon indépendante.

### B13 — Exactitude et mise à jour des RP utilisés pour une décision; conservation ≥ 1 an après la décision

- **Statut:** Atteint
- **Base légale:** s. 11 [LOI]
- **Éléments observés:**
  - réponse / answer: oui, les dossiers clients sont à jour dans Shopify.
- **Raisonnement:** Autodéclaré dans le questionnaire; les documents à l'appui n'ont pas été vérifiés de façon indépendante.

### B14 — Destruction ou anonymisation des RP lorsque les fins sont accomplies

- **Statut:** Non atteint
- **Base légale:** s. 23 [LOI]
- **Éléments observés:**
  - réponse / answer: non, on n'efface jamais rien. Les anciennes listes de clients sont toutes gardées.
- **Raisonnement:** Autodéclaré dans le questionnaire; les documents à l'appui n'ont pas été vérifiés de façon indépendante.

### B15 — Prospection commerciale : consentement requis (jamais une « fin compatible »); identification et droit de retrait

- **Statut:** Partiel
- **Base légale:** ss. 12, 22 [LOI]
- **Éléments observés:**
  - réponse / answer: partiellement. Les gens s'abonnent eux-mêmes à l'infolettre, mais on a déjà ajouté des clients de la caisse sans leur demander.
- **Raisonnement:** Autodéclaré dans le questionnaire; les documents à l'appui n'ont pas été vérifiés de façon indépendante.

### B16 — Traitement des demandes d'accès et de rectification : réponse écrite sous 30 jours, gratuité, refus motivés

- **Statut:** Indéterminé
- **Base légale:** ss. 27-34 [LOI]
- **Éléments observés:**
  - réponse / answer: incertain. Personne n'a jamais demandé, on ne saurait pas trop comment répondre dans les délais.
- **Raisonnement:** Autodéclaré dans le questionnaire; les documents à l'appui n'ont pas été vérifiés de façon indépendante.

### B17 — Inventaire à jour des renseignements personnels détenus, avec évaluation de sensibilité

- **Statut:** Non atteint
- **Base légale:** pratique-phare de la CAI (aide-mémoire; guide prévention, étape 2; guide EFVP, étape 3) [CAI]
- **Éléments observés:**
  - réponse / answer: non, on n'a pas de liste de ce qu'on détient ni où c'est rendu.
- **Raisonnement:** Autodéclaré dans le questionnaire; les documents à l'appui n'ont pas été vérifiés de façon indépendante.

### B18 — Vidéosurveillance : nécessité/proportionnalité documentées, affichage, conservation limitée (~30 jours)

- **Statut:** Partiel
- **Base légale:** fiche vidéosurveillance (2019, jurisprudence) + s. 8; EFVP obligatoire post-Loi 25 [CAI]
- **Éléments observés:**
  - réponse / answer: partiellement. Il y a quatre caméras contre le vol, une affichette à l'entrée, mais on garde les images tant que le disque n'est pas plein.
- **Raisonnement:** Autodéclaré dans le questionnaire; les documents à l'appui n'ont pas été vérifiés de façon indépendante.

### B19 — Authentification multifacteur (MFA) sur les courriels et les accès à distance

- **Statut:** Partiel
- **Base légale:** s. 10 (application courante) [INTERPRÉTATION]
- **Éléments observés:**
  - réponse / answer: partiellement. La MFA est activée sur le courriel de la propriétaire, mais pas sur les deux autres comptes ni sur l'accès à distance de la caisse.
- **Raisonnement:** Autodéclaré dans le questionnaire; les documents à l'appui n'ont pas été vérifiés de façon indépendante.

### B20 — Copies de sauvegarde hors ligne des données critiques, testées régulièrement

- **Statut:** Non atteint
- **Base légale:** s. 10 (application courante) [INTERPRÉTATION]
- **Éléments observés:**
  - réponse / answer: non, la sauvegarde est sur un disque branché en permanence à l'ordinateur du bureau.
- **Raisonnement:** Autodéclaré dans le questionnaire; les documents à l'appui n'ont pas été vérifiés de façon indépendante.


## Annexe — Préparer une demande d'assurance cyber

Les demandes d'assurance cyber s'ouvrent sur le chiffre d'affaires et le nombre d'employés; les contrôles ci-dessous déterminent ensuite l'admissibilité et les rabais. Les éléments de gouvernance (politique, responsable, conservation) figurent surtout sur les formulaires détaillés et les suivis de souscription — pas sur tous les formulaires courts. Ce tableau relie vos constats Balise à ces thèmes récurrents; chaque statut renvoie au constat complet et à sa preuve dans le rapport.

| Thème du questionnaire | Où les assureurs le demandent | Vos constats |
|---|---|---|
| Authentification multifacteur (MFA) | Question obligatoire des formulaires courts (condition d'admissibilité). | B19 : Partiel |
| Copies de sauvegarde hors ligne, testées | Question obligatoire des formulaires courts (condition d'admissibilité). | B20 : Non atteint |
| Formation et sensibilisation du personnel | Question obligatoire ou à rabais sur la plupart des formulaires. | B11 : Non atteint |
| Plan de réponse et registre des incidents | Tous les formulaires exigent l'historique des violations (3 à 5 ans); un registre d'incidents tenu à jour y répond directement. | B1 : Non atteint |
| Politique de confidentialité documentée | Formulaires détaillés et suivis de souscription; l'assureur peut demander la politique elle-même. | A1 : Atteint · A2 : Indéterminé |
| Responsable désigné (sécurité et vie privée) | Formulaires détaillés (personne désignée pour la vie privée). | A3 : Partiel |
| Gestion des fournisseurs et des tiers | Formulaires courts (liste des fournisseurs TI critiques) et détaillés (revues annuelles, preuve d'assurance des fournisseurs). | B3 : Non atteint · B4 : Partiel |
| Conservation, destruction et demandes d'accès | Formulaires détaillés (politique de conservation, destruction sécurisée, procédures de demandes d'accès). | B5 : Non atteint · B14 : Non atteint · B16 : Indéterminé |
| Mesures de sécurité générales (art. 10) | Trame de fond de toutes les questions techniques des formulaires. | B12 : Partiel |

> Balise n'évalue pas les contrôles purement techniques que les formulaires détaillés peuvent aussi demander (chiffrement, EDR, gestion des correctifs, tests d'intrusion, etc.) : indiquez « non évalué par cet outil » et répondez-y avec votre fournisseur TI.


---

# Law 25 Readiness Report

**Site:** https://pepiniere-renard-bleu.example
**Date:** 2026-08-24

> **Important notice** — This report is a readiness self-assessment produced by an automated tool. It is not legal advice, renders no compliance verdict, and does not replace consulting a legal professional. Every finding states the authority tier of its legal basis (STATUTE / CAI / FIRM).

## If you read only one paragraph

**30 points assessed** : Met 3 · Partial 7 · Not met 8 · Not applicable 4 · Unknown 8.

**Priorities:**
1. **Your privacy officer, named and reachable.** Publish the officer's title and a contact means on the site.
2. **The incident register.** Create the register (8 prescribed elements) and wire the response process to it.
3. **Your data at vendors outside Quebec.** Inventory out-of-Quebec vendors, then PIA + written agreement for each.

An 'Unknown' finding is a point to clarify together, not a failure.

## Posture by domain

- **Transparency** — Met: 2, Partial: 2, Unknown: 5
- **Governance** — Partial: 3, Unknown: 3, Not met: 6, Met: 1
- **Incidents** — Not met: 1
- **Vendors & transfers** — Not met: 1, Partial: 1
- **Special categories** — Not applicable: 4, Partial: 1

## Findings

### A1 — Privacy policy published on the website

- **Status:** Met
- **Legal basis:** s. 8.2 [STATUTE]
- **Evidence:**
  - https://pepiniere-renard-bleu.example/politique-de-confidentialite.html
- **Reasoning:** A dedicated privacy-policy page was retrieved.

### A2 — Policy in clear and plain language, covering purposes, rights, third parties and communication outside Quebec

- **Status:** Unknown
- **Legal basis:** ss. 8, 8.2 + guide CAI [STATUTE]
- **Reasoning:** Semantic engine not configured (ANTHROPIC_API_KEY absent); this judgment-type check was not assessed.

### A3 — Privacy officer title and contact information published

- **Status:** Partial
- **Legal basis:** s. 3.1 [STATUTE]
- **Evidence:**
  - https://pepiniere-renard-bleu.example/politique-de-confidentialite.html
  - « …e en tout temps grâce au lien présent dans chaque courriel. responsable de la protection des renseignements personnels la direction de la pépinière agit comme responsable de la p… »
- **Reasoning:** Officer mentioned but no contact means detected nearby.

### A4 — Detailed information about governance policies published

- **Status:** Unknown
- **Legal basis:** s. 3.2 [STATUTE]
- **Reasoning:** Semantic engine not configured (ANTHROPIC_API_KEY absent); this judgment-type check was not assessed.

### A5 — Non-essential trackers inactive before consent; banner with accessible refusal

- **Status:** Partial
- **Legal basis:** s. 8.1 + Lignes directrices 2023-1 [CAI] *(contested interpretation)*
- **Evidence:**
  - https://pepiniere-renard-bleu.example/
  - traceurs / trackers: Google Analytics / GTM
- **Reasoning:** Tracker scripts in the initial payload with no consent platform detected. Indicator of activation before consent (regulator expectation, contested tier); runtime confirmation recommended.

### A6 — Tracking, locating or profiling technology disclosed, with means of activation

- **Status:** Unknown
- **Legal basis:** s. 8.1 [STATUTE]
- **Reasoning:** Semantic engine not configured (ANTHROPIC_API_KEY absent); this judgment-type check was not assessed.

### A7 — French version of site, policy and terms (French-first for adhesion contracts)

- **Status:** Met
- **Legal basis:** Charte de la langue française, art. 52, 55 [FIRM] *(contested interpretation)*
- **Evidence:**
  - https://pepiniere-renard-bleu.example/
  - html lang=fr
  - version fr / fr alternate: non/no
- **Reasoning:** Site presents in French (Charter s. 52 exposure low). Policy/ToS French versions still need page-level review.

### A8 — Forms: purpose-granular consent, in clear language, requested separately

- **Status:** Unknown
- **Legal basis:** s. 14 [STATUTE]
- **Reasoning:** Semantic engine not configured (ANTHROPIC_API_KEY absent); this judgment-type check was not assessed.

### A9 — Policy amendment-notice practice

- **Status:** Unknown
- **Legal basis:** s. 8.2 [STATUTE]
- **Reasoning:** Semantic engine not configured (ANTHROPIC_API_KEY absent); this judgment-type check was not assessed.

### A10 — Forms: no refusal of goods or services over declining to provide unnecessary PI

- **Status:** Unknown
- **Legal basis:** s. 9 [STATUTE]
- **Reasoning:** Semantic engine not configured (ANTHROPIC_API_KEY absent); this judgment-type check was not assessed.

### B1 — Confidentiality-incident register (8 prescribed elements, 5-year retention) and response process

- **Status:** Not met
- **Legal basis:** ss. 3.5-3.8 + Règlement sur les incidents [STATUTE]
- **Evidence:**
  - réponse / answer: non, on note les pépins dans un cahier quand on y pense, mais il n'y a pas de registre officiel ni de marche à suivre.
- **Reasoning:** Self-reported through the intake questionnaire; supporting documents not independently verified.

### B2 — PIA for any acquired, developed or overhauled information system involving PI

- **Status:** Not met
- **Legal basis:** s. 3.3 [STATUTE]
- **Evidence:**
  - réponse / answer: non, on n'a jamais fait ça. La boutique en ligne a été montée par notre neveu en 2021.
- **Reasoning:** Self-reported through the intake questionnaire; supporting documents not independently verified.

### B3 — PIA and written agreement for any communication outside Quebec (including every US-hosted SaaS)

- **Status:** Not met
- **Legal basis:** s. 17 [STATUTE]
- **Evidence:**
  - réponse / answer: non. On utilise Shopify pour la boutique et Mailchimp pour l'infolettre, mais personne n'a évalué ça ni signé d'entente particulière.
  - Hébergement aux États-Unis pour les deux outils.
- **Reasoning:** Self-reported through the intake questionnaire; supporting documents not independently verified.

### B4 — Written contracts with mandataries and service providers

- **Status:** Partial
- **Legal basis:** s. 18.3 [STATUTE]
- **Evidence:**
  - réponse / answer: partiellement. On a les contrats standards des fournisseurs, mais on ne sait pas s'ils contiennent les clauses dont vous parlez.
- **Reasoning:** Self-reported through the intake questionnaire; supporting documents not independently verified.

### B5 — Internal policies: lifecycle roles, retention/destruction, complaint handling

- **Status:** Not met
- **Legal basis:** s. 3.2 [STATUTE]
- **Evidence:**
  - réponse / answer: non, rien d'écrit. On garde les factures sept ans pour l'impôt, c'est pas mal tout.
- **Reasoning:** Self-reported through the intake questionnaire; supporting documents not independently verified.

### B6 — Biometric systems: express consent and CAI declaration 60 days before service

- **Status:** Not applicable
- **Legal basis:** LCCJTI, art. 44-45 [STATUTE]
- **Evidence:**
  - réponse / answer: pas de biométrie ici.
- **Reasoning:** Declared not applicable in the intake (the practice this check covers is not in use).

### B7 — Decisions based exclusively on automated processing: disclosure and right to submit observations

- **Status:** Not applicable
- **Legal basis:** s. 12.1 [STATUTE]
- **Evidence:**
  - réponse / answer: non, toutes les décisions passent par un humain.
- **Reasoning:** Declared not applicable in the intake (the practice this check covers is not in use).

### B8 — Minors under 14: consent of the holder of parental authority

- **Status:** Not applicable
- **Legal basis:** s. 4.1 [STATUTE]
- **Evidence:**
  - réponse / answer: on ne vise pas les enfants, nos clients sont des adultes.
- **Reasoning:** Declared not applicable in the intake (the practice this check covers is not in use).

### B9 — Data-portability request handling (structured, commonly used technological format)

- **Status:** Unknown
- **Legal basis:** s. 27 [STATUTE]
- **Evidence:**
  - réponse / answer: incertain. Shopify doit bien pouvoir exporter quelque chose, mais on n'a jamais essayé.
- **Reasoning:** Self-reported through the intake questionnaire; supporting documents not independently verified.

### B10 — Sensitive information: express consent for use and communication

- **Status:** Not applicable
- **Legal basis:** ss. 12-13 [STATUTE]
- **Evidence:**
  - réponse / answer: rien de sensible, des commandes de plantes.
- **Reasoning:** Declared not applicable in the intake (the practice this check covers is not in use).

### B11 — Staff privacy training and awareness

- **Status:** Not met
- **Legal basis:** attente de la CAI (guides) [CAI]
- **Evidence:**
  - réponse / answer: non, jamais eu de formation là-dessus.
- **Reasoning:** Self-reported through the intake questionnaire; supporting documents not independently verified.

### B12 — Security safeguards proportionate to sensitivity, purpose, quantity, distribution, medium

- **Status:** Partial
- **Legal basis:** s. 10 [STATUTE]
- **Evidence:**
  - réponse / answer: partiellement. Les mots de passe sont dans un cahier au bureau; l'ordinateur de la caisse a un antivirus.
- **Reasoning:** Self-reported through the intake questionnaire; supporting documents not independently verified.

### B13 — Accuracy and currency of PI used to make a decision; keep decision-info ≥ 1 year after

- **Status:** Met
- **Legal basis:** s. 11 [STATUTE]
- **Evidence:**
  - réponse / answer: oui, les dossiers clients sont à jour dans Shopify.
- **Reasoning:** Self-reported through the intake questionnaire; supporting documents not independently verified.

### B14 — Destruction or anonymization of PI once purposes are achieved

- **Status:** Not met
- **Legal basis:** s. 23 [STATUTE]
- **Evidence:**
  - réponse / answer: non, on n'efface jamais rien. Les anciennes listes de clients sont toutes gardées.
- **Reasoning:** Self-reported through the intake questionnaire; supporting documents not independently verified.

### B15 — Commercial prospection: consent required (never a 'consistent purpose'); self-identification and withdrawal right

- **Status:** Partial
- **Legal basis:** ss. 12, 22 [STATUTE]
- **Evidence:**
  - réponse / answer: partiellement. Les gens s'abonnent eux-mêmes à l'infolettre, mais on a déjà ajouté des clients de la caisse sans leur demander.
- **Reasoning:** Self-reported through the intake questionnaire; supporting documents not independently verified.

### B16 — Access/rectification request handling: written reply within 30 days, free access, reasoned refusals

- **Status:** Unknown
- **Legal basis:** ss. 27-34 [STATUTE]
- **Evidence:**
  - réponse / answer: incertain. Personne n'a jamais demandé, on ne saurait pas trop comment répondre dans les délais.
- **Reasoning:** Self-reported through the intake questionnaire; supporting documents not independently verified.

### B17 — Up-to-date inventory of personal information held, with sensitivity assessment

- **Status:** Not met
- **Legal basis:** pratique-phare de la CAI (aide-mémoire; guide prévention, étape 2; guide EFVP, étape 3) [CAI]
- **Evidence:**
  - réponse / answer: non, on n'a pas de liste de ce qu'on détient ni où c'est rendu.
- **Reasoning:** Self-reported through the intake questionnaire; supporting documents not independently verified.

### B18 — Video surveillance: documented necessity/proportionality, signage, limited retention (~30 days)

- **Status:** Partial
- **Legal basis:** fiche vidéosurveillance (2019, jurisprudence) + s. 8; EFVP obligatoire post-Loi 25 [CAI]
- **Evidence:**
  - réponse / answer: partiellement. Il y a quatre caméras contre le vol, une affichette à l'entrée, mais on garde les images tant que le disque n'est pas plein.
- **Reasoning:** Self-reported through the intake questionnaire; supporting documents not independently verified.

### B19 — Multi-factor authentication (MFA) on email and remote access

- **Status:** Partial
- **Legal basis:** s. 10 (application courante) [FIRM]
- **Evidence:**
  - réponse / answer: partiellement. La MFA est activée sur le courriel de la propriétaire, mais pas sur les deux autres comptes ni sur l'accès à distance de la caisse.
- **Reasoning:** Self-reported through the intake questionnaire; supporting documents not independently verified.

### B20 — Offline backups of critical data, regularly tested

- **Status:** Not met
- **Legal basis:** s. 10 (application courante) [FIRM]
- **Evidence:**
  - réponse / answer: non, la sauvegarde est sur un disque branché en permanence à l'ordinateur du bureau.
- **Reasoning:** Self-reported through the intake questionnaire; supporting documents not independently verified.


## Appendix — Preparing a cyber-insurance application

Cyber-insurance applications open with revenue and employee count; the controls below then determine eligibility and discounts. Governance items (policy, designated officer, retention) appear chiefly on fuller applications and underwriting follow-ups — not on every short form. This table links your Balise findings to those recurring themes; each status points back to the full finding and its evidence in the report.

| Application theme | Where insurers ask | Your findings |
|---|---|---|
| Multi-factor authentication (MFA) | Mandatory question on short-form applications (eligibility condition). | B19 : Partial |
| Offline, tested backups | Mandatory question on short-form applications (eligibility condition). | B20 : Not met |
| Staff security and privacy training | Mandatory or discount-earning question on most applications. | B11 : Not met |
| Incident response plan and register | Every form requires 3-5 years of breach history; a maintained incident register answers it directly. | B1 : Not met |
| Documented privacy policy | Fuller applications and underwriting follow-ups; the insurer may request the policy itself. | A1 : Met · A2 : Unknown |
| Designated individual (security and privacy) | Fuller applications (designated privacy individual). | A3 : Partial |
| Vendor and third-party management | Short forms (critical IT vendor list) and fuller forms (annual reviews, proof of vendors' own coverage). | B3 : Not met · B4 : Partial |
| Retention, disposal and access requests | Fuller applications (retention policy, secure disposal, access-request procedures). | B5 : Not met · B14 : Not met · B16 : Unknown |
| General security safeguards (s. 10) | The backdrop of every technical question on the forms. | B12 : Partial |

> Balise does not assess the purely technical controls fuller applications may also ask about (encryption, EDR, patch management, penetration testing, etc.): mark those "not assessed by this tool" and answer them with your IT provider.
