"""Various IP models for HRTC and variants."""

from pulp import LpProblem, LpMaximize, LpVariable, lpSum, LpStatusOptimal

from pyhrtc.weightedinstance import WeightedInstance


class MAX_SMTI_IP(LpProblem):
    """An IP model to find a maximum cardinality stable matching.
    """

    def __init__(self, instance, name=None):
        if instance.number_of_couples_left() != 0:
            raise Exception("This model does not support couples")
        if name is None:
            name = "SMTI"
        super().__init__(name, LpMaximize)
        self._instance = instance
        self._built = False
        self._cardinality_restriction = None

        """Map from each variable name (as a string) to the actual variable object.
        _variables_lr is a map such that _variables_lr[left][right] gives the
        variable where Agent left is assigned to Agent right
        _variables_rl is a map such that _variables_rl[right][left] gives the
        variable where Agent right is assigned to Agent left
        """
        self._variables_lr = None
        self._variables_rl = None

        self._use_dummy = False
        """Maps the y variables, the dummy binary variables from Chapter 5 of paper.
        """
        self._variables_yl = None
        self._variables_yr = None

        """Should we find a maximum weight matching, or maximum size?"""
        self._weighted = False

    @property
    def dummy_variables(self):
        """Are dummy variables used in this model."""
        return self._use_dummy

    @dummy_variables.setter
    def dummy_variables(self, choice):
        """Enable (or disable) the use of dummy variables. Note that this only
        makes sense before building or solving.
        """
        if self._built:
            raise Exception("Cannot modify model after it is built")
        self._use_dummy = choice

    @property
    def weighted(self):
        """Are we finding a maximum weight matching"""
        return self._weighted

    @weighted.setter
    def weighted(self, choice):
        """Enable (or disable) the search for a maximum weight stable matching.
        """
        if self._built:
            raise Exception("Cannot modify model after it is built")
        if choice and not isinstance(self._instance, WeightedInstance):
            raise Exception("Cannot find a maximum weight stable matching if "
                            "the instance is not weighted")
        self._weighted = choice

    @property
    def cardinality_restriction(self):
        """Are we looking for a matching of a specific, known size?
        """
        return self._cardinality_restriction

    @cardinality_restriction.setter
    def cardinality_restriction(self, value):
        """Add a constraint to only search for matchings of the given size.
        """
        self._cardinality_restriction = value

    def _make_variables(self):
        """Makes the variables
        """
        if self._variables_lr is not None:
            return
        self._variables_lr = {}
        self._variables_rl = {}
        for left in self._instance.single_agents_left:
            self._variables_lr[left.ident] = {}
            for right in left.acceptable_agents():
                name = f"x_{left.ident}_{right}"
                variable = LpVariable(name, cat='Binary')
                self._variables_lr[left.ident][right] = variable
                if right not in self._variables_rl:
                    self._variables_rl[right] = {}
                self._variables_rl[right][left.ident] = variable

    def _make_capacity_constraints(self):
        """Makes the constraints for capacities.
        """
        for left in self._instance.single_agents_left:
            self += (lpSum(self._variables_lr[left.ident].values()) <= 1,
                     f"left_{left.ident}_capacity")
        for right in self._instance.single_agents_right:
            # If right.ident isn't in here, then this right agent has no
            # preferences.
            if right.ident not in self._variables_rl:
                continue
            self += (lpSum(self._variables_rl[right.ident].values()) <= 1,
                     f"right_{right.ident}_capacity")

    def _make_dummy_stability_constraints(self):
        """Makes a variable variable for each agent and each rank k in their
        preferences, which will be 1 if and only if the agent is matched with
        another agent of rank k or less.
        """
        if self._variables_yl is not None:
            return
        self._variables_yl = {}
        self._variables_yr = {}
        for left in self._instance.single_agents_left:
            self._variables_yl[left.ident] = {}
            name = f"y_l_{left.ident}_1"
            self._variables_yl[left.ident][1] = LpVariable(name, cat='Binary')
            sum_left = []
            for right_id in left.preferences[0]:
                sum_left.append(self._variables_lr[left.ident][right_id])
            self += (lpSum(sum_left) == self._variables_yl[left.ident][1])
            for k, tie_group in enumerate(left.preferences[1:], start=2):
                name = f"y_l_{left.ident}_{k}"
                self._variables_yl[left.ident][k] = LpVariable(name,
                                                               cat='Binary')
                sum_left = []
                for right_id in tie_group:
                    sum_left.append(self._variables_lr[left.ident][right_id])
                self += (lpSum(sum_left) + self._variables_yl[left.ident][k-1]
                         == self._variables_yl[left.ident][k])
        for right in self._instance.single_agents_right:
            self._variables_yr[right.ident] = {}
            name = f"y_r_{right.ident}_1"
            self._variables_yr[right.ident][1] = LpVariable(name, cat='Binary')
            sum_right = []
            for left_id in right.preferences[0]:
                sum_right.append(self._variables_lr[left_id][right.ident])
            self += (lpSum(sum_right) == self._variables_yr[right.ident][1])
            for k, tie_group in enumerate(right.preferences[1:], start=2):
                name = f"y_r_{right.ident}_{k}"
                self._variables_yr[right.ident][k] = LpVariable(name,
                                                                cat='Binary')
                sum_right = []
                for left_id in tie_group:
                    sum_right.append(self._variables_lr[left_id][right.ident])
                self += (lpSum(sum_right)
                         + self._variables_yr[right.ident][k-1]
                         == self._variables_yr[right.ident][k])
        for left in self._instance.single_agents_left:
            for k, tie_group in enumerate(left.preferences[1:], start=2):
                for right_id in tie_group:
                    right = self._instance.single_agent_right(right_id)
                    rank = right.rank_of(left.ident)
                    self += (1 - self._variables_yl[left.ident][k]
                             <= self._variables_yr[right_id][rank])

    def _make_stability_constraints(self):
        """Makes the stability constraints.
        """
        for left in self._instance.single_agents_left:
            for right_id in left.acceptable_agents():
                right = self._instance.single_agent_right(right_id)
                xiq = lpSum(self._variables_lr[left.ident][other]
                            for other in left.as_good_as(right.ident))
                xpj = lpSum(self._variables_rl[right.ident][other]
                            for other in right.as_good_as(left.ident))
                self += 1 - xiq <= xpj, f"{left.ident}.{right.ident}.stability"

    def _add_dummy_card_constraint(self):
        """Make a cardinality constraint obased on the dummy variables.
        """
        constraint = []
        for left in self._instance.single_agents_left:
            max_group = len(left.preferences)
            constraint.append(self._variables_yl[left.ident][max_group])
        self += (lpSum(constraint) == self._cardinality_restriction,
                 f"card-constraint")

    def _make_dummy_card_objective(self):
        """Make an objective based on the xij variables.
        """
        objective = []
        for left in self._instance.single_agents_left:
            max_group = len(left.preferences)
            objective.append(self._variables_yl[left.ident][max_group])
        self += lpSum(objective)

    def _make_card_objective(self):
        """Make an objective based on the xij variables.
        """
        objective = []
        for left in self._instance.single_agents_left:
            for right in left.acceptable_agents():
                if self.weighted:
                    objective.append(left.weight_of(right) *
                                     self._variables_lr[left.ident][right])
                else:
                    objective.append(self._variables_lr[left.ident][right])
                objective.append(self._variables_lr[left.ident][right])
        self += lpSum(objective)

    def build_model(self):
        """Build the model.
        """
        if self._built:
            return
        self._make_variables()
        self._make_capacity_constraints()
        if self._use_dummy:
            self._make_dummy_stability_constraints()
            if not self.weighted:
                self._make_dummy_card_objective()
            else:
                if self._cardinality_restriction is not None:
                    self._add_dummy_card_constraint()
                self._make_regular_objective()
        else:
            self._make_stability_constraints()
            self._make_card_objective()
        self._built = True

    def solve(self):
        """Solves the problem, and returns the matching. The matching is a map
        such that matching[left] = right if and only if left is matched to
        right.
        """
        self.build_model()
        super().solve()
        if self.status != LpStatusOptimal:
            raise Exception("Not optimal solution.")
        matching = {}
        for left in self._instance.single_agents_left:
            for right in left.acceptable_agents():
                # Because some solvers sometimes return "close to 1" instead of
                # 1, even for binary values, we just get close.
                if self._variables_lr[left.ident][right].varValue >= 0.95:
                    matching[left.ident] = right
        return matching
