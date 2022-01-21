from nfa import NFA
import copy


def get_single_symbol_regex(symbol):
    """ Returns an NFA that recognizes a single symbol """

    nfa = NFA()
    nfa.add_state(1, True)
    nfa.add_transition(0, symbol, {1})

    return nfa


def shift(nfa, inc):
    """
    Increases the value of all states (including accept states and transition function etc)
    of a given NFA bya given value.

    This is useful for merging NFAs, to prevent overlapping states
    """
    # update NFA states
    new_states = set()
    for state in nfa.states:
        new_states.add(state + inc)
    nfa.states = new_states

    # update NFA accept states
    new_accept_states = set()
    for state in nfa.accept_states:
        new_accept_states.add(state + inc)
    nfa.accept_states = new_accept_states

    # update NFA transition function
    new_transition_function = {}
    for pair in nfa.transition_function:
        to_set = nfa.transition_function[pair]
        new_to_set = set()

        for state in to_set:
            new_to_set.add(state + inc)

        new_key = (pair[0] + inc, pair[1])
        new_transition_function[new_key] = new_to_set

    nfa.transition_function = new_transition_function


def merge(a, b):
    """Merges two NFAs into one by combining their states and transition function"""
    a.accept_states = b.accept_states
    a.states |= b.states
    a.transition_function.update(b.transition_function)
    a.alphabet |= b.alphabet


def get_concat(a, b):
    """ Concatenates two NFAs, ie. the dot operator """

    # number to add to each b state number
    # this is to ensure each NFA has separate number ranges for their states
    # one state overlaps; this is the state that connects a and b
    add = max(a.states)

    # shift b's state/accept states/transition function, etc.
    shift(b, add)

    # merge b into a
    merge(a, b)

    return a


def get_union(a, b):
    """Returns the resulting union of two NFAs (the '|' operator)"""

    # create a base NFA for the union
    nfa = NFA()

    # clear a and b's accept states
    a.accept_states = set()
    b.accept_states = set()

    # merge a into the overall NFA
    shift(a, 1)
    merge(nfa, a)

    # merge b into the overall NFA
    shift(b, max(nfa.states) + 1)
    merge(nfa, b)

    # add an empty string transition from the initial state to the start of a and b
    # (so that the NFA starts in the start of a and b at the same time)
    nfa.add_transition(0, "", {1, min(b.states)})

    # add an accept state at the end so if either a or b runs through,
    # this NFA accepts
    new_accept = max(nfa.states) + 1
    nfa.add_state(new_accept, True)
    nfa.add_transition(max(a.states), "", {new_accept})
    nfa.add_transition(max(b.states), "", {new_accept})

    return nfa


def get_kleene_star_nfa(nfa):
    """
    Wraps an NFA inside a kleene star expression
    (NFA passed in recognizes 0, 1 or many of the strings it originally recognized)
    """
    # clear old accept state
    nfa.accept_states = {}

    # shift NFA by 1 and insert new initial state
    shift(nfa, 1)
    nfa.add_state(0)

    # add new ending accept state
    last_state = max(nfa.states)
    new_accept = last_state + 1
    nfa.add_state(new_accept, True)
    nfa.add_transition(last_state, "", {new_accept})

    # add remaining empty string transitions
    nfa.add_transition(0, "", {1, new_accept})
    nfa.add_transition(last_state, "", {0})

    return nfa

def get_one_or_more_of_nfa(nfa):
    """
    Wraps an NFA inside the "one or more of" operator (plus symbol)

    Simply combines the concatenation operator and the kleene star operator.
    """

    # must make a copy of the nfa,
    # these functions operate on the nfa passed in, they do not make a copy
    return get_concat(copy.deepcopy(nfa), get_kleene_star_nfa(nfa))

def get_zero_or_one_of_nfa(nfa):
    """
    Wraps an NFA inside the "zero or one of" operator (question mark symbol)

    Simply uses the union operator, with one path for the empty string, and the other path
    for the NFA being wrapped.
    """

    return get_union(get_single_symbol_regex(""), nfa)

def get_regex_nfa(regex, indent=""):
    """Recursively builds an NFA based on the given regex string"""

    print("{0}Building NFA for regex:\n{0}({1})".format(indent, regex))
    indent += " " * 4

    # special symbols: +*.| (in order of precedence highest to lowest, symbols coming before that

    # union operator
    bar_pos = regex.find("|")
    if bar_pos != -1:
        # there is a bar in the string; union both sides
        # (uses the leftmost bar if there are more than 1)
        return get_union(
            get_regex_nfa(regex[:bar_pos], indent),
            get_regex_nfa(regex[bar_pos + 1:], indent)
        )

    # concatenation operator
    dot_pos = regex.find(".")
    if dot_pos != -1:
        # there is a dot in the string; concatenate both sides
        # (uses the leftmost dot if there are more than 1)
        return get_concat(
            get_regex_nfa(regex[:dot_pos], indent),
            get_regex_nfa(regex[dot_pos + 1:], indent)
        )

    # kleene star operator
    star_pos = regex.find("*")
    if star_pos != -1:
        # there is an asterisk in the string; wrap everything before it in a kleene star expression
        # (uses the leftmost dot if there are more than 1)
        star_part = regex[:star_pos]
        trailing_part = regex[star_pos + 1:]
        kleene_nfa = get_kleene_star_nfa(get_regex_nfa(star_part, indent))

        if len(trailing_part) > 0:
            return get_concat(
                kleene_nfa,
                get_regex_nfa(trailing_part, indent)
            )
        else:
            return kleene_nfa

    # "one or more of" operator ('+' symbol)
    plus_pos = regex.find("+")
    if plus_pos != -1:
        # there is a plus in the string; wrap everything before it in the "one or more of" expression
        # (uses the leftmost plus if there are more than 1)

        plus_part = regex[:plus_pos]
        trailing_part = regex[plus_pos + 1:]
        plus_nfa = get_one_or_more_of_nfa(get_regex_nfa(plus_part, indent))

        if len(trailing_part) > 0:
            return get_concat(
                plus_nfa,
                get_regex_nfa(trailing_part, indent)
            )
        else:
            return plus_nfa

    # "zero or one of" operator ('?' symbol)
    qmark_pos = regex.find("?")
    if qmark_pos != -1:
        # there is a question mark in the string; wrap everything before it in the "zero or one of" expression
        # (uses the leftmost question mark if there are more than 1)

        leading_part = regex[:qmark_pos]
        trailing_part = regex[qmark_pos + 1:]
        zero_or_one_of_nfa = get_zero_or_one_of_nfa(get_regex_nfa(leading_part, indent))

        if len(trailing_part) > 0:
            return get_concat(
                zero_or_one_of_nfa,
                get_regex_nfa(trailing_part, indent)
            )
        else:
            return zero_or_one_of_nfa

    # no special symbols left at this point

    if len(regex) == 0:
        # base case: empty nfa for empty regex
        return NFA()
    elif len(regex) == 1:
        # base case: single symbol is directly turned into an NFA
        return get_single_symbol_regex(regex)
    else:
        # multiple characters left; apply implicit concatenation between the first character
        # and the remaining characters
        return get_concat(
            get_regex_nfa(regex[0], indent),
            get_regex_nfa(regex[1:], indent)
        )
