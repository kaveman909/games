#!/opt/homebrew/bin/python3

import itertools


def combinations(l1, l2):
  for i in range(len(l1)):
    for j in range(len(l2)):
      yield (l1[i], l2[j])


deck1 = [['A', [1, 2, 5, 6,  7,  9,  10, 11, 14, 15, 16, 18]],
         ['B', [1, 3, 4, 5,  8,  9,  10, 12, 13, 14, 17, 18]],
         ['C', [2, 3, 4, 6,  7,  8,  11, 12, 13, 15, 16, 17]]]

deck2 = [['D', [1, 4, 9, 12, 14, 17, 19, 22, 27, 30, 32, 35]],
         ['E', [2, 5, 7, 10, 15, 18, 20, 23, 25, 28, 33, 36]],
         ['F', [3, 6, 8, 11, 13, 16, 21, 24, 26, 29, 31, 34]]]

for deck in [deck1, deck2]:
  stats = {}
  for first, second in itertools.combinations(deck, 2):
    first_name = first[0]
    second_name = second[0]
    combo = first_name + second_name

    # init stats for this particular combo
    stats[combo] = {}
    stats[combo]['win'] = 0
    stats[combo]['lose'] = 0
    stats[combo]['tie'] = 0
    stats[combo]['total'] = 0

    for a, b in combinations(first[1], second[1]):
      if a > b:
        stats[combo]['win'] += 1
      elif a == b:
        stats[combo]['tie'] += 1
      else:
        stats[combo]['lose'] += 1
      stats[combo]['total'] += 1
    

  print(stats)
