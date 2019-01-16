"""Describes an instance of our problem.
"""

from pyhrtc.basics import Agent, Instance


class WeightedAgent(Agent):
    """An agent in an instance of SMTI-GRP.
    """

    def __init__(self, ident, capacity=1):
        super().__init__(ident, capacity=capacity)
        self._preference_weights = []
        self._sorted_preferences = None

    def add_weight(self, other_ident, weight):
        """Adds the given weight for the given ident.
        :param other_ident: The ID of the other agent
        :type other_ident: integer
        :param weight: The weight of other_ident according to this agent
        :type weight: float
        """
        self._preference_weights.append((other_ident, weight))

    @property
    def preferences(self):
        """Return the preferences, as a list of tie groups. Entries which are
        not in a tie at all still appear by themselvs in a list (i.e. 1 (2 3)
        is [[1], [2, 3]]).
        """
        self._sort_preferences()
        return self._preferences

    def threshold(self, threshold):
        """Remove any scores below the given threshold.
        :param threshold: The value under which no scores will be considered
        :type threshold: integer
        """
        self._sort_preferences()
        while self._sorted_preferences[-1][1] < threshold:
            self._sorted_preferences.pop()

    def better_than(self, ident):
        """Returns the list of WeightedAgent IDs that this agent prefers as good as, or
        more than the one given by ident.
        :param ident: An ID for an WeightedAgent to compare to.
        :type ident: integer
        """
        self._sort_preferences()
        result = []
        agent_score = None
        for pref in self._sorted_preferences:
            if pref[0] == ident:
                agent_score = pref[1]
            if agent_score is not None and pref[1] < agent_score:
                return result
            result.append(pref[0])
        return result

    def _sort_preferences(self):
        """Sorts the preferences by score, highest to lowest.
        """
        # Do nothing if the list is already sorted.
        if self._sorted_preferences is not None:
            return
        self._sorted_preferences = sorted(self._preference_weights,
                                          reverse=True,
                                          key=lambda x: x[1])
        last_weight = None
        self._preferences = []
        group = []
        for ident, weight in self._sorted_preferences:
            if last_weight is not None and weight != last_weight:
                self._preferences.append(group)
                group = []
            group.append(ident)
            last_weight = weight
        if group:
            self._preferences.append(group)

    def __str__(self):
        """A human readable string representation of this Agent.
        """
        return (f"WeightedAgent %d with preferences: %s" %
                (self._ident, self.preference_string()))


class WeightedInstance(Instance):
    """Represents an instance of SMTI-GRP. We assume that both sets of agents
    all have all weights assigned.

    :param lefts: One set of WeightedAgent objects
    :type lefts: Dict[:class:`WeightedAgent`]
    :param rights: The other set of WeightedAgent objects
    :type rightss: Dict[:class:`WeightedAgent`]
    """
    def __init__(self, lefts, rights):
        super().__init__(single_agents_left=lefts, single_agents_right=rights)

    def threshold(self, threshold):
        """Remove any scores below the given threshold from any agents in this
        instance.
        :param threshold: The value under which no scores will be considered
        :type threshold: integer
        """
        for left in self._single_agents_left.values():
            left.threshold(threshold)
        for right in self._single_agents_right.values():
            right.threshold(threshold)

    @property
    def agents_left(self):
        """Returns a list of the WeightedAgents on the left side of this SMTI instance.
        :return: a list of WeightedAgents on the left side
        :rtype: List[:class:`WeightedAgent`]
        """
        return self._single_agents_left

    @property
    def agents_right(self):
        """Returns a list of the WeightedAgents on the right side of this SMTI
        instance.
        :return: a list of WeightedAgents on the right side
        :rtype: List[:class:`WeightedAgent`]
        """
        return self.number_of_single_agents_right

    def __str__(self):
        """A human readable string representation of this instance.
        """
        return (f"WeightedInstance with %d single agents on the left, %d "
                 "couples on the left and %d single agents on the right" %
                (self.number_of_single_agents_left(),
                 self.number_of_couples_left(),
                 self.number_of_single_agents_right()))
