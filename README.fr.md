# Balise

**Évaluation de préparation à la Loi 25 pour les PME québécoises, avec un raisonnement qu'on peut vraiment lire.**

*[English version: README.md](README.md)*

Balise analyse le site web public d'une entreprise et le combine à un court questionnaire pour évaluer sa préparation aux obligations de la Loi 25. Il produit un rapport bilingue (FR/EN) où chaque constat montre ses éléments observés, sa base légale et la force réelle de cette base. L'évaluation complète est aussi consignée dans une piste de vérification lisible par machine.

> Balise est un outil d'autoévaluation de préparation. Ce n'est pas un avis juridique, et il ne rend jamais de verdict de conformité.

## Ce qui le distingue

La plupart des outils automatisés vérifient la surface de votre site : bannière de témoins, présence d'une politique. Le problème, c'est que l'essentiel de la Loi 25 se trouve ailleurs. Le registre des incidents, les ÉFVP pour chaque fournisseur SaaS hébergé aux États-Unis, les contrats de mandataires, les déclarations biométriques. Balise évalue les deux couches :

- **Module A, analyse externe :** politique de confidentialité (présence et contenu), publication du responsable, indicateurs de témoins et de consentement, exposition linguistique.
- **Module B, questionnaire organisationnel :** registre d'incidents, ÉFVP, ententes de transfert, contrats de fournisseurs, biométrie, décisions automatisées, mineurs, portabilité, et plus.

29 vérifications au total, chacune rattachée à un article de loi ou à une orientation du régulateur, et chaque référence vérifiée par un humain contre le texte officiel consolidé sur LégisQuébec.

Trois règles de conception qu'on s'impose :

1. **Niveaux d'autorité.** Chaque vérification est étiquetée selon la force de sa base légale : `LOI` (texte légal explicite), `CAI` (attente du régulateur) ou `INTERPRÉTATION` (lecture convergente des cabinets). Les points contestés sont rapportés à leur juste force, jamais gonflés. Le marché de la conformité est plein d'affirmations confiantes qui ne survivent pas à une lecture de la loi, et on préfère être précis plutôt que bruyants. Les détails et les preuves sont dans [docs/methodology.md](docs/methodology.md).
2. **Aucune note de conformité.** Le rapport montre une posture de préparation par domaine, jamais un pourcentage unique. Le raisonnement derrière ce refus est aussi dans la documentation.
3. **Une piste de vérification lisible.** Si votre entreprise automatise des décisions, la Loi 25 s'attend à ce que vous puissiez les expliquer. Balise est lui-même un évaluateur automatisé, donc il a le même problème, et il livre la réponse intégrée : les éléments observés et le raisonnement de chaque constat sont consignés en JSONL infalsifiable et annexés au rapport. L'outil est un exemple fonctionnel de la traçabilité qu'il évalue.

## Utilisation

```bash
pip install -e .
balise scan https://www.exemple.com --out ./mandat-001
# avec le questionnaire organisationnel :
balise scan https://www.exemple.com --intake intake/rempli.yaml --out ./mandat-001
```

Les vérifications déterministes s'exécutent sans aucune configuration. Les vérifications de jugement (langage clair, couverture des divulgations) passent par un moteur IA optionnel. Sans lui, elles rapportent honnêtement « indéterminé » plutôt que de deviner.

## Limites assumées

Ce que cette version ne fait pas encore, pour que vous ne l'appreniez pas à vos dépens :

- L'analyse des témoins est statique. Balise voit quels scripts de suivi sont livrés dans la page et si une plateforme de consentement est présente, mais il ne lance pas de navigateur pour confirmer ce qui s'active avant le consentement. Les constats le disent clairement.
- L'obligation de diffusion de la politique (la faire réellement parvenir aux personnes, pas seulement la publier) ne s'observe pas depuis une analyse de site. Elle est couverte par le questionnaire.
- Les réponses du Module B sont autodéclarées. Balise les consigne comme telles et ne prétend jamais avoir vérifié les documents.

## Posture de sécurité

Voir [THREAT-MODEL.md](THREAT-MODEL.md) : garde anti-SSRF, confinement de l'injection d'instructions pour le contenu non fiable, données client locales seulement, enregistrements de vérification infalsifiables.

## Statut

v0.1. Analyseur et rapport fonctionnels. Références légales vérifiées contre LégisQuébec (barrière de vérification fermée le 2026-08-23, voir [docs/VERIFICATION.md](docs/VERIFICATION.md)). C'est encore jeune, et ça va évoluer avec le projet.

## Licence

MIT. Questions ou commentaires, ouvrez un issue. Ça fait toujours plaisir de jaser.
