"""Basic elements of HRTC problems."""
from __future__ import annotations


from collections.abc import Sequence
from enum import Enum
import logging
from typing import Callable
import random


logger = logging.getLogger(__name__)

class STABILITY(Enum):
    MM = "MM"
    BIS = "BIS"
    KPR = "KPR"


def grouped(things):
    """Given some iterable object, returns an iterator that goes through the
    things in the object two at a time.
    """
    return zip(*[iter(things)]*2)



class PreferencePair(tuple):
    """A pair of preferences that would appear in the preference list of a couple.
    """
    def __new__(self, left, right):
        return tuple.__new__(PreferencePair, (left, right))

    @property
    def ident(self):
        return f"{self[0]},{self[1]}"

    def __str__(self):
        return f"Preference pair {self[0]},{self[1]}"

    def __repr__(self):
        return f"Preference pair {self[0]},{self[1]}"


class Agent:
    """An agent."""

    def __init__(self, ident: str, capacity: int=1):
        self._ident = ident
        self._capacity = capacity
        self._couple: Couple | None = None
        # This will be a list of lists, with each inner list corresponding to a
        # tie group
        self._preferences: list[list[str]] = []
        self._num_preferences: int | None = None

    def __repr__(self):
        """A human readable string representation of this Agent.
        """
        return (f"Agent {self._ident} with preferences: "
                f"{self.preference_string()}")

    def __str__(self):
        return f"Agent:{self._ident}"

    @property
    def ident(self) -> str:
        """The ID of this agent."""
        return self._ident

    @ident.setter
    def ident(self, new):
        """We cannot change the ID of an agent"""
        raise NotImplementedError

    @property
    def capacity(self) -> int:
        """How many other agents can this agent can support."""
        return self._capacity

    @capacity.setter
    def capacity(self, new):
        """Not supported."""
        raise NotImplementedError

    @property
    def couple(self) -> Couple | None:
        """Return the couple this agent is in, if they are in one. Otherwise return None"""
        return self._couple

    @couple.setter
    def couple(self, couple: Couple):
        self._couple = couple

    @property
    def num_preferences(self) -> int:
        """The number of preferences of this agent, aka the length of its
        preference list.
        """
        if self._num_preferences is None:
            self._num_preferences = sum([len(x) for x in self.preferences])
        return self._num_preferences

    def is_empty(self) -> bool:
        """Return True if and only if this Agent has no preferences, and
        therefore can be safely deleted.
        """
        return not self.preferences

    @property
    def preferences(self) -> list[list[str]]:
        """Return the preferences, as a list of tie groups. Entries which are
        not in a tie at all still appear by themselvs in a list (i.e. 1 (2 3)
        is [["1"], ["2", "3"]]).
        """
        return self._preferences

    @preferences.setter
    def preferences(self, new):
        """Set the preferences of this agent. This must be a list of lists,
        such that each tie group is a list. For instance, 1 (2 3) should be
        passed in as [["1"], ["2", "3"]].
        """
        self._preferences = new
        self._num_preferences = None

    def rank_of(self, other: str | Agent | PreferencePair) -> int:
        """Find the rank of other according to this agent. Note that ranks
        start at 1, not 0.
        """
        if isinstance(other, Agent):
            ident = other.ident
        elif isinstance(other, PreferencePair):
            ident = other.ident
        else:
            ident = other
        for index, group in enumerate(self.preferences, start=1):
            if ident in group:
                return index
        raise Exception(f"Tried to get rank of {other} according to {self} but failed")

    def prefers(self, one: Agent | PreferencePair | str, two: Agent | PreferencePair | str,
                allow_equal: bool = False) -> bool:
        """Does this agent strictly prefer one to two? Note that the order of arguments
        is very important here.

        :param allow_equal: If True, this function will also return true if
            this agent is indifferent between the two agents.

        """
        if allow_equal:
            return self.rank_of(one) <= self.rank_of(two)
        return self.rank_of(one) < self.rank_of(two)

    def trim_after_worst(self, agents: list[Agent]):
        """Given a set of agents, trim this agents preference list by removing
        anything that occurs after the worst agent in agents.
        :param agents: An Iterable containing agent IDs
        :return: The number of preferences removed
        """
        removed = 0
        while not [agent for agent in agents if agent in self.preferences[-1]]:
            removed += len(self.preferences.pop(-1))
        return removed

    def position_of(self, other: Agent) -> int:
        """Find the position of other in this preference list. Note that this
        is not the same as rank, this function assumes an ordering on the
        elements within a tie, and gives an absolute count on the number of
        agents before it.
        """
        count = 0
        for group in self.preferences:
            for item in group:
                if item == other.ident:
                    return count
                count += 1
        return -1

    def tie_density(self) -> float:
        """Get the tie density according to this agent."""
        if len(self.preferences) == 1 and len(self.preferences[1]) == 1:
            raise NotImplementedError()
        count = 0
        for pref in self.preferences:
            count += len(pref) - 1
        return count / (count + len(self.preferences))

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
        """An iterator for acceptable agents for this Agent."""
        for tie in self.preferences:
            for agent in tie:
                yield agent

    def as_good_as(self, other):
        """An iterator for all agent IDs that this agent thinks are at least as good as other.
        :param other: an Agent ID
        :return: An iterator of Agent IDs
        """
        for tie in self.preferences:
            for agent in tie:
                yield agent
            if other in tie:
                break

    def is_acceptable(self, ident: str) -> bool:
        """Is the given agent (as identified by their identifier) acceptable
        for this Agent?
        """
        for tie in self.preferences:
            if ident in tie:
                return True
        return False

    def preference_string(self) -> str:
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
                    current.append(token[1:])
                else:
                    # Not at all a tie
                    if token[0] == "(" and token[-1] == ")":
                        token = token[1:-1]
                    self._preferences.append([token])
            else:
                # Inside a tie
                if token[-1] == ")":
                    # Tie ends here
                    current.append(token[:-1])
                    self._preferences.append(current)
                    in_tie = False
                    current = []
                else:
                    # Tie keeps going
                    current.append(token)


    def prefers_to_matched(self, instance: Instance, matching: Matching, agent: Agent | PreferencePair | str, ignore: str | None = None) ->  bool:
        """Does this agent prefer the given agent or preference pair to any
        they are currently matched to. If not None, ignore indicates an agent
        who should be ignored when considering preferences.
        """
        matches = matching.matched(self)
        logging.debug(f"Checking if {repr(self)} prefers {agent} to matched {matches} with {ignore=}")
        if len(matches) == 0:
            return True
        for matched in matches:
            if self.prefers(agent, matched) and matched != ignore:
                logging.debug(f"{repr(self)} prefers {agent} to {matched}")
        return any(self.prefers(agent, matched) for matched in matching.matched(self)
                   if matched != ignore)

    def prefers_couple_to_matched(self, instance: Instance, matching: Matching, couple: Couple, both_beat_both: bool, strict: bool, just_one: bool = False) ->  bool:
        """Does this agent prefer the given Couple to agents they are
        currently matched to.

        :param both_beat_both: If True, then there must be two distinct agents
            currently matched such that both members of the preference pair are
            strictly prefered to both of the two agents currently matched.
        :param strict_both: If True, the agent must strictly prefer both
            members of the couple to the agent or agents currently matched
        """
        if both_beat_both:
            for one in matching.matched(self):
                for two in matching.matched(self):
                    if one == two:
                        continue
                    if self.prefers(couple.first, one, allow_equal=not strict) and self.prefers(couple.second, two, allow_equal=not strict):
                        return True
        else:
            # How many agents do we need the couple to beat
            needed = 2
            if just_one:
                needed = 1
            # Need at least two agents such that the agent would prefer either
            # member of the couple to either of the two about to be rejected
            return sum(1
                       for matched in matching.matched(self)
                       if self.prefers(couple.first, matched, allow_equal=not strict) and self.prefers(couple.second, matched, allow_equal=not strict)) >= needed
        return False


class Couple(Agent):
    """Two agents together."""

    def __init__(self, first: Agent, second: Agent):
        super().__init__("(%s,%s)" % (first, second))
        self._first: Agent = first
        self._second: Agent = second

    @property
    def first(self) -> Agent:
        return self._first

    @property
    def second(self) -> Agent:
        return self._second

    def split_ident(self) -> str:
        """Returns a string representation of the two individual agents,
        rather than the combined couple.
        """
        return "%s %s" % (self._first, self._second)

    def read_individual_preferences(self, tokens_a: str, tokens_b: str):
        """Read in and assign preferences, when preferences are given in two
        distinct lists of strings.
        """
        self._preferences = []
        for one, two in zip(tokens_a, tokens_b):
            self._preferences.append([f"{one},{two}"])

    def read_preferences(self, tokens: str) -> None:
        """Read in and assign preferences based on the given string. As this is
        a Couple, each token in the string should represent a pair of
        hospitals, separate by a comma (and with no space). Note that this may
        need the creation of a "null" agent who has unlimited capacity and has
        no strict preferences over agents.

        :param tokens: A representation of this Couple's preferences.
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
                    current.append(token[1:])
                else:
                    # Not at all a tie
                    if token[0] == "(" and token[-1] == ")":
                        token = token[1:-1]
                    self._preferences.append([token])
            else:
                # Inside a tie
                if token[-1] == ")":
                    # Tie ends here
                    current.append(token[:-1])
                    self._preferences.append(current)
                    in_tie = False
                    current = []
                else:
                    # Tie keeps going
                    current.append(token)
        self._preferences.append(current)

    def __str__(self):
        """A human readable string representation of this Agent.
        """
        return f"Couple {self._first.ident}, {self._second.ident} with preferences: {self.preference_string()}"

    def __repr__(self):
        return f"Couple:{self._first.ident},{self._second.ident}"

    @staticmethod
    def from_two_agents(agent1: Agent, agent2: Agent):
        """Given two agents, create a Couple from them.
        """
        couple = Couple(agent1, agent2)
        new_preferences: list[list[str]] = []
        for second_ind, second_pref in enumerate(agent2.preferences):
            for first_ind, first_pref in enumerate(agent1.preferences):
                if second_ind < first_ind:
                    continue
                if len(first_pref) != 1 or len(second_pref) != 1:
                    raise NotImplementedError("pyhrtc can't interleave "
                                              "from agents with ties")
                if first_ind == second_ind:
                    new_preferences.append([f"{first_pref[0]}|{second_pref[0]}"])
                else:
                    first_alt = agent1.preferences[second_ind]
                    second_alt = agent2.preferences[first_ind]
                    new_preferences.append([f"{first_pref[0]}|{second_pref[0]}",
                                            f"{first_alt[0]}|{second_alt[0]}"])
        couple.preferences = new_preferences
        return couple


class Instance:
    """An instance of HRTC.
    """

    """A dict to hold all functions that can write Instances to a file.
    """
    instance_writers: dict[str, Callable[["Instance", str], None]] = {}

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

    def left_agents(self) -> list[Agent | Couple]:
        return list(self._single_agents_left.values()) + list(self._couples_left.values())

    @property
    def single_agents_right(self):
        """Returns a list of all the single agents on the right."""
        return list(self._single_agents_right.values())

    @single_agents_right.setter
    def single_agents_right(self, new):
        """Not allowed."""
        raise NotImplementedError

    def agent_left(self, ident: str) -> Agent | Couple:
        """Return either the single agent or the couple on the left by their ID.

        :param ident: The identifier for the requested agent.
        :return: The agent in question.
        """
        try:
            return self.single_agent_left(ident)
        except KeyError:
            return self._couples_left[ident]

    def single_agent_left(self, ident: str):
        """Returns the agent on the left identified by ident.
        :param ident: The ID of the desired agent.
        :returns: the agent
        """
        return self._single_agents_left[ident]

    def single_agent_right(self, ident: str) -> Agent:
        """Returns the agent on the right identified by ident.
        :param ident: The ID of the desired agent.
        :returns: the agent
        """
        return self._single_agents_right[ident]

    def add_agent_left(self, agent):
        """Add a single agent to the left side of this instance.
        """
        self._single_agents_left[agent.ident] = agent

    def add_couple_left(self, couple: Couple):
        """Adds a couple to the left side of this instance.
        """
        self._couples_left[couple.ident] = couple

    def add_agent_right(self, agent):
        """Adds an agent to the right side of this instance.
        """
        self._single_agents_right[agent.ident] = agent

    def couple_from_agent(self, agent: Agent | str) -> Couple | None:
        """Return the couple to which an agent belongs, if they are part of a
        couple. If they aren't, return None.
        """
        if isinstance(agent, Agent):
            ident = agent.ident
        else:
            ident = agent
        for couple in self._couples_left.values():
            if ident in [couple.first.ident, couple.second.ident]:
                return couple
        return None

    def make_couple_from_agent_pair_on_left(self, number=1):
        """Take "number x 2" agents from the left, and turn them into couples
        by interleaving. Note that there is no reliable way to select which
        agents.
        """
        while number:
            if len(self._single_agents_left) < 2:
                raise LookupError("Don't have enough agents left")
            id1, id2 = list(self._single_agents_left.keys())[-2:]
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

    def long_string(self):
        """Write a long human-readable description of this instance.
        """
        return ("\n".join([str(agent) for agent in self.single_agents_left]) +
                "\n" +
                "\n".join([str(agent) for agent in self.single_agents_right]) +
                "\n")

    def __str__(self):
        """A human readable string representation of this instance.
        """
        return ("Instance with %d single agents on the left, %d couples on "
                "the left and %d single agents on the right" %
                (self.number_of_single_agents_left(),
                 self.number_of_couples_left(),
                 self.number_of_single_agents_right()))

    def preprocess(self, side='L', order=None):
        """Preprocess this instance, removing any pairs which will definitely
        not be part of a stable matching.
        For each agent l on the Left, we build up a set O containing elements
        from the Right.  Then we set T to be all those agents on the Left which
        any agent from O considers at least as good as l.  If the total
        capacity of O is >= the total capacity of T, then in a stable matching
        l will be matched with an agent that l thinks is no worse than the
        worst agent in O.
        :param side: From which side are we removing preferences, 'L' or 'R'
        :param order: An iterating function to determine how we build up the
        set positions. It should take 5 parameters: agent, instance, positions,
        candidates, and side.  Agent is an Agent object, the one whose list we
        are preprocessing. The default implementation is to simply iterate
        through the preferences of this agent in order. More complex ordering
        functions might look at either positions or candidates to see if
        yielding a particular agent will significantly increase the size of
        candidates, which may be less useful for preprocessing.  instance is
        this instance, which may be useful when designing these more complex
        orderings. Side is as for this function.
        :return: How many preferences have been removed. Note that if the pair
        (a,b) is now no longer considered, this counts as one removal, not two.
        """
        removed = 0
        if order is None:
            def order(agent, instance, positions, candidates, side):
                for group in agent.preferences:
                    for other_agent in group:
                        if other_agent not in positions:
                          yield other_agent
        if side == 'L':
            these = self.single_agents_left
            other = self.single_agents_right
            these_agent = self.single_agent_left
            other_agent = self.single_agent_right
        else:
            these = self.single_agents_right
            other = self.single_agents_left
            these_agent = self.single_agent_right
            other_agent = self.single_agent_left
        for single in these:
            positions = set()
            candidates = set()
            # Go through agents in this preference list according to some
            # ordering.
            for each in order(single, self, positions, candidates, side):
                positions.add(each)
                # Add anything that each thinks is at least as good as single
                for group in other_agent(each).preferences:
                    for agent in group:
                        candidates.add(agent)
                    if single.ident in group:
                        break
                if (sum([other_agent(pos).capacity for pos in positions]) >=
                    sum([these_agent(cand).capacity for cand in candidates])):
                    removed += single.trim_after_worst(positions)
                    self.clean_one(single, other)
        return removed

    def clean_one(self, agent, other_side):
        """Clean this instance, removing incompatible agents. This variant
        knows which agent has had its preferences edited, so it only goes
        through one set of agents, and only looks to remove one particular
        agent from a preference group.
        """
        found = False
        for other in other_side:
            for group in other.preferences:
                if agent.ident in group and not agent.is_acceptable(other.ident):
                    group.remove(agent.ident)
                    found = True
                    break
            if found:
                other.preferences = [group for group in other.preferences if group]

    def clean(self):
        """Clean this instance, removing from preference lists any incompatible
        agents.
        """
        for queue, other_queue in [(self.single_agents_left, self.single_agent_right),
                                   (self.single_agents_right, self.single_agent_left)]:
            for agent in queue:
                new_preferences = []
                for group in agent.preferences:
                    new_group = [other for other in group
                                if other_queue(other).is_acceptable(agent.ident)]
                    if new_group:
                        new_preferences.append(new_group)
                agent.preferences = new_preferences


class Matching:

    def __init__(self, instance: Instance, matching: list[tuple[str, str]]):
        self._matching = matching
        self._instance = instance
        lefts = set(pair[0] for pair in matching)
        rights = set(pair[1] for pair in matching)
        self._matches_from_left = {
            l: [pair[1] for pair in matching if pair[0] == l]
            for l in lefts
        }
        self._matches_from_right = {
            r: [pair[0] for pair in matching if pair[1] == r]
            for r in rights
        }

    def matches_from_left(self, agent: str) -> list[str]:
        """Given a left-agent, return the list of agents the left-agent is
        matched with.

        :param agent: The id of the left-agent in question
        """
        if agent in self._matches_from_left:
            return self._matches_from_left[agent]
        return []

    def matches_from_right(self, agent: str) -> list[str]:
        """Given a right-agent, return the list of agents the right-agent is
        matched with.

        :param agent: The id of the right-agent in question
        """
        if agent in self._matches_from_right:
            return self._matches_from_right[agent]
        return []

    def capacity_available(self, agent: Agent | str) -> int:
        if isinstance(agent, str):
            actual_agent = self._instance.single_agent_right(agent)
        else:
            actual_agent = agent
        return actual_agent.capacity - len(self.matches_from_right(actual_agent.ident))

    def is_stable(self, stability_type):
        for left in self._instance.left_agents():
            for right_ident in left.acceptable_agents():
                if isinstance(left, Couple):
                    right = PreferencePair(*right_ident.split(","))
                    logger.debug(f"Made {right=} from {right_ident=}")
                    if not self._is_stable_couple(left, right, stability_type):
                        logger.debug(f"Not stable with couple: {left} and {right}")
                        return False
                else:
                    right = self._instance.single_agent_right(right_ident)
                    if not self._is_stable_not_couple(left, right):
                        logger.debug(f"Not stable no couple: {left} and {right}")
                        return False
        return True

    def matched(self, agent: str | Agent) -> Sequence[str]:
        """Given the ID of an agent, return the agent that this agent is
        matched too, or None if they are not matched.
        If agent is a couple, return the PreferencePair corresponding to the
        matched agents.
        """
        if isinstance(agent, Couple):
            return [f"{self.matches_from_left(agent.first.ident)[0]},{self.matches_from_left(agent.second.ident)[0]}"]
        if isinstance(agent, Agent):
            agent_ident = agent.ident
        else:
            agent_ident = agent
        if match := self.matches_from_left(agent_ident):
            return match
        return self.matches_from_right(agent_ident)

    def _is_stable_not_couple(self, left, right):
        if self.matched(left) == [right]:
            return True
        if not left.prefers_to_matched(self._instance, self, right):
            return True
        if not right.prefers_to_matched(self._instance, self, left):
            return True
        return False

    def _is_stable_couple(self, left: Couple, right: PreferencePair, stability_type) -> bool:
        # Note that CH1 is already handled by only considering acceptable pairs for left
        # This handles CH2 and CHH2
        logger.debug(f"Checking stability of {left=} and {right=}")
        if (self.matched(left.first) and self.matched(left.second)) and not left.prefers_to_matched(self._instance, self, right):
            logger.debug("Not satisfying CH2/CHH2, not blocking pair")
            return True
        logger.debug("Satisfies CH2/CHH2")
        # At this point, the couple would rather be matched to the pair of hospitals.
        hosps = tuple(self._instance.single_agent_right(p) for p in right)
        if right[0] != right[1]:
            logger.debug("CHH case")
            # We're in the CHH case
            # CHH3
            if not (
                    self.capacity_available(right[0]) >= 1 or
                    right[0] in self.matches_from_left(left.first.ident) or
                    hosps[0].prefers_to_matched(self._instance, self, left.first)
                    ):
                logger.debug("Not satisfying CHH3, not blocking pair")
                return True
            # CHH4
            if not (
                    self.capacity_available(right[1]) >= 1 or
                    right[1] in self.matches_from_left(left.second.ident) or
                    hosps[1].prefers_to_matched(self._instance, self, left.second)
                    ):
                logger.debug("Not satisfying CHH4, not blocking pair")
                return True
        else:
            # CH cases
            logger.debug("CH case")
            # flag to see if CH3 holds
            ch3 = False
            # CH3.1
            if self.capacity_available(hosps[0]) >= 2:
                logger.debug("Satisfies CH3.1")
                ch3 = True
            # CH3.2
            if self.capacity_available(hosps[0]) == 1 and (hosps[0].ident in self.matched(left.first) or hosps[0].ident in self.matched(left.second)):
                logger.debug("Satisfies CH3.2")
                ch3 = True
            # CH3.3
            if stability_type == STABILITY.MM:
                # CH3.3'
                if self.capacity_available(hosps[0]) == 1 and (hosps[0].prefers_to_matched(self._instance, self, left.first) or hosps[0].prefers_to_matched(self._instance, self, left.second)):
                    logger.debug("Satisfies CH3.3'")
                    ch3 = True
            else:
                if self.capacity_available(hosps[0]) == 1 and (hosps[0].prefers_to_matched(self._instance, self, left.first) and hosps[0].prefers_to_matched(self._instance, self, left.second)):
                    logger.debug("Satisfies CH3.3")
                    ch3 = True
            # CH3.4
            if stability_type == STABILITY.MM:
                # CH3.4.1'
                if hosps[0].prefers_to_matched(self._instance, self, left.first, ignore=left.second.ident) and self.matched(left.second) == [right[0]]:
                    logger.debug("Satisfies CH3.4.1'")
                    ch3 = True
                # CH3.4.2'
                if hosps[0].prefers_to_matched(self._instance, self, left.second, ignore=left.first.ident) and self.matched(left.first) == [right[0]]:
                    logger.debug("Satisfies CH3.4.2'")
                    ch3 = True
                pass
            else:
                if ((self.matched(left.first) == [hosps[0].ident] or (self.matched(left.second) == [hosps[0].ident])) and (hosps[0].prefers_couple_to_matched(self._instance, self, left, both_beat_both=False, strict=True, just_one=True))):
                    logger.debug("Satisfies CH3.4")
                    ch3 = True
            # CH3.5
            if stability_type == STABILITY.MM:
                if hosps[0].prefers_couple_to_matched(self._instance, self, left, both_beat_both=False, strict=True):
                    logger.debug("Satisfies CH3.5'")
                    ch3 = True
            else:
                if hosps[0].prefers_couple_to_matched(self._instance, self, left, both_beat_both=True, strict=True):
                    logger.debug("Satisfies CH3.5")
                    ch3 = True
            if stability_type == STABILITY.BIS:
                # CH3.6
                for agent_ident in self.matched(hosps[0]):
                    couple = self._instance.couple_from_agent(agent_ident)
                    if couple is None:
                        # This matched doctor is not in a couple, so 3.6 cannot apply
                        continue
                    if not (couple.first in self.matched(hosps[0]) and couple.second in self.matched(hosps[0])):
                        continue
                    if not (hosps[0].prefers(left.first, couple.first) and hosps[0].prefers(left.second, couple.first) or
                        hosps[0].prefers(left.first, couple.second) and hosps[0].prefers(left.second, couple.second)
                        ):
                        logger.debug("Satisfies CH3.6")
                        ch3 = True
                        break
            # If CH3 doesn't hold, this pairing is stable
            if ch3 is False:
                logger.debug("CH3 not satisfied, is not blocking pair")
                return True
        return False


import pyhrtc.fileio
