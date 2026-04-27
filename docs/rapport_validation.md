# Rapport De Validation Finale

## Contexte

Ce rapport présente la validation finale du dataset enrichi `output/anime_gold.csv`, après les étapes successives d'exploration, de nettoyage et de normalisation.

L'objectif est de vérifier que le fichier final respecte les exigences minimales de qualité attendues pour une exploitation analytique et pour la suite du projet.

## Fichier validé

- Entrée validée : `output/anime_gold.csv`
- Dimensions observées : `17 562 lignes` et `48 colonnes`

## Exigences de validation retenues

La validation finale repose sur les contrôles suivants :

- fichier final présent
- dataset non vide
- absence de doublons exacts
- unicité de la clé `mal_id`
- présence des colonnes métier attendues
- cohérence des scores
- cohérence du ratio d'abandon
- cohérence du ratio d'engagement
- mesure du taux de remplissage restant

## Résultats de validation

### Intégrité générale

- le fichier final est bien présent
- le dataset est correctement chargé
- aucun doublon exact n'a été détecté
- la clé `mal_id` reste unique

Ces résultats valident la stabilité structurelle du fichier final.

### Colonnes obligatoires

Les colonnes attendues pour la suite du projet sont présentes, notamment :

- `mal_id`
- `name`
- `score`
- `genres`
- `episodes`
- `members`
- `favorites`
- `completed`
- `dropped`
- `aired_start`
- `aired_end`
- `weighted_score`
- `drop_ratio`
- `score_category`
- `main_studio`
- `studio_tier`
- `year`
- `decade`
- `n_genres`
- `main_genre`
- `engagement_ratio`

Le dataset final contient donc bien les éléments nécessaires pour l'analyse et le reporting.

### Cohérence des variables calculées

Les contrôles métier principaux sont conformes :

- les valeurs renseignées dans `score` restent dans l'intervalle `1` à `10`
- `drop_ratio` est cohérent et reste compris entre `0` et `1`
- `engagement_ratio` est positif ou nul

Ces résultats confirment que les features créées pendant la normalisation sont globalement fiables.

## Pourcentages de valeurs manquantes restantes

Les valeurs manquantes restantes ne constituent pas nécessairement une erreur. Elles reflètent surtout l'état réel du dataset source. Les principaux taux observés sont :

- `premiered` : `100.00 %`
- `licensors` : `77.53 %`
- `english_name` : `60.16 %`
- `aired_end` : `55.85 %`
- `producers` : `44.38 %`
- `studios` : `40.31 %`
- `main_studio` : `40.31 %`
- `studio_tier` : `40.31 %`
- `score` : `29.27 %`
- `weighted_score` : `29.27 %`
- `score_category` : `29.27 %`
- `source` : `20.31 %`
- `score_9` : `18.03 %`
- `year` : `12.01 %`
- `aired_start` : `12.01 %`
- `decade` : `12.01 %`
- `ranked` : `10.03 %`

## Lecture des résultats

### Ce qui est validé

- la structure finale du dataset est cohérente
- les identifiants sont propres
- les features principales sont bien générées
- le dataset final est exploitable pour la suite du projet

### Ce qui reste imparfait mais acceptable

- plusieurs colonnes métier restent incomplètes
- certaines informations n'existent pas dans la source initiale
- les colonnes dérivées héritent logiquement des manques des colonnes d'origine

Par exemple :

- `weighted_score` dépend directement de `score`
- `main_studio` et `studio_tier` dépendent de `studios`
- `year` et `decade` dépendent de la disponibilité d'une date exploitable

## Conclusion

La validation finale confirme que `anime_gold.csv` respecte les exigences essentielles du projet :

- fichier exploitable
- structure stable
- identifiants propres
- features métier présentes
- cohérence globale des variables calculées

Le dataset peut donc être considéré comme **valide pour la suite du pipeline**, notamment pour :

- la visualisation
- la validation métier
- l'indexation
- l'alimentation d'un moteur de recommandation

Les valeurs manquantes restantes doivent être interprétées comme une limite de la donnée source et non comme un échec du traitement. Le fichier final est suffisamment propre et structuré pour constituer une base de travail solide.
