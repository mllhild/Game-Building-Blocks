# while most things in nature follow a gaussian (= normal) destribution you might want to use it to simulate randomness in your game
# Rather than using random.gauss that has outputs from +inf to -inf, 
# for game design its better to have constrained random gaussian either via cliping (more expensive)
# or by adding 3 random numbers together which is enough for a pseudo gaussian destribution at cheap cost

import random
import matplotlib.pyplot as plt
from collections import Counter
import time

start_time = time.time()
numbersR1 = [random.random() for _ in range(1000)]
end_time = time.time()
generation_time = end_time - start_time
print(f"Time to generate 1000 random numbers: {generation_time:.9f} seconds")

start_time = time.time()
numbers1 = [random.random() for _ in range(1000)]
numbers2 = [random.random() for _ in range(1000)]
numbersR2 = [(a + b)/2 for a, b in zip(numbers1, numbers2)]
end_time = time.time()
generation_time = end_time - start_time
print(f"Time to generate 2000 random numbers: {generation_time:.9f} seconds")


start_time = time.time()
numbers1 = [random.random() for _ in range(1000)]
numbers2 = [random.random() for _ in range(1000)]
numbers3 = [random.random() for _ in range(1000)]
numbersR3 = [(a + b + c)/3 for a, b, c in zip(numbers1, numbers2, numbers3)]
end_time = time.time()
generation_time = end_time - start_time
print(f"Time to generate 3000 random numbers: {generation_time:.9f} seconds")

start_time = time.time()
numbers1 = [random.random() for _ in range(1000)]
numbers2 = [random.random() for _ in range(1000)]
numbers3 = [random.random() for _ in range(1000)]
numbers4 = [random.random() for _ in range(1000)]
numbers5 = [random.random() for _ in range(1000)]
numbersR5 = [(a + b + c + d + e)/5 for a, b, c, d, e in zip(numbers1, numbers2, numbers3, numbers4, numbers5)]
end_time = time.time()
generation_time = end_time - start_time
print(f"Time to generate 5000 random numbers: {generation_time:.9f} seconds")

start_time = time.time()
numbers1 = [random.random() for _ in range(1000)]
numbers2 = [random.random() for _ in range(1000)]
numbers3 = [random.random() for _ in range(1000)]
numbers4 = [random.random() for _ in range(1000)]
numbers5 = [random.random() for _ in range(1000)]
numbers6 = [random.random() for _ in range(1000)]
numbers7 = [random.random() for _ in range(1000)]
numbersR7 = [(a + b + c + d + e + f + g)/7 for a, b, c, d, e, f, g in zip(numbers1, numbers2, numbers3, numbers4, numbers5, numbers6, numbers7)]
end_time = time.time()
generation_time = end_time - start_time
print(f"Time to generate 7000 random numbers: {generation_time:.9f} seconds")


start_time = time.time()
numbersG1 = [max(min(random.gauss(0.5, 0.15), 1), 0) for _ in range(1000)]
end_time = time.time()
generation_time = end_time - start_time
print(f"Time to generate 1000 random gaussian numbers: {generation_time:.9f} seconds")

datasets = [
    (numbersG1, 'Gauss scaled and clipped', 'black'),
    (numbersR1, 'Uniform 1', 'green'),
    (numbersR2, 'Uniform +2', 'green'),
    (numbersR3, 'Uniform +3', 'green'),
    (numbersR5, 'Uniform +5', 'green'),
    (numbersR7, 'Uniform +7', 'green'),
]

fig, axs = plt.subplots(3, 2, figsize=(10, 8), sharex=True)

axs = axs.flatten()

for ax, (data, label, color) in zip(axs, datasets):
    ax.hist(data, bins=50, color=color, edgecolor='black', alpha=0.6, label=label)
    ax.set_ylabel('Frequency')
    ax.legend()
    ax.grid(True, axis='y', linestyle='--', alpha=0.5)

axs[-1].set_xlabel('Value')


plt.tight_layout()
plt.show()



