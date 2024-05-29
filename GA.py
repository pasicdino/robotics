from deap import base, creator, tools, algorithms
import random
import csv

from Controller import Controller

controller = Controller()

# Define the problem as a maximization problem
creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

# Create toolbox
toolbox = base.Toolbox()
toolbox.register("attr_float", random.uniform, -1, 1)  # Assuming weights and biases are initialized between -1 and 1
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_float, 410)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

# Define the output file names
logbook_filename = 'logbook.csv'
individual_log_filename = 'individual_log.csv'
best_individual_filename = 'best_individual.txt'

# Open the logbook file for writing
with open(logbook_filename, mode='w', newline='') as logbook_file, \
        open(individual_log_filename, mode='w', newline='') as individual_log_file:
    logbook_writer = csv.writer(logbook_file)
    individual_log_writer = csv.writer(individual_log_file)

    # Write headers
    logbook_writer.writerow(["gen", "nevals", "avg", "std", "min", "max"])
    individual_log_writer.writerow(["gen", "individual_id", "weights", "fitness"])

    # Evaluation function
    def run_simulation(individual):
        fitness = controller.simulate(individual)  # Replace with your actual simulation call
        return fitness

    def evaluate(individual):
        fitness = run_simulation(individual)
        return fitness,

    toolbox.register("evaluate", evaluate)

    toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=0.1, indpb=0.1)  # Increased indpb from 0.05 to 0.1
    toolbox.register("select", tools.selRoulette)

    # Create population
    population = toolbox.population(n=50)

    # Create statistics object and logbook
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", lambda fits: sum(f[0] for f in fits) / len(fits))
    stats.register("std", lambda fits: (sum((f[0] ** 2 for f in fits)) / len(fits) - (
                sum(f[0] for f in fits) / len(fits)) ** 2) ** 0.5)
    stats.register("min", lambda fits: min(f[0] for f in fits))
    stats.register("max", lambda fits: max(f[0] for f in fits))

    logbook = tools.Logbook()
    logbook.header = ["gen", "nevals"] + stats.fields

    # Run genetic algorithm
    for gen in range(1, 80):
        # Select the next generation individuals
        offspring = toolbox.select(population, len(population))
        # Clone the selected individuals
        offspring = list(map(toolbox.clone, offspring))

        # Apply crossover and mutation on the offspring
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < 0.5:
                toolbox.mate(child1, child2)
                del child1.fitness.values
                del child2.fitness.values

        for mutant in offspring:
            if random.random() < 0.2:
                toolbox.mutate(mutant)
                del mutant.fitness.values

        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        for ind in invalid_ind:
            ind.fitness.values = toolbox.evaluate(ind)
            individual_id = id(ind)
            print(ind.fitness.values[0])
            individual_log_writer.writerow([gen, individual_id, list(ind), ind.fitness.values[0]])

        # Update the population
        population[:] = offspring

        # Gather all the fitnesses in one list and print the stats
        fits = [ind.fitness.values[0] for ind in population]

        record = stats.compile(population)
        logbook.record(gen=gen, nevals=len(invalid_ind), **record)
        logbook_writer.writerow([gen, len(invalid_ind), record['avg'], record['std'], record['min'], record['max']])

    # Get the best individual
    best_individual = tools.selBest(population, k=1)[0]

    # Write the best individual to a file
    with open(best_individual_filename, mode='w') as best_individual_file:
        best_individual_file.write(f"Best individual is: {best_individual}\n")
        best_individual_file.write(f"Fitness: {best_individual.fitness.values}\n")

    # Print the best individual
    print("Best individual is: ", best_individual)
    print("Fitness: ", best_individual.fitness.values)

    # Print logbook
    print(logbook)
