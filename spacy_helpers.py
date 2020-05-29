#
# Some helper functions that operate on spacy objects

def get_all_conjuncts(token: spacy.Token) -> list:
        """
        Return all conjuncts of the token (words connected to it by conjunctions)

        Parameters:
            token: spacy Token (word)
        Returns:
            list of spacy Tokens
        """
        conjs = []
        current = get_shallow_conjuncts(token)
        while current:
            conjs += current
            current = get_shallow_conjuncts(current[0])
        return conjs


def get_shallow_conjuncts(token: spacy.Token) -> list:
    """
    Return all immediate child conjuncts of the token.
    This is different from the token.conjuncts attribute because this
    only includes conjuncts that are children of the token.

    Parameters:
        token: spacy Token (word)
    Returns:
        list of spacy Tokens
    """

    return [child for child in token.children if child.dep_ == 'conj']


def get_objects(token):
    
    head, tail = split_conjuncts(token)
    objects = [head]

    while tail:
        
        head, tail = split_conjuncts(tail)
        objects.append(head)

    return objects


def split_conjuncts(span):
    # Get the first conjunct
    conjs = get_shallow_conjuncts(span.root)

    if conjs:
        conj = conjs[0]

        # Split around the coordinating conjunction, if there is one
        if conj.nbor(-1).dep_ == 'cc':
            head = span.doc[: conj.i - 1]
        else:
             head = span.doc[: conj.i]

        tail = span.doc[conj.i :]

        return head, tail

    else:
        return span, None


def get_direct_objects(token: spacy.Token) -> list:
    """
    Return all direct objects of the token.

    Parameters:
        token: spacy Token (word)
    Returns:
        list of spacy Tokens
    """
    return [child for child in token.children if child.dep_ == 'dobj']

