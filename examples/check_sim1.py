# -*- coding: utf-8 -*-

import textwrap
import matplotlib.pyplot as plt

from biosim.simulation import BioSim

"""
Compatibility check for BioSim simulations.

This script shall function with biosim packages written for
the INF200 project June 2020.
"""

__author__ = "Hans Ekkehard Plesser, NMBU"
__email__ = "hans.ekkehard.plesser@nmbu.no"

if __name__ == '__main__':
    # import time
    # start_time = time.time()

    plt.ion()

    geogr = """\
               WWWWWWWWWWWWWWWWWWWWW
               WWWWWWWWHWWWWLLLLLLLW
               WHHHHHLLLLWWLLLLLLLWW
               WHHHHHHHHHWWLLLLLLWWW
               WHHHHHLLLLLLLLLLLLWWW
               WHHHHHLLLDDLLLHLLLWWW
               WHHLLLLLDDDLLLHHHHWWW
               WWHHHHLLLDDLLLHWWWWWW
               WHHHLLLLLDDLLLLLLLWWW
               WHHHHLLLLDDLLLLWWWWWW
               WWHHHHLLLLLLLLWWWWWWW
               WWWHHHHLLLLLLLWWWWWWW
               WWWWWWWWWWWWWWWWWWWWW"""
    geogr2 = """\
            WWWWWWWWW
            WHDDDDDDW
            WDDDDDDDW
            WDDDDDDDW
            WDDDDDDDW
            WDDDDDDDW
            WDDDDDDDW
            WDDDDDDDW
            WWWWWWWWW"""

    geogr2 = """\
            WWW
            WLW
            WWW
            """
    geogr = textwrap.dedent(geogr2)

    ini_herbs = [{'loc': (2, 2),
                  'pop': [{'species': 'Herbivore', 'age': 5, 'weight': 20} for _ in range(50)]}]
    ini_carns = [{'loc': (2, 2),
                  'pop': [{'species': 'Carnivore', 'age': 5, 'weight': 20} for _ in range(20)]}]

    sim = BioSim(island_map=geogr, ini_pop=ini_herbs, seed=1,
                 # hist_specs = {'fitness': {'max': 1.0, 'delta': 0.05},
                 #               'age': {'max': 60.0, 'delta': 2},
                 #               'weight': {'max': 60, 'delta': 2}},
                 )
    # sim.set_animal_parameters("Herbivore",
    #                           {"zeta": 3.2, "xi": 1.8})
    # sim.set_animal_parameters("Carnivore", {"a_half": 70,
    #                                         "phi_age": 0.5, "omega": 0.3, "F": 65,
    #                                         "DeltaPhiMax": 9.})
    #
    # sim.set_landscape_parameters('L', {'f_max': 700})

    sim.simulate(num_years=100, vis_years=1, img_years=2000)

    sim.add_population(population=ini_carns)
    sim.simulate(num_years=300, vis_years=1, img_years=2000)

    # I think the img_years is how often we save to file

    # print("--- %s seconds ---" % (time.time() - start_time))
    plt.savefig('check_sim.pdf')
    # sim.make_movie()

    input('Press ENTER')