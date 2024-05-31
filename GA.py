import numpy as np
from RNN import RNN

#Class containing GA and all functions associated with it
#Author: Dino
class GA:
    def __init__(self, population_size, mutation_rate, crossover_rate, generations, nn_class, elite_size=2):
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.generations = generations
        self.nn_class = nn_class
        self.elite_size = elite_size

    #Method that inits population. Since we have many weights, we can go over all of them 1 by 1 and assign the weight
    #Instead of having to slice everything. This way, changing layers will also not impact this process. (GPT helped)
    def initialize_population(self):
        return [self._generate_random_weights(self.nn_class()) for _ in range(self.population_size)]

    #Uniformly randomly assign each weight
    def _generate_random_weights(self, nn_instance):
        flat_weights = []
        for param in nn_instance.parameters():
            flat_weights.extend(np.random.uniform(-1, 1, param.numel()))
        return flat_weights

    #Evaluating the population.
    #Basically run the simulation and get the returned value (= Fitness function)
    def evaluate_population(self, population):
        fitness_scores = []
        for idx, individual in enumerate(population):
            nn_instance = self.nn_class()
            nn_instance.set_weights(individual)
            fitness = nn_instance.simulate(individual)
            fitness_scores.append((fitness, individual))
            print(f'Individual {idx + 1} Fitness: {fitness}')
        return fitness_scores

    #the 2 best are selected each time regardless
    def select_elite(self, fitness_scores):
        fitness_scores.sort(key=lambda x: x[0], reverse=True)
        return fitness_scores[:self.elite_size]

    #The rest is selected through roulette selection where the chance to be picked relates to the relative fitness
    def roulette_wheel_selection(self, fitness_scores):
        max_fitness = sum(fitness for fitness, _ in fitness_scores)
        pick = np.random.uniform(0, max_fitness)
        current = 0
        for fitness, individual in fitness_scores:
            current += fitness
            if current > pick:
                return individual

    #Since the chromosome is large, use blend crossover
    def blend_crossover(self, parent1, parent2, alpha=0.5):
        child1, child2 = [], []
        for p1, p2 in zip(parent1, parent2):
            d = abs(p1 - p2)
            lower = min(p1, p2) - alpha * d
            upper = max(p1, p2) + alpha * d
            child1.append(np.random.uniform(lower, upper))
            child2.append(np.random.uniform(lower, upper))
        return child1, child2

    #Mutations rate also scales with generations
    def adaptive_mutation(self, individual, generation, max_generations):
        for i in range(len(individual)):
            if np.random.rand() < self.mutation_rate:
                mutation_scale = (1 - (generation / max_generations))
                individual[i] += np.random.normal(scale=mutation_scale)
        return individual

    #Used to save the weights after running
    def save_weights(self, weights, filename):
        with open(filename, 'w') as f:
            f.write(f"[{','.join(map(str, weights))}]\n")

    #Combines everything
    def run(self):
        population = self.initialize_population()

        for generation in range(self.generations):
            print(f'Generation {generation + 1}')
            fitness_scores = self.evaluate_population(population)
            elite = self.select_elite(fitness_scores)

            new_population = [ind for _, ind in elite]

            while len(new_population) < self.population_size:
                parent1 = self.roulette_wheel_selection(fitness_scores)
                parent2 = self.roulette_wheel_selection(fitness_scores)
                child1, child2 = self.blend_crossover(parent1, parent2)

                new_population.append(self.adaptive_mutation(child1, generation, self.generations))
                if len(new_population) < self.population_size:
                    new_population.append(self.adaptive_mutation(child2, generation, self.generations))

            population = new_population
            best_fitness = elite[0][0]
            print(f'End of Generation {generation + 1}, Best Fitness: {best_fitness}')

        self.save_weights(elite[0][1], "best_individual_weights.txt")
        return elite[0]


#params
population_size = 50
mutation_rate = 0.01
crossover_rate = 0.7
generations = 30

ga = GA(population_size, mutation_rate, crossover_rate, generations, RNN)
best_individual = ga.run()


best_nn = RNN()
best_nn.set_weights(best_individual[1])
test_result = best_nn.simulate(best_individual[1])
print('Test Result:', test_result)
