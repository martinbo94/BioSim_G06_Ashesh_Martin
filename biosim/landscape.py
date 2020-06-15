# -*- coding: utf-8 -*-

"""
"""
__author__ = "Ashesh Raj Gnawali, Maritn Bø"
__email__ = "asgn@nmbu.no & mabo@nmbu.no"

import numpy as np
import operator
import random


class Landscape:
    """
    Parent class for the landscapes classes water, desert, highland and lowland \n
    """

    parameters = {}

    def __init__(self):
        """
        Constructor for the Landscape class
        """
        # self.sorted_animal_fitness_dict = {}
        self.fauna_dict = {"Herbivore": [], "Carnivore": []}
        self.updated_fauna_dict = {"Herbivore": [], "Carnivore": []}
        self.migrated_fauna_dict = {"Herbivore": [], "Carnivore": []}
        self.food_left = {'Herbivore': 0, 'Carnivore': 0}

    def add_animal(self, animal):
        """
        Adds the animal object to the species dictionary \n
        :param animal: Input animal object \n
        """
        species = animal.__class__.__name__
        self.fauna_dict[species].append(animal)

    def remove_animal(self, animal):
        """
        Removes the animal object from the species dictionary \n
        :param animal: Input animal object \n
        """
        species = animal.__class__.__name__
        self.fauna_dict[species].remove(animal)

    def sort_by_fitness(self):
        """
        Sorts the animal by their fitness. Herbivores are sorted from low to high while the \n
        carnivores are sorted from high to low \n
        """
        self.fauna_dict["Herbivore"].sort(key=operator.attrgetter("animal_fitness"))
        self.fauna_dict["Carnivore"].sort(key=operator.attrgetter("animal_fitness"), reverse=True)

    def update_fodder(self):
        """
        Method to update fodder in cells, which is overridden in Lowland and Highland \n
        """
        pass

    def animal_eats(self):
        """
        The animals in the cells feed, the herbivores feed on fodder and the carnivores \n
        on herbivores \n
        """
        self.update_fodder()
        self.herbivore_eats()
        self.carnivore_eats()

    def available_food(self, animal):
        """
        Returns the remaining food value in a cell for the specific species. \n
        :param animal: animal object \n
        :return: the remaining amount of food \n
        """
        species = animal.__class__.__name__
        return self.remaining_food[species]

    def herbivore_eats(self):
        """
        Herbivores eat randomly, and if there is no fodder available in the cell, the animal \n
        doesn't eat. \n
        If the available fodder is greater than the food the animal requires, \n
        we calculate the food that remains. \n
        If the fodder available is less than the food required by the animal we update remaining \n
        fodder as 0. \n
        """
        np.random.shuffle(self.fauna_dict["Herbivore"])
        for herb in self.fauna_dict["Herbivore"]:
            herb_remaining_fodder = self.remaining_food['Herbivore']
            if herb_remaining_fodder == 0:
                break
            elif herb_remaining_fodder >= herb.parameters['F']:
                herb.animal_weight_with_food(herb.parameters['F'])
                self.remaining_food['Herbivore'] -= herb.parameters['F']
            elif 0 < herb_remaining_fodder < herb.parameters["F"]:
                herb.animal_weight_with_food(herb_remaining_fodder)
                self.remaining_food['Herbivore'] = 0

    def carnivore_eats(self):
        """
        The carnivores eat in the order of fitness. The carnivore with the highest fitness \n
        eats first and preys on the herbivore with the lowest fitness. If the herbivore is \n
        heavy enough or a carnivore to eat, it eats according to it's appetite, \n
        else it eats the food according to the weight of the herbivore \n
        """
        self.sort_by_fitness()
        for carnivore in self.fauna_dict["Carnivore"]:
            appetite_of_carnivore = carnivore.parameters["F"]
            food_eaten = 0
            dead_animals = []
            for herb in self.fauna_dict["Herbivore"]:
                if food_eaten <= appetite_of_carnivore:
                    if np.random.uniform(0, 1) < carnivore.probability_of_killing(herb):
                        eaten = min(carnivore.parameters['F'] - food_eaten, herb.weight)
                        carnivore.animal_weight_with_food(eaten)
                        dead_animals.append(herb)
                        food_eaten += eaten
            self.fauna_dict['Herbivore'] = [herbivore for herbivore in self.fauna_dict['Herbivore']
                                            if
                                            herbivore not in dead_animals]  # self.fauna_dict["Herbivore"].sort(key=operator.attrgetter("animal_fitness"))  # self.sort_by_fitness()

    def new_carnivore_eats(self):
        self.fauna_dict['Carnivore'].sort(key=lambda h: h.fitness, reverse=True)

        self.fauna_dict['Herbivore'].sort(key=lambda h: h.fitness)

        for carnivore in self.fauna_dict['Carnivore']:
            appetite = carnivore.parameters['F']
            amount_eaten = 0

            for herbivore in self.fauna_dict['Herbivore']:

                if amount_eaten >= appetite:
                    break

                elif np.random.uniform(0, 1) < carnivore.probability_of_killing(herbivore):
                    food_wanted = appetite - amount_eaten

                    if herbivore.weight <= food_wanted:
                        amount_eaten += herbivore.weight
                        self.fauna_dict['Herbivore'].remove(herbivore)

                    elif herbivore.weight > food_wanted:
                        amount_eaten += food_wanted
                        self.fauna_dict['Herbivore'].remove(herbivore)

            carnivore.animal_weight_with_food(amount_eaten)

    @property
    def remaining_food(self):
        """
        Gives the remaining food in a cell for different landscape types. Return ValueError \n
        if the property is called on cells that are not migratable, I.E Water \n
        :return: the remaining amount of food \n
        """
        if isinstance(self, Water):
            raise ValueError("There is no fodder available in the water")
        elif isinstance(self, Desert):
            self.food_left = {'Herbivore': 0, 'Carnivore': self.total_herbivore_weight}
        else:
            self.food_left = {"Herbivore": self.food_left["Herbivore"],
                              "Carnivore": self.total_herbivore_weight}
        return self.food_left

    def update_animal_weight_and_age(self):
        """
        Each year the animals ages by 1 and loses weight by a factor of eta \n
        """
        for species in self.fauna_dict:
            for animal in self.fauna_dict[species]:
                animal.animal_weight_with_age()

    def animal_gives_birth(self):
        """
        Compares the birth_probability of an animal with the randomly generated value between \n
        0 and 1 and if it's greater, the animal gives birth. Creates the child of the same \n
        species and decreases the weight of the animal \n
        """
        for species, animals in self.updated_fauna_dict.items():
            for i in range(len(self.updated_fauna_dict[species])):
                animal = animals[i]

                if animal.proba_animal_birth(len(animals)):
                    child_species = animal.__class__
                    child = child_species()
                    animal.weight_update_after_birth(child)

                    if animal.gives_birth:
                        self.fauna_dict[species].append(child)
                        animal.gives_birth = False

    def add_children_to_adult_animals(self):
        """
        After the breeding season, new babies are added to the fauna dictionary \n
        """
        self.updated_fauna_dict = self.fauna_dict

    def migration(self, adj_cells):
        """
        Animal can migrate to any of the adjacent cells with equal probability. The animal \n
        is added to the new cell and remove from the old cell. \n
        :param adj_cells: list of adjacent cells that animal can move to \n
        """
        animals_that_migrated = []
        for species, animals in self.fauna_dict.items():

            for animal in animals:
                if animal.has_animal_already_moved is False:
                    if animal.animal_moves_bool:
                        cell_to_migrate = random.choice(adj_cells)
                        if cell_to_migrate.is_migratable:
                            cell_to_migrate.add_animal(animal)
                            # self.remove_animal(animal)
                            animal.has_animal_already_moved = True
                            animals_that_migrated.append(animal)

            self.fauna_dict[species] = [animal for animal in self.fauna_dict[species] if
                                        animal not in animals_that_migrated]

    def reset_migration_bool_in_cell(self):
        """
        Resets the boolean if an animal has moved or not during a year. Ensures that the animal \n
        migrates maximum once per year. \n
        :return: Boolean \n
        """
        for species, animals in self.fauna_dict.items():
            for animal in animals:
                animal.has_animal_already_moved = False

    def animal_dies(self):
        """"
        If the generated random number is greater than the probability of death, we remove \n
        the animal from the dictionary \n
        """
        for species, animals in self.fauna_dict.items():
            for animal in animals:
                if animal.death_probability:
                    self.remove_animal(animal)

    @property
    def cell_fauna_count(self):
        """
        Calculates the number of herbivores and carnivores separately \n
        :return: A dictionary with herbivore and carnivore as key and the count as value \n
        """
        herb_count = len(self.fauna_dict['Herbivore'])
        carn_count = len(self.fauna_dict['Carnivore'])
        return {"Herbivore": herb_count, "Carnivore": carn_count}

    def total_herbivore_weight(self):
        """
        Calculates the weight of all herbivores in a single cell \n
        :return: The total weight of all herbivores in a single cell \n
        """
        sum_herb_weight = 0
        for herbivore in self.fauna_dict["Herbivore"]:
            sum_herb_weight += herbivore.weight
        return sum_herb_weight

    @classmethod
    def set_parameters(cls, given_params):
        for param in given_params:
            if param in cls.parameters:
                cls.parameters[param] = given_params[param]
            else:
                raise ValueError('Parameter not set in list' + str(param))


class Water(Landscape):
    """
    Child class of Landscape. Animals are unable to migrate to Water cells \n
    """
    is_migratable = False

    def __init__(self):
        super().__init__()


class Desert(Landscape):
    """
    Child class of Landscape. Animals are able to migrate to Desert cells. \n
    There is no fodder in the desert for herbivores to eat, while carnivores can eat the \n
    herbivores \n
    """
    is_migratable = True

    parameters = {'f_max': 0}

    def __init__(self, given_params=None):
        super().__init__()
        if given_params is not None:
            self.set_parameters(given_params)
        self.remaining_food['Herbivore'] = self.parameters['f_max']
        self.remaining_food["Carnivore"] = self.total_herbivore_weight()


class Highland(Landscape):
    """
    Child class of Landscape. Animals are able to migrate to Highland cells. \n
    The amount of fodder is reset every year to the default parameter. Carnivores can \n
    eat the herbivores in the highland \n
    """
    is_migratable = True

    parameters = {'f_max': 300}

    def __init__(self, given_params=None):
        super().__init__()
        if given_params is not None:
            self.set_parameters(given_params)
        self.remaining_food['Herbivore'] = self.parameters['f_max']
        self.remaining_food['Carnivore'] = self.total_herbivore_weight()

    def update_fodder(self):
        """
        Updates the amount of fodder back to f_max annually \n
        """
        self.remaining_food["Herbivore"] = self.parameters["f_max"]


class Lowland(Landscape):
    """
    Child class of Landscape. Animals are able to migrate to Lowland cells. \n
    The amount of fodder is reset every year to the default parameter. Carnivores can \n
    eat the herbivores in the Lowland. \n
    """

    is_migratable = True

    parameters = {'f_max': 800}

    def __init__(self, given_params=None):
        super().__init__()
        if given_params is not None:
            self.set_parameters(given_params)

        self.remaining_food['Herbivore'] = self.parameters['f_max']
        self.remaining_food['Carnivore'] = self.total_herbivore_weight

    def update_fodder(self):
        """
        Updates the amount of fodder back to f_max annually \n
        """
        self.remaining_food["Herbivore"] = self.parameters["f_max"]
