# Rapport Après Exploration

## Contexte

Ce rapport synthétise les principaux constats obtenus après l'exploration initiale des données du projet AniData Lab. L'objectif de cette étape était de vérifier la disponibilité des fichiers, comprendre leur structure, identifier les anomalies de qualité et préparer l'étape de nettoyage.

## Jeux de données explorés

Trois fichiers ont été analysés :

- `data/anime.csv`
- `data/anime_with_synopsis.csv`
- `data/rating_complete.csv`

### Volumétrie observée

- `anime.csv` : 17 562 lignes, 35 colonnes
- `anime_with_synopsis.csv` : 16 214 lignes, 5 colonnes
- `rating_complete.csv` : 57 633 278 lignes, 3 colonnes

Cette volumétrie est suffisante pour construire un pipeline data réaliste, avec à la fois des métadonnées riches sur les animes et une base massive d'interactions utilisateurs.

## Principaux constats sur `anime.csv`

Le fichier `anime.csv` est globalement bien rempli, sans valeurs manquantes classiques détectées par défaut. En revanche, l'exploration a mis en évidence de nombreuses valeurs manquantes deguisées, notamment sous la forme :

- `Unknown`
- `0` pour certains scores
- chaînes ambiguës dans des colonnes qui devraient être numériques

Plusieurs colonnes importantes sont stockées sous forme de texte alors qu'elles correspondent à des valeurs numériques :

- `Score`
- `Episodes`
- `Ranked`
- `Score-1` à `Score-10`

L'exploration a également montré que certaines colonnes contiennent des listes encodées dans une seule cellule :

- `Genres`
- `Producers`
- `Licensors`
- `Studios`

Ces colonnes demandent une normalisation avant toute exploitation avancée.

## Principaux constats sur `anime_with_synopsis.csv`

Le fichier de synopsis est plutôt propre.

- 16 214 lignes
- seulement 8 synopsis manquants
- aucun doublon exact détecté

Le point principal d'attention est le nom de colonne `sypnopsis`, qui contient une faute de frappe. Cette particularité doit être prise en compte dans les scripts de fusion et de nettoyage.

## Principaux constats sur `rating_complete.csv`

Le fichier de ratings représente la partie la plus volumineuse et la plus utile pour un futur système de recommandation.

Sur l'échantillon analysé :

- aucune valeur manquante
- 2 825 utilisateurs uniques
- 11 300 animes uniques
- notes comprises entre 1 et 10

La distribution des notes montre un biais positif net :

- les notes `7`, `8`, `9` et `10` sont largement majoritaires
- la moyenne observée sur l'échantillon est de `7.55`
- la médiane est de `8`

Cela suggère que les utilisateurs notent davantage les contenus qu'ils apprécient, ce qui est un comportement classique mais important à prendre en compte pour la modélisation.

## Problèmes détectés après exploration

- valeurs manquantes déguisées dans plusieurs colonnes
- types de données incohérents
- colonnes multi-valuées non normalisées
- risque de biais de popularité dans les scores et ratings
- présence de colonnes textuelles nécessitant un nettoyage léger
- dates stockées sous plusieurs formats

## Analyse globale

Le dataset est exploitable et suffisamment riche pour la suite du projet. Les données ne sont pas "mauvaises", mais elles nécessitent une phase de préparation sérieuse avant toute analyse avancée, indexation ou recommandation.

L'exploration a confirmé que :

- la base anime est assez complète
- les synopsis enrichissent utilement les métadonnées
- les ratings utilisateurs apportent une vraie valeur pour la recommandation collaborative

## Conclusion

Après exploration, le projet dispose d'une base solide pour la suite. Les travaux prioritaires identifiés sont :

- convertir correctement les colonnes numériques
- remplacer les valeurs `Unknown` par des valeurs manquantes cohérentes
- normaliser les colonnes textuelles
- nettoyer les colonnes multi-valuées
- préparer les données pour le feature engineering et la recommandation

L'étape suivante logique est donc le nettoyage structuré du dataset, afin d'obtenir une base unifiée, cohérente et prête à être exploitée.
