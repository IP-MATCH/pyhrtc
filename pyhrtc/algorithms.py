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
    if instance.get_number_of_couples() != 0:
        raise Exception("max card matching does not currently support couples")
    for doctor in instance.single_residents:
        graph.add_node(f"d%d" % doctor.ident, bipartite=0)
    for hospital in instance.hospitals:
        for cap in range(hospital.capacity):
            graph.add_node(f"h%d_%d" % (hospital.ident, cap), bipartite=1)
    for doctor in instance.single_residents:
        for pref_group in doctor.preferences:
            for hosp_id in pref_group:
                for cap in range(instance.hospital(hosp_id).capacity):
                    graph.add_edge(f"d%d" % doctor.ident,
                                   f"h%d_%d" % (hosp_id, cap))
    if is_connected(graph):
        size = len(maximum_matching(graph))
    else:
        size = 0
        for component in connected_component_subgraphs(graph):
            size += len(maximum_matching(component))
    return int(size/2)
