import random, itertools

# 2 nur links 2 nur recht 5 beide

states = []

pitches_left = {"C4": 60, "D4": 62, "E4": 64, "F4": 65, "G4": 67,}
pitches_right = {"C5": 72, "D5": 73, "E5": 74, "F5": 75, "G5": 76}

L = list(pitches_left.values())
R = list(pitches_right.values())

all_dyads_left = [frozenset(pair) for pair in itertools.combinations(L,2)]
all_dyads_right = [frozenset(pair) for pair in itertools.combinations(R,2)]
all_dyads_cross = [frozenset(pair) for pair in itertools.product(L,R)]

# states.extend(random.sample(all_dyads_left, 2))
# states.extend(random.sample(all_dyads_right, 2))
# states.extend(random.sample(all_dyads_cross, 5))

print(states)

# picks thwo distinct values from dict
# def sample_dyad_from(values_seq):
#         a, b = random.sample(values_seq, 2)
#         return frozenset({a,b})

# def sample_dyad_cross(left_seq, right_seq):
#     """Pick one from left, one from right."""
#     return frozenset({random.choice(left_seq),rand.choice(right_seq)})

# def pitch_states_one_hand(pitches):
#     states =[]
#     s1 = sample_dyad_from(list(pitches.values()))
#     s2 = sample_dyad_from(list(pitches.values()))
#     while s2 == s1:  # ensure they differ
#         s2 = sample_dyad_from(list(pitches.value))
#     states.extend[s1,s2]

# def pitch_states_both_hands(pitches_left, pitches_right):
#     states = []

#     s1 = sample_dyad_from(list(pitches_left.values()), list(pitches_right.values()))
#     s2 = sample_dyad_from(list(pitches_left.values()), list(pitches_right.values()))
#     s3 = sample_dyad_from(list(pitches_left.values()), list(pitches_right.values()))
#     s4 = sample_dyad_from(list(pitches_left.values()), list(pitches_right.values()))
    
#     while (s1 == s2 or s1 == s3 or s1 == s4):
#         if s1 == s2:
#             s2 = sample_dyad_from(list(pitches_left.values()), list(pitches_right.values()))
#         if s1 == s3:
#             s3 = sample_dyad_from(list(pitches_left.values()), list(pitches_right.values()))
#         if s1 == s4:
#             s4 = sample_dyad_from(list(pitches_left.values()), list(pitches_right.values()))
    
#     while (s2 == s3 or s2 == s4):
#         if s2 == s3:
#             s3 = sample_dyad_from(list(pitches_left.values()), list(pitches_right.values()))
#         if s2 == s4:
#             s4 = sample_dyad_from(list(pitches_left.values()), list(pitches_right.values()))
    
#     while (s3 == s4):
#         s4 = sample_dyad_from(list(pitches_left.values()), list(pitches_right.values()))
        
#     states.extend[s1,s2,s3,s4]
#     return states

# def generate_states(pitches_left = pitches_left, pitches_right = pitches_right):
#     states = []
    
    

#     # 2 left-only (unique dyads)
#     left_set = set()



print (list(all_dyads_left))
# print(all_dyads_right)
# print(all_dyads_cross)