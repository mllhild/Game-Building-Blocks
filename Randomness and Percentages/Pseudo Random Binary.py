# True random contains two sequence patterns which players consider unnatural and hence think the game is cheating
# 1. Clumping 10100100000000100101111
# 2. Patterns 11001100011100001111, 1100110011001100

# Rules to counter it
# 1. If the newest value will produce a run of 4 or more, then there is a 75% chance
# to flip the newest value. This doesn’t make runs of 4 or more impossible, but progressively much less likely (the probability of a run of 4 occurring goes from 1/8
# to 1/128). Runs of a particular length can be prohibited altogether, but this will more negatively affect the integrity of the randomness.
# 2. If the newest value causes a repeating pattern of four values, like 11001100, then flip the last value (so that the sequence becomes 11001101).
# 3. If the newest value causes a repeating pattern of 111000 or 000111, then flip the last value.

import random

def generate_initial_sequence(length):
    return [random.randint(0, 1) for _ in range(length)]

def flip(bit):
    return 1 - bit

def has_run(sequence, run_length):
    if len(sequence) < run_length:
        return False
    count = 1
    for i in range(len(sequence) - 1, 0, -1):
        if sequence[i] == sequence[i - 1]:
            count += 1
            if count >= run_length:
                return True
        else:
            break
    return False

def has_repeating_pattern(sequence, pattern_length):
    if len(sequence) < pattern_length * 2:
        return False
    return sequence[-pattern_length:] == sequence[-2 * pattern_length:-pattern_length]

def matches_pattern(sequence, pattern):
    if len(sequence) < len(pattern):
        return False
    return sequence[-len(pattern):] == pattern

def filter_random_sequence(sequence):
    filtered = []
    for bit in sequence:
        # Try applying the three rules in order
        temp = filtered + [bit]
        triggered = False

        # Rule 1: Prevent runs of 4 or more (with 75% chance)
        if not triggered and has_run(temp, 4):
            if random.random() < 0.75:
                triggered = True

        # Rule 2: Prevent repeating pattern of 4
        if not triggered and has_repeating_pattern(temp, 4):
            triggered = True

        # Rule 3: Prevent 111000 or 000111
        if not triggered:
            if matches_pattern(temp, [1, 1, 1, 0, 0, 0]) or matches_pattern(temp, [0, 0, 0, 1, 1, 1]):
                triggered = True
                
        if triggered == True:
            bit = flip(bit)
        filtered.append(bit)

    return filtered

def to_str(seq):
    return ''.join(str(b) for b in seq)

# Example usage
random.seed(42)
length = 100
original = generate_initial_sequence(length)
filtered = filter_random_sequence(original)

print("Original: ", to_str(original))
print("Filtered: ", to_str(filtered))

