# Documentation Du Projet

Ce dossier regroupe les rapports produits au fil des étapes de préparation des données du projet AniData Lab.

## Contenu

- `rapport_exploration.md` : synthèse des constats après l'exploration initiale des fichiers sources
- `rapport_nettoyage.md` : bilan des transformations appliquées lors du nettoyage de `anime.csv`
- `rapport_normalisation.md` : rapport sur la normalisation et le feature engineering menés sur le dataset nettoyé
- `rapport_validation.md` : validation finale du dataset enrichi `anime_gold.csv`

## Ordre De Lecture Conseillé

1. `rapport_exploration.md`
2. `rapport_nettoyage.md`
3. `rapport_normalisation.md`
4. `rapport_validation.md`

## Objectif

L'ensemble de ces documents permet de suivre l'évolution du dataset depuis les fichiers bruts jusqu'au fichier final prêt à être exploité pour :

- l'analyse
- la visualisation
- l'indexation
- la recommandation

## Fichiers De Données Principaux

- `data/anime.csv`
- `data/anime_with_synopsis.csv`
- `data/rating_complete.csv`
- `output/anime_cleaned.csv`
- `output/anime_gold.csv`
