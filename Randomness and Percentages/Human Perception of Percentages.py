# Humans are terrible at understanding percentages and estimating actual frequency based on them.
# They overestimate small chances, blinded by the lure of winning.
# Underestimate large chances, due to fear of failure.
# so you might want to tweak the real percentages behind the scenes to conform to what your players expect.

import numpy as np
import matplotlib.pyplot as plt

# more emotinal state
def prelecLow(p, alpha=0.50):
    return np.exp(-(-np.log(p))**alpha)

# often a good middle ground 
def prelecAverage(p, alpha=0.70):
    return np.exp(-(-np.log(p))**alpha)

# more logical and calm state 
def prelecHigh(p, alpha=0.80):
    return np.exp(-(-np.log(p))**alpha)


real_probs = np.linspace(0.01, 1.0, 500)
perceived_probs_low = prelecLow(real_probs)
perceived_probs_high = prelecHigh(real_probs)

plt.figure(figsize=(8, 6))
plt.plot(real_probs, real_probs, label="Real Probability", color="blue", linestyle="--")
plt.plot(real_probs, perceived_probs_low, label="Perceived Probability Emotional State", color="red", linewidth=2)
plt.plot(real_probs, perceived_probs_high, label="Perceived Probability Logical State", color="green", linewidth=2)

plt.title("Human Perception of Probability (Prelec Weighting)")
plt.xlabel("Actual Probability")
plt.ylabel("Perceived Probability")
plt.xticks(np.linspace(0, 1, 11), [f"{int(x*100)}%" for x in np.linspace(0, 1, 11)])
plt.yticks(np.linspace(0, 1, 11), [f"{int(x*100)}%" for x in np.linspace(0, 1, 11)])
plt.grid(True)
plt.legend()
plt.tight_layout()

plt.show()


