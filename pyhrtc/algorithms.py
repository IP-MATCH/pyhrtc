"""Contains some calls to algorithms from 3rd parties.
"""


from networkx import Graph as NxGraph, connected_component_subgraphs
from networkx.algorithms.bipartite import maximum_matching
from networkx.algorithms.components import is_connected


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
    if is_connected(graph):
        size = len(maximum_matching(graph))
    else:
        size = 0
        for component in connected_component_subgraphs(graph):
            size += len(maximum_matching(component))
    return int(size/2)
