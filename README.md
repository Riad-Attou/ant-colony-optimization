# Ant Colony Optimization

Ant Colony Optimization (ACO)

This repository contains an implementation of the Ant Colony Optimization (ACO) algorithm for solving graph-based optimization problems. The algorithm is inspired by the foraging behavior of ants and uses pheromone trails to iteratively improve solutions.

Features

Implementation of the classical ACO algorithm

Configurable parameters: pheromone evaporation rate, $\alpha$ (pheromone influence), $\beta$ (heuristic influence), number of ants, number of iterations

Visualization of the best path and pheromone distribution over time

Modular design that can be extended to other ACO variants (e.g., Ant Colony System, Max-Min Ant System)
## Installation

1. Cloner ce dépôt :

   ```bash
   git clone https://github.com/Riad-Attou/ant_colony.git
   cd ant_colony
   ```

2. Installer les dépendances (un environnement virtuel est recommandé) :

    ```bash
    pip install -r requirements.txt
    ```

## Utilisation

Pour démarrer l'application, lancer `main_pcc.py` ou bien `main_tsp.py`. Dans ces deux fichiers, deux modes sont fournis : un mode avec une ville prédéfinie, et un mode permettant de créer soit-même sa ville (décommenter le code correspondant).

L'utilisation détaillée de l'application est présentée dans le rapport.

## Auteurs

Riad ATTOU : <riad.attou@etu.ec-lyon.fr>\
Asma EL MOUHSINE : <asma.el-mouhsine@etu.ec-lyon.fr>

---

Centrale Lyon - 2024-2025
