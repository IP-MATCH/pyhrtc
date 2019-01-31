"""Various IP models for HRTC and variants."""

import pulp


class MAX_SMTI_IP(pulp.LpProblem):

    def __init__(self, instance, name=None):
        if name is None:
            name = "SMTI"
        self.super().__init__(name, pulp.LpMaximize)
        self._instance = instance

    def build_model(self):
        """Build the model.
        """

