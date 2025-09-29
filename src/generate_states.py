import random, itertools

# 2 nur links 2 nur recht 5 beide


def generate_states(pitches_left, pitches_right, n_left, n_right,n_cross, fingers_used = 2,  seed = None):
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

    if fingers_used <= 5:
        all_dyads_left = [frozenset(combo) for combo in itertools.combinations(L, fingers_used)]
        all_dyads_right = [frozenset(combo) for combo in itertools.combinations(R,fingers_used)]
    else:
        n_left = 0
        n_right = 0
        Warning("You are using more than 5 fingers per hand one handed inpossible only uses both hands")


    # Cross-hand: mindestens 1 von links UND mindestens 1 von rechts
    all_dyads_cross = []
    if fingers_used <= 1:
        all_dyads_cross = [frozenset(combo) for combo in itertools.combinations(L+R, fingers_used)]
    else:
        for combo in itertools.combinations(L+R, fingers_used):
            # Prüfe ob mindestens eine Note aus L und mindestens eine aus R dabei ist
            has_left = any(note in L for note in combo)
            has_right = any(note in R for note in combo)
            if has_left and has_right:
                all_dyads_cross.append(frozenset(combo))

    # to prevent errors that not enough chords for rng.sample
    if fingers_used == 4:
        Warning("You are using 4 fingers per hand. Only 5 different states possible per hand if only one hand is used."
        "if not 9 states it will be filled up with cross hand states")
        if n_left > 5:
            n_left = 5
        if n_right > 5:
            n_right = 5
    if fingers_used == 5:
        Warning("You are using 5 fingers per hand. Only 1 different state possible per hand if only one hand is used."
                "if not 9 states it will be filled up with cross hand states")
        if n_left > 1:
            n_left = 1
        if n_right > 1:
            n_right = 1
    
    if (n_left+n_right+n_cross != 9):
        x = 9 - (n_left+n_right+n_cross)
        n_cross += x

    states = []
    if fingers_used <=5: ## one handed not possible therefore deactivated
        states.extend(rng.sample(all_dyads_left, n_left))
        states.extend(rng.sample(all_dyads_right, n_right))
    states.extend(rng.sample(all_dyads_cross, n_cross))
    rng.shuffle(states)

    return states



