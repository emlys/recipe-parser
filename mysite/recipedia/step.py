class Step:

    def __init__(self, span):
        """Instantiate a Step.
        Args:

            text:
        """
        self.span = span
        self.verb = None
        self.labels = {}

    def set_verb(self, token_index):
        """Mark a token of this Step as the main verb.
        Args:
            token_index (int): index of token to label in self.span
        Returns:
            None
        """
        self.verb = token_index

    def as_dict(self):
        step_dict = {
            'tokens': {token.i: token.text for token in self.span},
            'verb': self.verb,
            'labels': self.labels,
            'full_text': self.span.text
        }
        return step_dict



