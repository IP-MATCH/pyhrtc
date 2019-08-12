"""Contains some calls to algorithms from 3rd parties.
"""

from networkx import Graph as NxGraph, DiGraph, connected_component_subgraphs
from networkx.algorithms.bipartite import maximum_matching
from networkx.algorithms.components import is_connected
from networkx.algorithms.matching import max_weight_matching as nx_max_weight

from pyhrtc.weightedinstance import WeightedInstance


def max_card_matching(instance):
    """Given an instance, calculate the cardinality of the biggest matching.
    Note that this matching need not be, and probably won't be, stable.

    :param instance: The instance in question
    :type instance: Instance
    :rtype: int
    :return: The size of the largest matching.
    """
    graph = NxGraph()
    if instance.number_of_couples_left() != 0:
        raise Exception("max card matching does not currently support couples")
    for left in instance.single_agents_left:
        graph.add_node(f"l%d" % left.ident, bipartite=0)
    for right in instance.single_agents_right:
        for cap in range(right.capacity):
            graph.add_node(f"r%d_%d" % (right.ident, cap), bipartite=1)
    for left in instance.single_agents_left:
        for pref_group in left.preferences:
            for right_id in pref_group:
                for cap in range(instance.single_agent_right(right_id).capacity):
                    graph.add_edge(f"l%d" % left.ident,
                                   f"r%d_%d" % (right_id, cap))
    size = 0
    for component in connected_component_subgraphs(graph):
        size += len(maximum_matching(component))
    return int(size/2)


def max_weight_matching(instance):
    """Given a weighted instance, calculate the weight of of the maximum weight
    matching.  Note that this matching need not be, and probably won't be,
    stable.

    :param instance: The instance in question
    :type instance: WeightedInstance
    :rtype: int
    :return: The size of the largest matching.
    """
    if not isinstance(instance, WeightedInstance):
        raise Exception("Max weight matching needs a WeightedInstance")
    graph = NxGraph()
    if instance.number_of_couples_left() != 0:
        raise Exception("Max weight matching does not "
                        "currently support couples")
    for left in instance.single_agents_left:
        graph.add_node(f"l%d" % left.ident, bipartite=0)
    for right in instance.single_agents_right:
        for cap in range(right.capacity):
            graph.add_node(f"r%d_%d" % (right.ident, cap), bipartite=1)
    for left in instance.single_agents_left:
        for pref_group in left.preferences:
            for right_id in pref_group:
                for cap in range(instance.single_agent_right(right_id).capacity):
                    graph.add_edge(f"l%d" % left.ident,
                                   f"r%d_%d" % (right_id, cap),
                                   weight=left.weight_of(right_id))
    weight = 0
    for component in connected_component_subgraphs(graph):
        for start, end in nx_max_weight(component):
            weight += graph[start][end]['weight']
    return weight

def largest_weight_antichain(agents):
    """Given a set of agents, determine how complex their preferences are,
    where complexity is defined as distance from a commonly shared strict
    ordering of options.
    """
    # Step 1, determine possible relationships

    # This class stores possible relationships. In particular, it says "is it
    # possible for a to always be more preferred than b"
    class Relation:
        def __init__(self):
            self.under = True
            self.over = True
    # Sets of possible relationships
    relations = {}
    for agent in agents:
        found = set()
        for group in agent.preferences:
            for now in group:
                for earlier in found:
                    pair = [earlier, now]
                    if pair not in relations:
                        relations[pair] = Relation()
                    relations[pair].under = False
                    pair = [now, earlier]
                    if pair not in relations:
                        relations[pair] = Relation()
                    relations[pair].over = False
            for now in group:
                found.add(now)
    # Step 2, build the graph
    graph = DiGraph()
    for pair, relation in relations.items():
        if not relation.over:
            continue
        # a can be over b!
        a, b = pair
        if a not in graph.nodes():
            graph.add_node(a)
        if b not in graph.nodes():
            graph.add_node(b)
        graph.add_edge(a, b)  # We're pointing "down" towards less preferred
    # Steps 3 and 4
    longest = max(len(antichain) for antichain in graph.condensation())
    return longest

