# Rapport Après Normalisation

## Contexte

Ce rapport présente les résultats obtenus après l'étape de normalisation et d'enrichissement du dataset à l'aide du script `notebooks/03_normalisation.py`.

L'objectif de cette phase était de transformer le dataset nettoyé en dataset enrichi, avec des variables supplémentaires directement exploitables pour l'analyse, la visualisation et la recommandation.

## Fichiers concernés

- Entrée : `output/anime_cleaned.csv`
- Sortie : `output/anime_gold.csv`

## Résultats globaux

### Dimensions

- Dataset d'entrée : 17 562 lignes, 38 colonnes
- Dataset de sortie : 17 562 lignes, 48 colonnes

Le nombre de lignes reste inchangé, ce qui est cohérent puisque cette étape n'a pas pour but de filtrer les observations, mais d'ajouter de l'information métier.

### Nombre de nouvelles variables

- `10` nouvelles features ont été créées

## Features créées

### 1. `weighted_score`

Cette variable combine le score moyen d'un anime avec sa base de membres :

`weighted_score = score × log10(members + 1)`

L'idée est d'éviter qu'un anime très bien noté mais très peu vu soit automatiquement considéré comme plus important qu'un anime bien noté et massivement populaire.

Top 5 observé :

- `Fullmetal Alchemist: Brotherhood`
- `Steins;Gate`
- `Hunter x Hunter (2011)`
- `Kimi no Na wa.`
- `Death Note`

Cette feature est utile pour construire un classement plus robuste que le score brut.

### 2. `drop_ratio`

Cette variable mesure le niveau d'abandon :

`drop_ratio = dropped / (dropped + completed)`

Résultats observés :

- moyenne : `17.48 %`
- médiane : `9.26 %`

Cette différence entre moyenne et médiane suggère que certains animes concentrent des taux d'abandon très élevés, ce qui peut constituer un signal intéressant pour l'analyse de rétention.

### 3. `score_category`

Le score a été discrétisé en quatre catégories :

- `Mauvais`
- `Moyen`
- `Bon`
- `Excellent`

Distribution observée :

- `Mauvais` : 513
- `Moyen` : 5 603
- `Bon` : 5 772
- `Excellent` : 533

Cette variable simplifie les analyses segmentées et peut être utile pour du reporting ou des visualisations.

### 4. `main_studio` et `studio_tier`

Le premier studio renseigné a été extrait comme studio principal, puis classé en trois niveaux :

- `Top`
- `Mid`
- `Indie`

Répartition observée :

- `Top` : 6 606 animes
- `Mid` : 2 534 animes
- `Indie` : 1 343 animes

Top 5 studios les plus représentés :

- `Toei Animation`
- `Sunrise`
- `J.C.Staff`
- `Madhouse`
- `Production I.G`

Cette transformation permet de simplifier l'analyse des studios et de créer des segments métier plus faciles à exploiter.

### 5. `year` et `decade`

Les dates de diffusion ont permis d'extraire :

- l'année de diffusion
- la décennie

La distribution montre une forte concentration des animes dans les années 2000 et surtout 2010, ce qui est cohérent avec l'explosion de la production récente.

Constats marquants :

- les années 2010 dominent très largement
- les années 2000 arrivent ensuite
- les décennies anciennes restent très marginales

Ces variables seront particulièrement utiles pour l'analyse temporelle du catalogue.

### 6. `n_genres` et `main_genre`

Deux variables ont été créées à partir de la colonne `genres` :

- `n_genres` : nombre de genres associés à un anime
- `main_genre` : premier genre déclaré

Résultat observé :

- moyenne : `2.9` genres par anime

Top genres principaux :

- `Action`
- `Comedy`
- `Adventure`
- `Music`
- `Hentai`
- `Kids`

Ces variables sont très utiles pour segmenter rapidement les contenus et pour préparer des systèmes de recommandation basés sur le contenu.

### 7. `engagement_ratio`

Cette variable mesure le niveau d'engagement communautaire :

`engagement_ratio = favorites / members`

Résultat observé :

- moyenne : `0.0031`

Les animes les plus engageants parmi ceux ayant au moins 10 000 membres incluent notamment :

- `One Piece`
- `Hunter x Hunter (2011)`
- `Steins;Gate`
- `Fullmetal Alchemist: Brotherhood`

Cette feature apporte une lecture différente de la popularité brute, car elle mesure l'intensité de l'attachement de la communauté.

## Analyse globale

L'étape de normalisation enrichit fortement la valeur analytique du dataset. Le fichier de sortie n'est plus seulement un dataset propre : il devient un dataset métier.

Les principales améliorations apportées sont :

- création d'indicateurs synthétiques plus faciles à interpréter
- transformation de variables complexes en catégories exploitables
- ajout d'une dimension temporelle
- ajout d'une dimension de popularité, de rétention et d'engagement
- meilleure préparation pour les analyses exploratoires avancées

Le dataset `anime_gold.csv` constitue donc une base beaucoup plus adaptée à :

- la visualisation
- le reporting
- la création de dashboards
- la recommandation hybride
- l'analyse métier du catalogue

## Limites observées

Même si le résultat est solide, quelques points méritent encore attention :

- certaines features reposent sur des données manquantes déjà présentes dans le dataset nettoyé
- la logique de `drop_ratio` peut surestimer les séries longues encore en cours
- la classification des studios selon le premier studio uniquement simplifie la réalité
- la variable `duration_minutes` n'a pas été réellement produite ici, car la colonne `duration` a déjà été interprétée comme non textuelle dans ce run

## Conclusion

Après la normalisation, le projet dispose désormais d'un dataset enrichi, cohérent et beaucoup plus utile pour les prochaines étapes.

Le fichier `output/anime_gold.csv` représente une version analytique du dataset, prête pour :

- la validation finale
- l'intégration dans Elasticsearch
- la visualisation dans Grafana
- la création d'un moteur de recommandation

Cette étape marque le passage d'un dataset nettoyé à un dataset réellement exploitable pour des usages data et produit.
