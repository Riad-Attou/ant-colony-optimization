# Ant Colony Optimization (ACO)

This repository contains an implementation of the **Ant Colony Optimization (ACO)** algorithm for solving graph-based optimization problems. The algorithm is inspired by the foraging behavior of ants and uses pheromone trails to iteratively improve solutions.

## Features

- Implementation of the classical ACO algorithm  
- Configurable parameters: pheromone evaporation rate, $\alpha$ (pheromone influence), $\beta$ (heuristic influence), number of ants, number of iterations  
- Visualization of the best path and pheromone distribution over time  
- Modular design that can be extended to other ACO variants (e.g., Ant Colony System, Max-Min Ant System)  

## Installation

1. Clone this repository:

    ```bash
    git clone <https://github.com/Riad-Attou/ant_colony.git>
    cd ant_colony
    ```

2. Install the dependencies (a virtual environment is recommended):

    ```bash
    pip install -r requirements.txt
    ```

## Usage

To start the application, run main_pcc.py or main_tsp.py.
Both files provide two modes:

- a mode with a predefined city
- a mode allowing you to create your own city (uncomment the corresponding code)

Detailed usage of the application is presented in the report.

## Authors

Riad ATTOU: <riad.attou@etu.ec-lyon.fr>\
Asma EL MOUHSINE: <asma.el-mouhsine@etu.ec-lyon.fr>

---

Centrale Lyon - 2024–2025
