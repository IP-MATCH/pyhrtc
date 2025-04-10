"""Contains some calls to algorithms from 3rd parties.
"""

from networkx import Graph as NxGraph, connected_components  # type: ignore
from networkx.algorithms.bipartite import maximum_matching  # type: ignore
from networkx.algorithms.matching import max_weight_matching as nx_max_weight  # type: ignore

from pyhrtc.weightedinstance import WeightedInstance


def connected_component_subgraphs(graph):
    for nodes in connected_components(graph):
        yield graph.subgraph(nodes)


def max_card_matching(instance):
    """Given an instance, calculate the cardinality of the biggest matching.
    Note that this matching need not be, and probably won't be, stable.

    :param instance: The instance in question
    :type instance: Instance
    :rtype: int
    :return: The size of the largest cardinality matching.
    """
    graph = NxGraph()
    if instance.number_of_couples_left() != 0:
        raise Exception("max card matching does not currently support couples")
    for left in instance.single_agents_left:
        graph.add_node(f"l{left.ident}", bipartite=0)
    for right in instance.single_agents_right:
        for cap in range(right.capacity):
            graph.add_node(f"r{right.ident}_{cap}", bipartite=1)
    for left in instance.single_agents_left:
        for pref_group in left.preferences:
            for right_id in pref_group:
                for cap in range(instance.single_agent_right(right_id).capacity):
                    graph.add_edge(f"l{left.ident}", f"r{right_id}_{cap}")
    size = 0
    for verts in connected_components(graph):
        component = graph.subgraph(verts).copy()
        size += len(maximum_matching(component))
    return int(size / 2)


def max_weight_matching(instance):
    """Given a weighted instance, calculate the weight of of the maximum weight
    matching.  Note that this matching need not be, and probably won't be,
    stable.

    :param instance: The instance in question
    :type instance: WeightedInstance
    :rtype: float
    :return: The weight of the largest weigh tmatching.
    """
    if not isinstance(instance, WeightedInstance):
        raise Exception("Max weight matching needs a WeightedInstance")
    graph = NxGraph()
    if instance.number_of_couples_left() != 0:
        raise Exception("Max weight matching does not " "currently support couples")
    for left in instance.single_agents_left:
        graph.add_node(f"l{left.ident}", bipartite=0)
    for right in instance.single_agents_right:
        for cap in range(right.capacity):
            graph.add_node(f"r{right.ident}_{cap}", bipartite=1)
    for left in instance.single_agents_left:
        for pref_group in left.preferences:
            for right_id in pref_group:
                for cap in range(instance.single_agent_right(right_id).capacity):
                    graph.add_edge(
                        f"l{left.ident}",
                        f"r{right_id}_{cap}",
                        weight=left.weight_of(right_id),
                    )
    weight = 0
    for verts in connected_components(graph):
        component = graph.subgraph(verts).copy()
        for start, end in nx_max_weight(component):
            weight += graph[start][end]["weight"]
    return weight
