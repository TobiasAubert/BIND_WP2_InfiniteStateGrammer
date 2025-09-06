import random, itertools

# 2 nur links 2 nur recht 5 beide


def generate_states(pitches_left, pitches_right, n_left=2, n_right=2,n_cross=5, seed = None):
    """
    Generate dyad states from two pitch dictionaries. A seed is manditory to replicate states if needed.
    It generets dyads left-left, right-right, left-right
    The order of the dyads will be shuffeld before returned

    Args:
        pitches_left (dict[str, int]): Mapping note names to MIDI values for left hand.
        pitches_right (dict[str, int]): Mapping note names to MIDI values for right hand.
        n_left (int): Number of left-hand dyads to sample.
        n_right (int): Number of right-hand dyads to sample.
        n_cross (int): Number of cross-hand dyads to sample.
        seed (int | None): Random seed for reproducibility.

    Returns:
        list[frozenset[int]]: A list of dyads, where each dyad is a frozenset of two MIDI pitches.
        int seed (which seed)

    Example:
        >>> generate_states({"C4": 60, "D4": 62}, {"C5": 72, "E5": 76}, seed=1)
        [frozenset({60, 62}), frozenset({72, 76}), frozenset({60, 72})]
    """


    if seed is None:
        raise ValueError("You must provide a random seed for reproducibility.")
    
    rng = random.Random(seed)
    

    L = list(pitches_left.values())
    R = list(pitches_right.values())

    all_dyads_left = [frozenset(pair) for pair in itertools.combinations(L,2)]
    all_dyads_right = [frozenset(pair) for pair in itertools.combinations(R,2)]
    all_dyads_cross = [frozenset(pair) for pair in itertools.product(L,R)]

    states = []
    states.extend(rng.sample(all_dyads_left, 2))
    states.extend(rng.sample(all_dyads_right, 2))
    states.extend(rng.sample(all_dyads_cross, 5))
    rng.shuffle(states)

    return states, seed



