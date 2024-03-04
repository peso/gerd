"""
A class to generate blueprints from a certain input, to a certain output, on a certain
amount of space in factorio.
"""
import random
from typing import List

from factoriocalc import Machine, Item

import layout

WIDTH = 96 # blueprint width
HEIGHT = 96 # blueprint height

class LocatedMachine:
    'A data class to store a machine and its position'
    def __init__(self, machine: Machine, position=None):
        self.connections = []
        self.machine = machine
        if position is None:
            my_size = layout.entity_size(machine.name)
            corner_range = [WIDTH - my_size[0], HEIGHT - my_size[1]]
            self.position = [random.random() * corner_range[i] for i in range(2)]
        else:
            self.position = position

    def to_int(self):
        '''Converts the stored position to integers.
        Truncates towards zero to avoid placement outside site.'''
        self.position[0] = int(self.position[0])
        self.position[1] = int(self.position[1])

    def __str__(self) -> str:
        'Converts the LocatedMachine to a nicely formatted string'
        return  str(self.machine) + " at " + str(self.position)

    def connect(self, otherMachine: 'LocatedMachine'):
        assert isinstance(otherMachine, LocatedMachine)
        self.connections.append(otherMachine)

    def getConnections(self):
        return self.connections

def randomly_placed_machines(factory):
    '''
    Gives machines needed by the factory a random location.

    :returns: a list of LocatedMachines.
    '''
    boxed_machines = factory.inner.machine.machines

    located_machines = []
    for machine in boxed_machines:
        for _ in range(machine.num):
            located_machine = LocatedMachine(machine.machine)
            located_machines.append(located_machine)

    # FIXME remove this debug code
    for located_machine in located_machines:
        print(located_machine)

    return located_machines


def spring(machines: List[LocatedMachine]):
    '''
    Does the spring algorithm on the given machines, and returns them after
    Will treat input as a list of floats
    '''
    for machine in machines:
        for input in machine.machine.inputs:
            source_machine = find_machine_of_type(machines, input)
            if source_machine is None:
                pass # TODO External input should be fixed at the edge of the construction site
            else:
                machine.connect(source_machine)

    # FIXME write code to do the springing

    return machines

def find_machine_of_type(machines: List[LocatedMachine], machine_type: dict[any, None]):
    print("looking for machine that produces " + str(machine_type))

    def machine_produces(machine: Machine, output: Item):
        assert isinstance(machine, Machine), f' {type(machine)} is not a Machine'
        assert isinstance(output, Item), f' {type(output)} is not an Item'
        if machine.recipe is None:
            return False # No recipe means no output
        for recipe_output in machine.recipe.outputs:
            if recipe_output.item == output:
                print(f' machine {machine} produces {recipe_output}')
                return True
        return False

    machine_list = [m for m in machines if machine_produces(m.machine, machine_type)]
    if len(machine_list) < 1:
        print(f' no machine produces {machine_type}')
        return None
    if len(machine_list) > 1:
        # TODO - This should not return error, but just choose the one that already is being used the most.
        raise ValueError(f'More than one machine in list produces {machine_type}')
    return machine_list[0]


def machines_to_int(machines: List[LocatedMachine]):
    'Assumes that the machiens are not overlapping in any way'
    for machine in machines:
        machine.to_int()

def place_on_site(site, machines: List[LocatedMachine]):
    '''
    Place machines on the construction site

    :param site:  A ConstructionSite that is sufficiently large
    :param machines:  A list of LocatedMachine
    '''
    for lm in machines:
        machine = lm.machine
        site.add_entity(machine.name, lm.position, 0, machine.recipe)

    for target in machines:
        for source in target.connections:
            dist = [target.position[i] - source.position[i] for i in range(2)]
            abs_dist = [abs(dist[i]) for i in range(2)]
            max_dist = max(abs_dist)
            # FIXME: Assume both machines are size 3x3
            if max_dist < 3:
                raise ValueError(f'Machines overlap')
            if max_dist == 3:
                raise NotImplementedError('Machines touch')
            if min(abs_dist) in [1,2]:
                raise NotImplementedError('Path algorithm cannot handle small offsets')
            assert max_dist > 3
            # Layout belt
            belt_count = sum(abs_dist) - 3 - 2*1
            if belt_count < 1:
                raise NotImplementedError('Machines can connect with single inserter')
            pos = [source.position[i] + 1 for i in range(2)]
            tgtpos = [target.position[i] + 1 for i in range(2)]
            step = 0
            while pos != tgtpos:
                step += 1
                if pos[0] != tgtpos[0]:
                    pos[0] += 1 if tgtpos[0] > pos[0] else -1
                else:
                    pos[1] += 1 if tgtpos[1] > pos[1] else -1
                if step < 2 or step > 3 + belt_count:
                    continue
                step_dir = 0 # TODO compute step_dir
                if step == 2:
                    site.add_entity('inserter', pos, step_dir, None)
                elif step == 3 + belt_count:
                    site.add_entity('inserter', pos, step_dir, None)
                else:
                    site.add_entity('transport-belt', pos, step_dir, None)

def connect_points(site):
    'Generates a list of coordinates, to walk from one coordinate to the other'
    pass # do A star

if __name__ == '__main__':
    '''Test code executed if run from command line'''
    import test.solver
    import unittest
    unittest.main(defaultTest='test.solver', verbosity=2)
