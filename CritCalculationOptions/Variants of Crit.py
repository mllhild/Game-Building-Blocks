#The basic values for these examples:
crit_chance = 0.3

base_damage = 100
crit_multi = 2.0
crit_flat = 75

critM = base_damage * crit_multi
critF = base_damage + crit_flat
critMF = base_damage * crit_multi + crit_flat

# simple crit
# inconsistent in short fights
# code
attacks = []
num_attacks = 10
for _ in range(num_attacks):
  if random.random() < crit_chance:
     attacks.append(critM)
  else:
     attacks.append(base_damage)

# accumulating crit simple (more damage)
# with each miss crit chance increases, until a hit occures then chance is reset
# remember to reset the accumulation each time the player leaves combat. Else strategies like hitting a mob a few times to stack crit chance and then hitting the enemy champion can be born.
# code
attacks = []
num_attacks = 10
current_crit_chance = 0 # leave at 0 if you want the first hit to never be a crit. This is nice when you dont want low health player to be oneshot when they dont expect it.
current_crit_chance = crit_chance # use this for your player damage output, since criting is nice, but getting critted not so much
for _ in range(num_attacks):
  if random.random() < current_crit_chance:
     current_crit_chance = crit_chance # set to zero if you want to never have two consecutive crits
     attacks.append(critM)
  else:
     current_crit_chance += crit_chance
     attacks.append(base_damage)

# accumulating crit with negative (standard damage)
# with each miss crit chance increases, until a hit occures then chance is reduced by 100%
# current_crit_chance can become negative
# code
attacks = []
num_attacks = 10
current_crit_chance = 0  
current_crit_chance = crit_chance 
for _ in range(num_attacks):
  if random.random() < current_crit_chance:
     current_crit_chance = current_crit_chance - 1 # set to zero if you want to never have two consecutive crits
     attacks.append(critM)
  else:
     current_crit_chance += crit_chance
     attacks.append(base_damage)


# gaussian crit
# random destribution is biased towards the center
# low crit almost never crits
# real critchance increases a lot as it goes towards 50% display crit chance
# real crit chance barely increases from 80% to 100% display crit chance
from scipy.stats import norm
mean = 0.5
std_dev = 0.1
current_crit_chance = norm.cdf(crit_chance, loc=mean, scale=std_dev)


# front loaded crit
# any amount of crit results in the first strike critting
# counter resets after a certain time out of combat
# really only useful for PvE
# code
attacks = []
num_attacks = 10
if crit_chance > 0
  current_crit_chance = 1 
for _ in range(num_attacks):
  if current_crit_chance >= 1:
     attacks.append(critM)
     current_crit_chance -= 1
  else:
     current_crit_chance += crit_chance
     attacks.append(base_damage)


# average crit
# if fluctuations in damage prove too disruptive, simple damage increase might be in order
# its more consistent, yet less exciting
damage = base_damage * ( 1 + crit_chance * crit_multi ) + ( crit_chance * crit_flat )
