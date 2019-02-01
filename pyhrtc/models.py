"""Various IP models for HRTC and variants."""

from pulp import LpProblem, LpMaximize, LpVariable, lpSum, LpStatusOptimal


class MAX_SMTI_IP(LpProblem):

    def __init__(self, instance, name=None):
        if instance.number_of_couples_left() != 0:
            raise Exception("This model does not support couples")
        if name is None:
            name = "SMTI"
        super().__init__(name, LpMaximize)
        self._instance = instance
        self._built = False

        """Map from each variable name (as a string) to the actual variable object.
        _variables_lr is a map such that _variables_lr[left][right] gives the
        variable where Agent left is assigned to Agent right
        _variables_rl is a map such that _variables_rl[right][left] gives the
        variable where Agent right is assigned to Agent left
        """
        self._variables_lr = None
        self._variables_rl = None


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
                     f"left.{left.ident}.capacity")
        for right in self._instance.single_agents_right:
            # If right.ident isn't in here, then this right agent has no
            # preferences.
            if right.ident not in self._variables_rl:
                continue
            self += (lpSum(self._variables_rl[right.ident].values()) <= 1,
                     f"right.{right.ident}.capacity")

    def _make_stability_constraints(self):
        """Makes the stability constraints.
        """
        for left in self._instance.single_agents_left:
            for right_id in left.acceptable_agents():
                right = self._instance.single_agent_right(right_id)
                xiq = lpSum([self._variables_lr[left.ident][other]
                             for other in left.as_good_as(right.ident)])
                xpj = lpSum([self._variables_rl[right.ident][other]
                             for other in right.as_good_as(left.ident)])
                self += 1 - xiq <= xpj, f"{left.ident}.{right.ident}.stability"

    def build_model(self):
        """Build the model.
        """
        if self._built:
            return
        self._make_variables()
        self._make_capacity_constraints()
        self._make_stability_constraints()
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
