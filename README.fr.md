# Balise

**Évaluation de préparation à la Loi 25 fondée sur la preuve, pour les PME québécoises, avec un raisonnement qu'on peut vraiment lire.**

*[English version: README.md](README.md)*

Balise analyse le site web public d'une entreprise et le combine à un court questionnaire pour évaluer sa préparation aux obligations de la Loi 25. Il produit un rapport bilingue (FR/EN) où chaque constat montre ses éléments observés, sa base légale et la force réelle de cette base. L'évaluation complète est aussi consignée dans une piste de vérification lisible par machine.

> Balise est un outil d'autoévaluation de préparation. Ce n'est pas un avis juridique, et il ne rend jamais de verdict de conformité.

## Ce qui le distingue

La plupart des outils automatisés vérifient la surface de votre site : bannière de témoins, présence d'une politique. Le problème, c'est que l'essentiel de la Loi 25 se trouve ailleurs. Le registre des incidents, les ÉFVP pour chaque fournisseur SaaS hébergé aux États-Unis, les contrats de mandataires, les déclarations biométriques. Balise évalue les deux couches :

- **Module A, analyse externe :** politique de confidentialité (présence et contenu), publication du responsable, indicateurs de témoins et de consentement, exposition linguistique.
- **Module B, questionnaire organisationnel :** registre d'incidents, ÉFVP, ententes de transfert, contrats de fournisseurs, biométrie, décisions automatisées, mineurs, portabilité, et plus.

32 vérifications au total, chacune rattachée à un article de loi ou à une orientation du régulateur, et chaque référence vérifiée par un humain contre le texte officiel consolidé sur LégisQuébec. Quand la loi ou le régulateur bouge, la barrière de vérification se rouvre : c'est arrivé en août 2026, quand les lignes directrices 2025 de la CAI sur le recrutement sont entrées au catalogue seulement après une relecture des sources officielles.

Trois règles de conception qu'on s'impose :

1. **Niveaux d'autorité.** Chaque vérification est étiquetée selon la force de sa base légale : `LOI` (texte légal explicite), `CAI` (attente du régulateur) ou `INTERPRÉTATION` (lecture convergente des cabinets). Les points contestés sont rapportés à leur juste force, jamais gonflés. Le marché de la conformité est plein d'affirmations confiantes qui ne survivent pas à une lecture de la loi, et on préfère être précis plutôt que bruyants. Les détails et les preuves sont dans [docs/methodology.md](docs/methodology.md).
2. **Aucune note de conformité.** Le rapport montre une posture de préparation par domaine, jamais un pourcentage unique. Le raisonnement derrière ce refus est aussi dans la documentation.
3. **Une piste de vérification lisible.** Si votre entreprise automatise des décisions, la Loi 25 s'attend à ce que vous puissiez les expliquer. Balise est lui-même un évaluateur automatisé, donc il a le même problème, et il livre la réponse intégrée : les éléments observés et le raisonnement de chaque constat sont consignés dans une piste JSONL chaînée par hachage, dont l'empreinte finale est imprimée dans le rapport lui-même : la cohérence entre le rapport et la piste peut donc être vérifiée. Cela établit l'intégrité entre les deux artefacts, pas quelle version a été émise à l'origine ([docs/VERIFICATION-TRAIL.md](docs/VERIFICATION-TRAIL.md) énonce exactement ce que ça garantit, par paliers, sans gonflage). L'outil est un exemple fonctionnel de la traçabilité qu'il évalue.

## Utilisation

```bash
pip install -e .
balise scan https://www.exemple.com --out ./mandat-001
# avec le questionnaire organisationnel :
balise scan https://www.exemple.com --intake intake/rempli.yaml --out ./mandat-001
```

Les vérifications déterministes s'exécutent sans aucune configuration. Les vérifications de jugement (langage clair, couverture des divulgations) passent par un moteur IA optionnel. Sans lui, elles rapportent honnêtement « indéterminé » plutôt que de deviner.

Deux options utiles : `--also <url>` ajoute à l'analyse une page que le robot manquerait (un formulaire d'inscription, une page de portail), et `--mini` produit un aperçu gratuit à partir des seules vérifications déterministes.

### Vérifier une évaluation livrée — sans serveur, sans compte, sans Balise

Chaque mandat est livré comme un paquet : le rapport, le sommaire visuel, la piste de vérification chaînée par hachage, les preuves archivées sur lesquelles chaque constat s'appuie, et un manifeste écrit en dernier qui prend l'empreinte de l'ensemble. Quiconque détient le paquet peut le vérifier hors ligne :

```bash
balise verify ./mandat-001
```

La liste de contrôle parcourt tout le paquet — intégrité de la chaîne, chaque artefact contre son empreinte, les preuves archivées contre la piste — et se termine par un verdict qui nomme exactement ce qui a été établi (`SELF-CONSISTENT`, et avec les sceaux, `+ ANCHORED (block N)` et `+ SIGNED (key: …)`). Changez un seul caractère n'importe où et la ligne correspondante passe au rouge. Essayez-le sur le mandat d'exemple dans [samples/demo/out](samples/demo/out).

Les sceaux permettent au paquet de prouver plus que sa cohérence interne : `balise seal` engage le manifeste dans Bitcoin via OpenTimestamps (gratuit, sans portefeuille — dit *quand* il existait) et applique la signature de l'émetteur (dit *qui* l'a émis; l'empreinte de la clé est publiée dans [docs/SIGNING.md](docs/SIGNING.md) et dans chaque lettre de mandat). Ce que chaque affirmation établit — et n'établit pas — est détaillé dans [docs/VERIFICATION-TRAIL.md](docs/VERIFICATION-TRAIL.md), sans gonflage.

La conception de la piste et du paquet suit le canon [loxodonta](https://github.com/Acquiredl/loxodonta), un enregistreur de vol pour pipelines d'agents IA où toute altération est détectable, et dont les registres de décisions gouvernent les niveaux de preuve, le manifeste du paquet et les signatures d'émetteur. Balise en est la première conception dérivée.

## Construit avec l'IA, vérifié par un humain

Balise est construit avec assistance IA, et six de ses vérifications utilisent un moteur IA au moment de l'évaluation. On traite ces deux faits comme des choses à encadrer, pas à cacher :

- Chaque référence légale a été vérifiée par un humain contre le texte officiel sur LégisQuébec avant tout usage client ([docs/VERIFICATION.md](docs/VERIFICATION.md)).
- Le moteur de jugement ne peut pas inventer une obligation. La liste des vérifications est fermée, les questions légales sont des textes rédigés, et la base légale vient toujours du catalogue, jamais du modèle.
- Les citations retournées par le moteur sont vérifiées contre le texte récupéré. Une citation introuvable est retirée, et le retrait est indiqué dans le constat.
- Sans moteur configuré, les vérifications de jugement rapportent « indéterminé » plutôt que de deviner.

L'historique du code affiche la co-rédaction ouvertement. Un outil qui demande à votre entreprise d'être transparente sur ses traitements automatisés doit s'imposer la même exigence.

## Limites assumées

Ce que cette version ne fait pas encore, pour que vous ne l'appreniez pas à vos dépens :

- L'analyse des témoins est statique. Balise voit quels scripts de suivi sont livrés dans la page et si une plateforme de consentement est présente, mais il ne lance pas de navigateur pour confirmer ce qui s'active avant le consentement. Les constats le disent clairement.
- L'obligation de diffusion de la politique (la faire réellement parvenir aux personnes, pas seulement la publier) ne s'observe pas depuis une analyse de site. Elle est couverte par le questionnaire.
- Les réponses du Module B sont autodéclarées. Balise les consigne comme telles et ne prétend jamais avoir vérifié les documents.

## Posture de sécurité

Voir [THREAT-MODEL.md](THREAT-MODEL.md) : garde anti-SSRF, confinement de l'injection d'instructions pour le contenu non fiable, données client locales seulement, piste de vérification chaînée où toute altération est détectable.

## Statut

v0.1. Analyseur et rapport fonctionnels. Références légales vérifiées contre LégisQuébec (barrière fermée le 2026-08-23; rouverte et refermée le 2026-08-24 pour les lignes directrices de la CAI sur le recrutement, voir [docs/VERIFICATION.md](docs/VERIFICATION.md)). C'est encore jeune, et ça va évoluer avec le projet.

## Licence

MIT. Questions ou commentaires, ouvrez un issue. Ça fait toujours plaisir de jaser.
