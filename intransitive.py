#!/opt/homebrew/bin/python3

import itertools

dice_set1 = [[1, 2, 5, 6,  7,  9,  10, 11, 14, 15, 16, 18],
             [1, 3, 4, 5,  8,  9,  10, 12, 13, 14, 17, 18],
             [2, 3, 4, 6,  7,  8,  11, 12, 13, 15, 16, 17]]

dice_set2 = [[1, 4, 9, 11, 13, 17, 19, 21, 27, 29, 31, 35],
             [2, 5, 7, 10, 15, 18, 20, 23, 25, 28, 33, 36],
             [3, 6, 8, 12, 14, 16, 22, 24, 26, 30, 32, 34]]

for r in itertools.combinations(range(len(dice_set1)), 2):
  print(r)
