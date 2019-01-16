"""Basic elements of HRTC problems."""


import random


def grouped(things):
    """Given some iterable object, returns an iterator that goes through the
    things in the object two at a time.
    """
    return zip(*[iter(things)]*2)


class Agent():
    """An agent."""

    def __init__(self, ident, capacity=1):
        self._ident = ident
        self._capacity = capacity
        # This will be a list of lists, with each inner list corresponding to a
        # tie group
        self._preferences = []
        self._num_preferences = None

    @property
    def ident(self):
        """The ID of this agent."""
        return self._ident

    @ident.setter
    def ident(self, new):
        """We cannot change the ID of an agent"""
        raise NotImplementedError

    @property
    def capacity(self):
        """How many other agents can this agent can support."""
        return self._capacity

    @capacity.setter
    def capacity(self, new):
        """Not supported."""
        raise NotImplementedError

    @property
    def num_preferences(self):
        """The number of preferences of this agent, aka the length of its
        preference list.
        """
        if self._num_preferences is None:
            self._num_preferences = sum([len(x) for x in self.preferences])
        return self._num_preferences

    @property
    def preferences(self):
        """Return the preferences, as a list of tie groups. Entries which are
        not in a tie at all still appear by themselvs in a list (i.e. 1 (2 3)
        is [[1], [2, 3]]).
        """
        return self._preferences

    @preferences.setter
    def preferences(self, new):
        """Set the preferences of this agent. This must be a list of lists,
        such that each tie group is a list. For instance, 1 (2 3) should be
        passed in as [[1], [2, 3]].
        """
        self._preferences = new
        self._num_preferences = None

    def rank_of(self, other):
        """Find the rank of other according to this agent.
        """
        for index, group in enumerate(self._preferences):
            if other.id in group:
                return index
        return -1

    def position_of(self, other):
        """Find the position of other in this preference list. Note that this
        is not the same as rank, this function assumes an ordering on the
        elements within a tie, and gives an absolute count on the number of
        agents before it.
        """
        count = 0
        for group in self._preferences:
            for item in group:
                if item == other.id:
                    return count
                count += 1
        return -1

    def make_random_preferences(self, options, tie_density=0, length=None):
        """Create a random preference list from the list options, with the
        given tie density. If length is given, then stop assigning preferences
        once "length" items have been added.
        """
        if length:
            chosen = random.sample(options, length)
        else:
            chosen = list(options)  # Copy so we don't shuffle the original
        random.shuffle(chosen)
        # Reset preferences
        self._preferences = []
        current_tie = []
        for item in chosen:
            # If there is a tie, and we want to end it, do so;
            if current_tie and random.random() >= tie_density:
                # Start a new tie group
                self._preferences.append(current_tie)
                current_tie = []
            current_tie.append(item)
        # Don't forget to add the last tie
        self._preferences.append(current_tie)

    def make_master_list_preferences(self, options, master_list, length=None):
        """Create a preference list from the list options, with the given tie
        density and master list. If length is given, then stop assigning
        preferences once "length" items have been added.
        """
        chosen = []
        for item in master_list:
            if item in options:
                chosen.append(item)
                if length and len(chosen) == length:
                    break
        # Reset preferences
        self._preferences = []
        for item in chosen:
            self._preferences.append([item])

    def acceptable_agents(self):
        """Get the list of acceptable agents for this Agent."""
        agents = []
        for tie in self._preferences:
            agents.extend(tie)
        return agents

    def is_acceptable(self, ident):
        """Is the given agent (as identified by their identifier) acceptable
        for this Agent?
        """
        for tie in self._preferences:
            if ident in tie:
                return True
        return False

    def preference_string(self):
        """Returns the string of preferences for this agent."""
        def format_tie(tie_as_list):
            """Given a set of tied elements, returns a string representing
            them, by surrounding with brackets if there is more than one item.
            """
            if not tie_as_list:
                return ""
            if len(tie_as_list) == 1:
                return "%s" % tie_as_list[0]
            return "(%s)" % (" ".join(map(str, tie_as_list)))
        return " ".join([format_tie(tie) for tie in self.preferences])

    def read_preferences(self, tokens):
        """Read in and assign preferences based on the given string.
        """
        # First reset preferences
        self._preferences = []
        in_tie = False
        current = []
        for token in tokens:
            if not in_tie:
                # Tie starting
                if token[0] == "(" and token[-1] != ")":
                    in_tie = True
                    current.append(int(token[1:]))
                else:
                    # Not at all a tie
                    if token[0] == "(" and token[-1] == ")":
                        token = token[1:-1]
                    self._preferences.append([int(token)])
            else:
                # Inside a tie
                if token[-1] == ")":
                    # Tie ends here
                    current.append(int(token[:-1]))
                    self._preferences.append(current)
                    in_tie = False
                    current = []
                else:
                    # Tie keeps going
                    current.append(int(token))


class Couple(Agent):
    """Two agents together."""

    def __init__(self, first, second):
        super().__init__("(%s,%s)" % (first, second))
        self._first = first
        self._second = second

    def split_ident(self):
        """Returns a string representation of the two individual agents,
        rather than the combined couple.
        """
        return "%s %s" % (self._first, self._second)

    def read_individual_preferences(self, tokens_a, tokens_b):
        """Read in and assign preferences, when preferences are given in two
        distinct lists of strings.
        """
        self._preferences = []
        for one, two in zip(tokens_a, tokens_b):
            self._preferences.append([int(one), int(two)])

    def read_preferences(self, tokens):
        """Read in and assign preferences based on the given string.
        """
        # First reset preferences
        self._preferences = []
        in_tie = False
        current = []
        for token1, token2 in grouped(tokens):
            if not in_tie:
                # Tie starting
                if token1[0] == "(":
                    in_tie = True
                    pref = (int(token1[1:]), int(token2))
                    current.append(pref)
                else:
                    # Not at all a tie
                    self._preferences.append([(int(token1), int(token2))])
            else:
                # Inside a tie
                if token2[-1] == ")":
                    # Tie ends here
                    current.append((int(token1), int(token2[:-1])))
                    self._preferences.append(current)
                    current = []
                else:
                    # Tie keeps going
                    current.append((int(token1), int(token2)))

    def preference_string(self):
        """Returns the string of preferences for this agent."""
        def format_tie(tie_as_list):
            """Given a set of tied elements, returns a string representing
            them, by surrounding with brackets if there is more than one item.
            """
            if not tie_as_list:
                return ""
            if len(tie_as_list) == 1:
                return "%s %s" % (tie_as_list[0][0], tie_as_list[0][1])
            return "(%s)" % (" ".join(["%s %s" % (c[0], c[1])
                                       for c in tie_as_list]))
        return " ".join([format_tie(tie) for tie in self.preferences])

    def __str__(self):
        """A human readable string representation of this Agent.
        """
        return (f"Agent %d with preferences: %s" % (self._ident,
                                                    self.preference_string()))

    @staticmethod
    def from_two_agents(agent1: Agent, agent2: Agent):
        """Given two agents, create a Couple from them.
        """
        couple = Couple(agent1.ident, agent2.ident)
        new_preferences = []
        for second_ind, second_pref in enumerate(agent2.preferences):
            for first_ind, first_pref in enumerate(agent1.preferences):
                if second_ind < first_ind:
                    continue
                if len(first_pref) != 1 or len(second_pref) != 1:
                    raise NotImplementedError("pyhrtc can't interleave "
                                              "from agents with ties")
                if first_ind == second_ind:
                    new_preferences.append([(first_pref[0], second_pref[0])])
                else:
                    first_alt = agent1.preferences[second_ind]
                    second_alt = agent2.preferences[first_ind]
                    new_preferences.append([(first_pref[0], second_pref[0]),
                                            (first_alt[0], second_alt[0])])
        couple.preferences = new_preferences
        return couple


class Instance():
    """An instance of HRTC.
    """

    """A dict to hold all functions that can write Instances to a file.
    """
    instance_writers = {}

    @staticmethod
    def add_writer(name, function):
        """Adds a writer function.
        :param name: The name (identifier) of the file format this function
        writes
        :type name: string
        :param function: A function which takes two parameters, an Instance and
        a string, and writes the instance to file as named in the string
        :type function: a function name
        """
        Instance.instance_writers[name] = function

    def __init__(self, single_agents_left=None, couples_left=None,
                 single_agents_right=None):
        """Create an Instance. Note that if any of the parameters are passed
        in, they are used as is (i.e. not copied) so don't modify the dicts
        after creating an instance. We use "left" and "right" to refer to the
        two sides of this instance.

        :param dict single_agents_left: A dictionary of single agents on the
        left side of this instance
        :param dict couples_left: A dictionary of couples on the left side of
        this instance
        :param dict single_agents_right: A dictionary of single agents on the
        right side of this instance
        """

        # Each of these is a map from ID to the actual entity, so make sure
        # you set IDs appropriately
        if single_agents_left:
            self._single_agents_left = single_agents_left
        else:
            self._single_agents_left = {}
        if couples_left:
            self._couples_left = couples_left
        else:
            self._couples_left = {}
        if single_agents_right:
            self._single_agents_right = single_agents_right
        else:
            self._single_agents_right = {}

    def number_of_single_agents_left(self) -> int:
        """The number of single residents on the left."""
        return len(self._single_agents_left)

    def number_of_couples_left(self) -> int:
        """The number of couples on the left."""
        return len(self._couples_left)

    def number_of_single_agents_right(self) -> int:
        """The number of single agents on the right."""
        return len(self._single_agents_right)

    @property
    def single_agents_left(self):
        """Returns a list of all single agents on the left."""
        return list(self._single_agents_left.values())

    @single_agents_left.setter
    def single_agents_left(self, new):
        """Not allowed."""
        raise NotImplementedError

    @property
    def couples_left(self):
        """Returns a list of all the couples on the left."""
        return list(self._couples_left.values())

    @couples_left.setter
    def couples_left(self, new):
        """Not allowed."""
        raise NotImplementedError

    @property
    def single_agents_right(self):
        """Returns a list of all the single agents on the right."""
        return list(self._single_agents_right.values())

    @single_agents_right.setter
    def single_agents_right(self, new):
        """Not allowed."""
        raise NotImplementedError

    def single_agent_left(self, ident):
        """Returns the agent on the left identified by ident.
        :param ident: The ID of the desired agent.
        :type ident: integer
        :returns: the agent
        :rtype: Agent
        """
        return self._single_agents_left[ident]

    def single_agent_right(self, ident):
        """Returns the agent on the right identified by ident.
        :param ident: The ID of the desired agent.
        :type ident: integer
        :returns: the agent
        :rtype: Agent
        """
        return self._single_agents_right[ident]

    def add_agent_left(self, agent):
        """Add a single agent to the left side of this instance.
        """
        self._single_agents_left[agent.ident] = agent

    def add_couple_left(self, couple):
        """Adds a couple to the left side of this instance.
        """
        self._couples_left[couple.ident] = couple

    def add_agent_right(self, agent):
        """Adds an agent to the right side of this instance.
        """
        self._single_agents_right[agent.ident] = agent

    def make_couple_from_agent_pair_on_left(self, number=1):
        """Take "number x 2" agents from the left, and turn them into couples
        by interleaving. Note that there is no reliable way to select which
        agents.
        """
        while number:
            if len(self._single_agents_left) < 2:
                raise LookupError("Don't have enough agents left")
            id1, id2 = [self._single_agents_left.keys()][-2:]  # pylint: disable=unbalanced-tuple-unpacking, line-too-long
            first = self._single_agents_left[id1]
            second = self._single_agents_left[id2]
            couple = Couple.from_two_agents(first, second)
            self._couples_left[couple.ident] = couple
            del self._single_agents_left[id1]
            del self._single_agents_left[id2]
            number -= 1

    def is_SMTI(self):
        """Returns true if this is an instance of SMTI (aka there are no
        couples, and each agent on the right has capacity 1.
        """
        if self.number_of_couples_left() != 0:
            return False
        for agent in self.single_agents_right:
            if agent.capacity != 1:
                return False
        return True

    def write_to_file(self, filename, variant="Glasgow_HRTC_nocolon"):
        """Writes the instance to a file."""
        if variant in Instance.instance_writers:
            Instance.instance_writers[variant](self, filename)
        else:
            raise Exception("pyhrtc either does not support or "
                            "cannot read this file format.")

    def __str__(self):
        """A human readable string representation of this instance.
        """
        return (f"Instance with %d single agents on the left, %d couples on "
                "the left and %d single agents on the right" %
                (self.number_of_single_agents_left(),
                 self.number_of_couples_left(),
                 self.number_of_single_agents_right()))
