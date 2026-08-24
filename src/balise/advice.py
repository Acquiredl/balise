"""Client-facing copy per check: plain-language title, why it matters, and
the first action — in the owner's language, not the statute's.

This is authored content, tier-consistent with the registry: risks are stated
concretely but never as fine-threats, and actions are first steps, not legal
advice. priority: 1 = urgent (statutory + enforcement-active or externally
visible), 2 = important paper obligations, 3 = good practice / lower likelihood.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ClientCopy:
    plain_fr: str
    plain_en: str
    risk_fr: str
    risk_en: str
    action_fr: str
    action_en: str
    priority: int  # 1 urgent, 2 important, 3 recommended


CLIENT_COPY: dict[str, ClientCopy] = {
    "A1": ClientCopy(
        "Votre politique de confidentialité en ligne",
        "Your privacy policy online",
        "Sans politique publiée, chaque visiteur qui remplit un formulaire vous confie ses renseignements sans savoir ce que vous en faites — et c'est la première chose qu'un client, un assureur ou un plaignant ira vérifier.",
        "Without a published policy, every visitor filling a form hands you their information blind — and it's the first thing a client, insurer or complainant will check.",
        "Publier une politique claire sur le site (le guide de la CAI fournit la structure).",
        "Publish a clear policy on the site (the CAI's guide provides the structure).",
        1),
    "A2": ClientCopy(
        "Ce que votre politique explique (ou pas)",
        "What your policy explains (or doesn't)",
        "Une politique vague ne protège personne : si elle ne dit pas quoi vous recueillez, pourquoi, et qui y a accès, elle ne remplit pas son rôle et mine la confiance au premier regard sérieux.",
        "A vague policy protects no one: if it doesn't say what you collect, why, and who has access, it fails its job and erodes trust at the first serious look.",
        "Compléter la politique avec les éléments manquants relevés dans le rapport.",
        "Complete the policy with the missing elements identified in the report.",
        2),
    "A3": ClientCopy(
        "La personne responsable, affichée et joignable",
        "Your privacy officer, named and reachable",
        "La loi exige qu'on puisse trouver et joindre votre responsable. Si personne n'est affiché, chaque demande ou plainte part dans le vide — et le délai légal de 30 jours court quand même.",
        "The law requires your officer be findable and reachable. If no one is posted, every request or complaint goes nowhere — and the legal 30-day clock runs anyway.",
        "Publier le titre et un moyen de contact du responsable sur le site.",
        "Publish the officer's title and a contact means on the site.",
        1),
    "A4": ClientCopy(
        "L'information sur vos pratiques internes",
        "Information about your internal practices",
        "Vous devez décrire publiquement comment vous gouvernez les renseignements (conservation, destruction, plaintes). Son absence signale qu'il n'y a probablement rien derrière.",
        "You must publicly describe how you govern information (retention, destruction, complaints). Its absence signals there's probably nothing behind the curtain.",
        "Publier un résumé clair de vos pratiques de gouvernance.",
        "Publish a clear summary of your governance practices.",
        2),
    "A5": ClientCopy(
        "Les témoins (cookies) avant consentement",
        "Cookies firing before consent",
        "Le régulateur s'attend à ce que les traceurs non essentiels soient inactifs tant que le visiteur n'a pas dit oui. Des traceurs qui partent tout seuls, c'est des données qui partent chez Google ou Meta sans permission.",
        "The regulator expects non-essential trackers to stay off until the visitor says yes. Trackers firing on their own means data leaving for Google or Meta without permission.",
        "Vérifier le comportement réel de la bannière et des traceurs au chargement.",
        "Verify the real behavior of the banner and trackers at load.",
        2),
    "A6": ClientCopy(
        "Dire quelles technologies vous suivent",
        "Disclosing what technology tracks people",
        "Si votre site peut identifier, localiser ou profiler quelqu'un, vous devez le dire avant, et expliquer comment l'activer ou non. Le silence ici est une non-conformité directe au texte de loi.",
        "If your site can identify, locate or profile someone, you must say so first and explain how it's turned on. Silence here is direct non-compliance with the statute's text.",
        "Ajouter la divulgation des technologies de suivi et leurs réglages à la politique.",
        "Add tracking-technology disclosure and its settings to the policy.",
        2),
    "A7": ClientCopy(
        "La version française de votre site",
        "The French version of your site",
        "Un site commercial sans version française équivalente expose à des plaintes à l'OQLF (3 000 $ à 30 000 $ par infraction) — un risque distinct de la Loi 25, mais qui frappe la même vitrine.",
        "A commercial site without an equivalent French version invites OQLF complaints ($3,000-$30,000 per offence) — a separate risk from Law 25, hitting the same storefront.",
        "Offrir le français à conditions au moins équivalentes, politique et conditions comprises.",
        "Offer French on at-least-equivalent terms, policy and terms included.",
        1),
    "A8": ClientCopy(
        "Le consentement dans vos formulaires",
        "Consent in your forms",
        "Un consentement mal demandé est invalide — donc tout ce qui repose dessus (envois, partages) devient sans permission. La CAI a 8 critères; en manquer un seul annule le consentement.",
        "Badly requested consent is invalid — so everything resting on it (sends, sharing) becomes permission-less. The CAI has 8 criteria; missing one voids the consent.",
        "Revoir chaque formulaire : une finalité par consentement, présenté séparément.",
        "Review each form: one purpose per consent, presented separately.",
        2),
    "A9": ClientCopy(
        "Annoncer les changements de politique",
        "Announcing policy changes",
        "Modifier la politique sans avis revient à changer les règles sans le dire : le consentement donné hier ne couvre pas les pratiques d'aujourd'hui.",
        "Changing the policy without notice is changing the rules silently: yesterday's consent doesn't cover today's practices.",
        "Prévoir un avis de modification (date de mise à jour + annonce visible).",
        "Add an amendment notice practice (update date + visible announcement).",
        3),
    "A10": ClientCopy(
        "Exiger seulement le nécessaire dans les formulaires",
        "Requiring only what's necessary in forms",
        "Refuser un service parce qu'un client ne donne pas un renseignement non nécessaire est interdit — et en cas de doute, la loi tranche contre vous : le renseignement est réputé non nécessaire.",
        "Refusing service because a client withholds unnecessary information is prohibited — and in doubt, the law rules against you: the information is deemed unnecessary.",
        "Passer chaque champ obligatoire au test : nécessaire à la finalité, ou pas?",
        "Test every required field: necessary for the purpose, or not?",
        3),
    "B1": ClientCopy(
        "Le registre des incidents",
        "The incident register",
        "Chaque erreur d'envoi, chaque accès non autorisé doit être consigné — même mineur. Sans registre, votre premier incident sérieux vous trouve sans historique, sans réflexes, et sans preuve de diligence devant la CAI ou l'assureur.",
        "Every misdirected email, every unauthorized access must be logged — even minor. Without a register, your first serious incident finds you with no history, no reflexes, and no proof of diligence for the CAI or your insurer.",
        "Créer le registre (8 éléments prescrits) et brancher le processus de réponse dessus.",
        "Create the register (8 prescribed elements) and wire the response process to it.",
        1),
    "B2": ClientCopy(
        "L'évaluation avant tout nouveau système",
        "The assessment before any new system",
        "Chaque nouveau logiciel qui touche des renseignements personnels exige une évaluation préalable (ÉFVP). L'adopter sans évaluer, c'est accumuler silencieusement des systèmes non conformes.",
        "Every new software touching personal information requires a prior assessment (PIA). Adopting without assessing quietly stockpiles non-compliant systems.",
        "Instaurer une ÉFVP légère et proportionnée pour chaque nouveau projet (méthode CAI).",
        "Set up a light, proportionate PIA for each new project (CAI's method).",
        2),
    "B3": ClientCopy(
        "Vos données chez des fournisseurs hors Québec",
        "Your data at vendors outside Quebec",
        "Chaque outil hébergé aux États-Unis (courriel, CRM, infonuagique) transporte des renseignements de vos clients hors Québec. Sans évaluation ni entente écrite, chacun de ces flux est une communication non encadrée de données personnelles.",
        "Every US-hosted tool (email, CRM, cloud) carries your clients' information outside Quebec. Without an assessment and written agreement, each flow is an unframed communication of personal data.",
        "Inventorier les fournisseurs hors Québec, puis ÉFVP + entente écrite pour chacun.",
        "Inventory out-of-Quebec vendors, then PIA + written agreement for each.",
        1),
    "B4": ClientCopy(
        "Les clauses de vos contrats de fournisseurs",
        "Your vendor contracts' clauses",
        "Si votre fournisseur perd vos données et que le contrat ne l'oblige ni à protéger, ni à aviser, ni à détruire à l'échéance, c'est vous qui restez responsable devant vos clients.",
        "If your vendor loses your data and the contract requires no protection, no notice, no end-of-term destruction, you remain the one answerable to your clients.",
        "Ajouter les clauses de l'art. 18.3 aux contrats (modèle dans nos recommandations).",
        "Add the s. 18.3 clauses to contracts (template in our recommendations).",
        2),
    "B5": ClientCopy(
        "Vos politiques internes",
        "Your internal policies",
        "Qui fait quoi avec les renseignements, combien de temps on les garde, comment on traite une plainte : sans règles écrites, chaque employé improvise — et l'improvisation est indéfendable.",
        "Who does what with information, how long it's kept, how complaints are handled: without written rules, every employee improvises — and improvisation is indefensible.",
        "Rédiger les politiques (cycle de vie, conservation/destruction, plaintes).",
        "Write the policies (lifecycle, retention/destruction, complaints).",
        2),
    "B6": ClientCopy(
        "Biométrie : empreintes, visages",
        "Biometrics: fingerprints, faces",
        "C'est LE domaine où le régulateur agit déjà : des entreprises ont reçu l'ordre de cesser et de détruire leurs systèmes. Un horodateur à empreinte non déclaré 60 jours d'avance est une infraction dès le premier jour.",
        "This is THE area where the regulator already acts: businesses have been ordered to stop and destroy their systems. An undeclared fingerprint time-clock is an offence from day one (60-day prior declaration).",
        "Avant tout projet biométrique : consentement exprès, déclaration à la CAI, solution de rechange offerte.",
        "Before any biometric project: express consent, CAI declaration, alternative offered.",
        1),
    "B7": ClientCopy(
        "Les décisions prises par vos systèmes automatisés",
        "Decisions your automated systems make",
        "Quand un logiciel décide seul (tri, score, refus), la personne a le droit de le savoir, de comprendre pourquoi, et de parler à un humain capable de réviser. Sans ce circuit, chaque décision automatisée est contestable.",
        "When software decides alone (sorting, scoring, refusing), the person has the right to know, understand why, and reach a human who can review. Without that circuit, every automated decision is challengeable.",
        "Recenser les décisions automatisées et prévoir l'avis + le recours humain.",
        "Map automated decisions and add the notice + human recourse.",
        2),
    "B8": ClientCopy(
        "Les renseignements des enfants de moins de 14 ans",
        "Information from children under 14",
        "Un formulaire qu'un enfant peut remplir seul recueille des renseignements sans le consentement parental requis — une non-conformité sensible qui touche directement des mineurs.",
        "A form a child can fill alone collects information without the required parental consent — a sensitive non-compliance directly involving minors.",
        "Vérifier que la collecte auprès des moins de 14 ans passe par le parent.",
        "Ensure collection from under-14s goes through the parent.",
        1),
    "B9": ClientCopy(
        "Remettre leurs données aux gens qui les demandent",
        "Giving people their data when they ask",
        "Depuis 2024, une personne peut exiger ses renseignements dans un format réutilisable. Ne pas pouvoir répondre, c'est un refus réputé — avec les recours qui viennent avec.",
        "Since 2024, a person can demand their information in a reusable format. Being unable to respond is a deemed refusal — with the remedies that follow.",
        "Tester : peut-on exporter les données d'une personne en format structuré?",
        "Test it: can you export one person's data in a structured format?",
        2),
    "B10": ClientCopy(
        "Les renseignements sensibles (santé, finances, intimité)",
        "Sensitive information (health, finances, intimacy)",
        "Les renseignements sensibles exigent un consentement exprès — pas implicite, pas présumé. C'est ici que les fuites font le plus mal aux personnes et à votre réputation.",
        "Sensitive information requires express consent — not implied, not presumed. This is where leaks hurt people, and your reputation, the most.",
        "Identifier les renseignements sensibles détenus et verrouiller le consentement exprès.",
        "Identify the sensitive information you hold and lock in express consent.",
        1),
    "B11": ClientCopy(
        "La formation de votre équipe",
        "Your team's training",
        "La majorité des incidents commencent par un geste humain : mauvaise pièce jointe, mauvais destinataire. Une équipe non formée est votre plus grande surface de fuite.",
        "Most incidents start with a human act: wrong attachment, wrong recipient. An untrained team is your biggest leak surface.",
        "Une sensibilisation courte et récurrente, en commençant par qui touche le plus de RP.",
        "Short, recurring awareness, starting with whoever touches the most PI.",
        3),
    "B12": ClientCopy(
        "Vos mesures de sécurité",
        "Your security measures",
        "La loi exige une sécurité proportionnée à la sensibilité des données — et son absence est une infraction pénale en soi. C'est aussi la première section du questionnaire de votre assureur cyber.",
        "The law requires security proportionate to the data's sensitivity — and its absence is a penal offence in itself. It's also the first section of your cyber insurer's questionnaire.",
        "Évaluer les mesures actuelles contre la sensibilité réelle des données détenues.",
        "Assess current measures against the real sensitivity of the data held.",
        1),
    "B13": ClientCopy(
        "Des données exactes quand elles servent à décider",
        "Accurate data when it's used to decide",
        "Décider sur des données périmées (mauvais dossier, adresse d'il y a 5 ans), c'est se tromper de personne avec des conséquences réelles — et la loi l'interdit expressément.",
        "Deciding on stale data (wrong file, five-year-old address) means wronging a real person with real consequences — and the law expressly prohibits it.",
        "Vérifier l'exactitude au moment de la décision; conserver le dossier 1 an après.",
        "Verify accuracy at decision time; keep the file 1 year after.",
        3),
    "B14": ClientCopy(
        "Détruire ce qui ne sert plus",
        "Destroying what's no longer needed",
        "Chaque renseignement gardé sans raison est un risque gardé sans raison : on ne peut pas fuir ce qu'on a détruit. La loi exige destruction ou anonymisation une fois la fin accomplie.",
        "Every record kept without reason is risk kept without reason: what's destroyed can't leak. The law requires destruction or anonymization once the purpose is done.",
        "Établir un calendrier de destruction branché sur vos fins réelles.",
        "Set a destruction schedule tied to your actual purposes.",
        2),
    "B15": ClientCopy(
        "Vos envois promotionnels",
        "Your promotional sends",
        "Avoir l'adresse de quelqu'un ne donne pas le droit de lui vendre : la loi dit expressément que la prospection n'est jamais une « fin compatible ». Chaque infolettre sans consentement est une utilisation interdite.",
        "Having someone's address doesn't grant the right to sell to them: the law expressly says prospection is never a 'consistent purpose.' Every consent-less newsletter is a prohibited use.",
        "Valider la base de consentement de vos listes; honorer chaque désabonnement immédiatement.",
        "Validate your lists' consent basis; honor every unsubscribe immediately.",
        2),
    "B16": ClientCopy(
        "Répondre aux demandes d'accès en 30 jours",
        "Answering access requests within 30 days",
        "C'est le seul vrai délai ferme de la loi : réponse écrite en 30 jours, sinon le silence vaut refus et ouvre les recours. La plupart des entreprises ne le savent pas — jusqu'à la première demande.",
        "This is the law's one real hard deadline: written reply in 30 days, or silence counts as refusal and opens remedies. Most businesses don't know it — until the first request arrives.",
        "Désigner le circuit : qui reçoit, qui cherche (courriels et tiers inclus), qui répond.",
        "Define the circuit: who receives, who searches (email and third parties included), who replies.",
        1),
    "B17": ClientCopy(
        "Savoir ce que vous détenez",
        "Knowing what you hold",
        "On ne peut pas protéger, détruire ni retrouver ce qu'on n'a pas répertorié. L'inventaire est la fondation de toutes les autres obligations — c'est la pratique n° 1 recommandée par le régulateur.",
        "You can't protect, destroy or retrieve what you haven't mapped. The inventory is the foundation of every other obligation — the regulator's #1 recommended practice.",
        "Faire l'inventaire : quoi, pourquoi, qui y accède, où, combien de temps.",
        "Build the inventory: what, why, who accesses, where, how long.",
        2),
    "B18": ClientCopy(
        "Vos caméras de surveillance",
        "Your surveillance cameras",
        "Des caméras exigent une nécessité documentée par des faits, un affichage, et une conservation limitée (~30 jours). Des images gardées sans règles sont des renseignements personnels qui s'accumulent sans contrôle.",
        "Cameras require fact-documented necessity, signage, and limited retention (~30 days). Footage kept without rules is personal information piling up uncontrolled.",
        "Documenter la nécessité, afficher, limiter la conservation, restreindre l'accès.",
        "Document necessity, post signage, cap retention, restrict access.",
        2),
    "B19": ClientCopy(
        "L'authentification à deux facteurs (MFA)",
        "Two-factor authentication (MFA)",
        "La loi ne nomme pas la MFA, mais votre assureur, oui : c'est la première question des formulaires d'assurance cyber, et une réclamation de plusieurs millions a déjà été refusée parce que la MFA n'était pas complète.",
        "The statute doesn't name MFA, but your insurer does: it's the first question on cyber-insurance forms, and a multi-million-dollar claim has already been denied because MFA wasn't fully in place.",
        "Activer la MFA sur tous les comptes courriel et tous les accès à distance.",
        "Enable MFA on every email account and all remote access.",
        3),
    "B20": ClientCopy(
        "Vos copies de sauvegarde, hors ligne et testées",
        "Your backups, offline and tested",
        "Une sauvegarde branchée en permanence se chiffre avec le reste lors d'un rançongiciel. Les assureurs demandent des copies hors ligne testées; une restauration jamais essayée est un pari, pas un plan.",
        "A permanently connected backup gets encrypted along with everything else in a ransomware attack. Insurers ask for tested offline copies; a never-attempted restore is a bet, not a plan.",
        "Mettre en place des sauvegardes hors ligne des données critiques et tester la restauration.",
        "Set up offline backups of critical data and test restoration.",
        3),
    "B21": ClientCopy(
        "Vos paramètres par défaut",
        "Your default privacy settings",
        "Si votre portail ou votre application offre des réglages de confidentialité, la loi exige que le niveau maximal soit déjà activé à l'arrivée. Un défaut trop bavard fait porter le fardeau au client — et la non-conformité à vous.",
        "If your portal or app offers privacy settings, the law requires the maximum level to be on from the start. A chatty default shifts the burden to the client — and the non-compliance to you.",
        "Vérifier chaque paramètre par défaut de vos produits et régler au niveau le plus protecteur.",
        "Review every default setting in your products and set the most protective level.",
        2),
    "B22": ClientCopy(
        "Le recrutement et vos candidats",
        "Recruiting and your candidates",
        "Le régulateur vient d'encadrer le recrutement : photocopier un permis, exiger le NAS trop tôt ou garder les CV des candidats non retenus sont des gestes courants — et non conformes. Un dossier de candidature est un renseignement personnel comme les autres.",
        "The regulator has just framed recruiting: photocopying a licence, asking for the SIN too early, or keeping unsuccessful candidates' CVs are common practices — and non-compliant. An application file is personal information like any other.",
        "Revoir l'embauche étape par étape et détruire les dossiers des candidats non retenus.",
        "Review hiring stage by stage and destroy unsuccessful candidates' files.",
        2),
}
