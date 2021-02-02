from spacy.tokens import Span, Token
#
# Some helper functions that operate on spacy objects

def get_all_conjuncts(token: Token) -> list:
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


def get_shallow_conjuncts(token: Token) -> list:
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


def split_conjuncts(span: Span):
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


def get_direct_objects(token: Token) -> list:
    """
    Return all objects of the token.

    Parameters:
        token: spacy Token (word)
    Returns:
        list of spacy Tokens
    """
    # get all immediate direct objects of the token
    dobjs = [child for child in token.children if child.dep_ == 'dobj']
    if len(dobjs) == 0:
        return []
    else:
        objs = [d for d in dobjs]
        for d in dobjs:
            objs += get_all_conjuncts(d)
        return objs

def and_conjuncts(token):
    return [token] + list(token.conjuncts)

def get_prepositional_objects(token):
    """
    Return (nested) prepositional objects of the token.

    Parameters:
        token: spacy Token (word)
    Returns:
        list of spacy Tokens
    """
    prepositional_objects = []
    prepositions = [child for child in token.children if child.dep_ == 'prep']
    print('prepositions:', prepositions)
    for prep in prepositions:
        objects = []
        for child in prep.children:
            if child.dep_ == 'pobj':
                objects += and_conjuncts(child)

        print('objects:', objects)
        prepositional_objects += objects
        for obj in objects:
            prepositional_objects += get_prepositional_objects(obj)
    return prepositional_objects


def get_top_noun(span: Span):
    """
    Return the noun that is highest in the span syntax

    Parameters:
        span: spacy.Span which may contain a noun
    Returns:
        spacy Token object
    """

    # search the phrase syntax breadth-first
    queue = [span.root]
    while queue:
        current = queue.pop(0)
        # may be a noun or proper noun
        if current.pos_ in ['NOUN', 'PROPN']:
            return current
        for child in current.children:
            queue.append(child)

    # there might not be a noun
    return None

def get_all_nouns(span: Span):
    """
    Return a list of all nouns in the span

    Parameters:
        span: spacy.Span which may contain a noun
    Returns:
        spacy Token object
    """
    return [token for token in span if token.pos_ in ['NOUN', 'PROPN']]


