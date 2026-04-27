# Rapport Après Nettoyage

## Contexte

Ce rapport présente les résultats obtenus après l'étape de nettoyage appliquée au dataset `anime.csv` via le script `notebooks/03_nettoyage.py`.

L'objectif de cette phase était de transformer un fichier brut en dataset plus propre, plus cohérent et plus simple à exploiter pour les étapes suivantes du projet.

## Fichier traité

- Entrée : `data/anime.csv`
- Sortie : `output/anime_cleaned.csv`

## Résultats globaux

### Dimensions

- Avant nettoyage : 17 562 lignes, 35 colonnes
- Après nettoyage : 17 562 lignes, 38 colonnes

Le nombre de lignes n'a pas changé, ce qui signifie qu'aucune suppression massive n'a été appliquée. Le nombre de colonnes a augmenté car de nouvelles colonnes ont été créées lors de la normalisation des dates et du marquage des anomalies.

### Colonnes ajoutées

- `aired_start`
- `aired_end`
- `is_outlier`

## Transformations effectuées

### 1. Normalisation des noms de colonnes

Toutes les colonnes ont été converties dans un format plus homogène :

- minuscules
- espaces remplacés par `_`
- tirets remplacés par `_`

Exemples :

- `MAL_ID` devient `mal_id`
- `English name` devient `english_name`
- `Score-10` devient `score_10`

Cette étape améliore la lisibilité du dataset et simplifie l'écriture des traitements futurs.

### 2. Vérification des doublons

- aucun doublon exact détecté
- aucun doublon sur la clé `mal_id`

Le dataset d'origine était donc propre sur ce point.

### 3. Traitement des valeurs manquantes déguisées

Le nettoyage a remplacé les valeurs ambiguës comme `Unknown`, `N/A`, `None`, `-` ou chaînes vides par de vrais `NaN`.

Au total :

- `75 470` valeurs textuelles ont été converties en `NaN`

Cette étape est importante car elle permet à pandas et aux futurs traitements de reconnaître correctement les données absentes.

### 4. Correction partielle des types

Certaines colonnes ont été préparées pour un usage numérique plus cohérent, notamment :

- `score`
- `episodes`
- `popularity`
- `members`
- `favorites`
- `watching`
- `completed`
- `on_hold`
- `dropped`
- `plan_to_watch`

Les colonnes entières ont été basculées en type nullable quand cela était possible.

### 5. Nettoyage textuel

Les colonnes textuelles ont été nettoyées par :

- suppression des espaces en début et fin de chaîne
- réduction des espaces multiples
- nettoyage léger sur certaines colonnes de nom

### 6. Normalisation des colonnes multi-valuées

Les colonnes contenant plusieurs valeurs dans une même cellule ont été harmonisées :

- `genres`
- `producers`
- `licensors`
- `studios`

Le nettoyage a permis de supprimer les éléments parasites et de rendre les séparations plus cohérentes.

### 7. Traitement des dates

La colonne `aired` a été découpée en deux champs :

- `aired_start`
- `aired_end`

La colonne `premiered` a été tentée en conversion date, mais le résultat montre que ce champ nécessitera probablement une stratégie spécifique, car son format métier n'est pas un format de date standard.

### 8. Détection des outliers

Une colonne `is_outlier` a été créée pour marquer d'éventuelles valeurs aberrantes.

Résultat du script actuel :

- `0` outlier marqué

Cela signifie surtout que les règles choisies sont encore prudentes et pourront être enrichies plus tard.

## Analyse des données nettoyées

Le fichier nettoyé est plus exploitable qu'à l'origine, mais il reste naturellement des valeurs manquantes. C'est normal : le nettoyage ne doit pas inventer des données qui n'existent pas.

### Colonnes les plus incomplètes après nettoyage

- `premiered` : 17 562 valeurs manquantes
- `licensors` : 13 616
- `english_name` : 10 565
- `aired_end` : 9 809
- `producers` : 7 794
- `studios` : 7 079
- `score` : 5 141

Ces résultats montrent que le nettoyage a surtout révélé l'état réel du dataset plutôt que de le dégrader.

### Qualité obtenue

Après nettoyage :

- les noms de colonnes sont homogènes
- les fausses valeurs connues ont été normalisées
- les types sont plus cohérents
- les colonnes multi-valuées sont plus propres
- les dates ont commencé à être structurées
- le dataset est prêt pour une étape de feature engineering

## Limites observées

Le nettoyage actuel fonctionne, mais il reste quelques points à améliorer :

- mieux gérer la colonne `premiered`, qui ne se convertit pas bien en date classique
- revoir certaines conversions numériques encore incomplètes
- renommer éventuellement `sypnopsis` en `synopsis` dans les datasets fusionnés
- affiner les règles de détection des outliers
- définir une stratégie pour les colonnes très incomplètes

## Conclusion

Cette étape de nettoyage a permis de transformer le dataset brut en une base beaucoup plus claire et plus fiable pour la suite du projet.

Le fichier `output/anime_cleaned.csv` peut désormais servir de base pour :

- le feature engineering
- la fusion avec d'autres sources
- l'indexation
- la visualisation
- la préparation d'un moteur de recommandation

La suite logique du projet consiste à enrichir les variables, créer des indicateurs utiles et préparer des données directement exploitables dans les outils analytiques ou applicatifs.
