from deap import base, creator, tools, algorithms
import random

from Controller import Controller

controller = Controller()

# Define the problem as a maximization problem
creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

# Create toolbox
toolbox = base.Toolbox()
toolbox.register("attr_float", random.uniform, -1, 1)  # Assuming weights and biases are initialized between -1 and 1
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_float, 362)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

# Evaluation function
def run_simulation(individual):
    fitness = controller.simulate(individual)  # Replace with your actual simulation call
    return fitness

def evaluate(individual):
    fitness = run_simulation(individual)
    print(f"Evaluating individual with weights: {individual}")
    print(f"Fitness: {fitness}")
    return fitness,

toolbox.register("evaluate", evaluate)

# Register genetic operators
toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=0.1, indpb=0.05)
toolbox.register("select", tools.selTournament, tournsize=3)

# Create population
population = toolbox.population(n=80)

# Create statistics object and logbook
stats = tools.Statistics(lambda ind: ind.fitness.values)
stats.register("avg", lambda fits: sum(f[0] for f in fits) / len(fits))
stats.register("std", lambda fits: (sum((f[0] ** 2 for f in fits)) / len(fits) - (sum(f[0] for f in fits) / len(fits)) ** 2) ** 0.5)
stats.register("min", lambda fits: min(f[0] for f in fits))
stats.register("max", lambda fits: max(f[0] for f in fits))

logbook = tools.Logbook()
logbook.header = ["gen", "nevals"] + stats.fields

# Run genetic algorithm
result_population, logbook = algorithms.eaSimple(population, toolbox, cxpb=0.5, mutpb=0.2, ngen=36,
                                                 stats=stats, halloffame=None, verbose=True)

# Get the best individual
best_individual = tools.selBest(result_population, k=1)[0]
print("Best individual is: ", best_individual)
print("Fitness: ", best_individual.fitness.values)

# Print logbook
print(logbook)
