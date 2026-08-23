# Balise

**Évaluation de préparation à la Loi 25 pour les PME québécoises — avec un raisonnement qu'on peut vraiment lire.**

*[English version: README.md](README.md)*

Balise analyse le site web public d'une entreprise et le combine à un questionnaire structuré pour évaluer sa préparation aux obligations de la Loi 25. Il produit un rapport bilingue (FR/EN) où **chaque constat porte ses éléments observés, sa base légale et le niveau d'autorité de cette base** — plus une piste de vérification lisible par machine couvrant toute l'évaluation.

> Balise est un outil d'autoévaluation de préparation. Ce **n'est pas un avis juridique**, et il ne rend jamais de verdict de conformité.

## Ce qui le distingue

Les outils automatisés actuels vérifient la surface du site : bannière de témoins, présence d'une politique. Or l'essentiel de la Loi 25 se trouve ailleurs — le registre des incidents, les ÉFVP pour chaque fournisseur SaaS hébergé aux États-Unis, les contrats de mandataires, les déclarations de systèmes biométriques. Balise évalue les deux couches :

- **Module A — analyse externe :** politique de confidentialité (présence et contenu), publication du responsable, indicateurs de témoins/consentement, exposition linguistique (Charte, art. 52).
- **Module B — questionnaire organisationnel :** registre d'incidents, ÉFVP, ententes de transfert (art. 17), contrats de fournisseurs, biométrie (le seul domaine d'application active de la CAI), décisions automatisées, mineurs, portabilité.

Et trois règles de conception que personne d'autre ne suit :

1. **Niveaux d'autorité.** Chaque vérification est étiquetée `LOI` (texte légal explicite), `CAI` (attente du régulateur) ou `INTERPRÉTATION` (lecture convergente des cabinets). Les points contestés — comme le consentement préalable aux témoins, qui repose sur les lignes directrices de la CAI plutôt que sur un texte réglé — sont rapportés à leur juste force. Aucun « délai de 72 heures » ici : il n'existe pas dans la loi (c'est le RGPD).
2. **Aucune note de conformité.** Le rapport montre une posture de préparation par domaine, jamais un « 82 % conforme » — un pourcentage est un verdict juridique implicite, et cet outil n'en rend pas.
3. **Une piste de vérification lisible.** Les éléments observés et le raisonnement de chaque constat sont consignés en JSONL infalsifiable et annexés au rapport. L'article 12.1 de la Loi 25 exige l'explicabilité des décisions automatisées — un outil d'évaluation devrait s'imposer la même norme.

## Utilisation

```bash
pip install -e .
balise scan https://www.exemple.com --out ./mandat-001
# avec le questionnaire organisationnel :
balise scan https://www.exemple.com --intake intake/rempli.yaml --out ./mandat-001
```

Les vérifications déterministes s'exécutent sans aucune configuration. Les vérifications de jugement (langage clair, couverture des divulgations) passent par un moteur IA optionnel — sans lui, elles rapportent honnêtement « indéterminé » plutôt que de deviner.

## Posture de sécurité

Voir [THREAT-MODEL.md](THREAT-MODEL.md) : garde anti-SSRF, confinement de l'injection d'instructions pour le contenu non fiable, données client locales seulement, enregistrements de vérification infalsifiables.

## Statut

v0.1 — analyseur et rapport fonctionnels; références légales en attente de la vérification humaine ([docs/VERIFICATION.md](docs/VERIFICATION.md)) avant tout usage client.

## Licence

MIT
