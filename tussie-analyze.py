#!/opt/homebrew/opt/python@3.9/libexec/bin/python3

from enum import Enum, auto, unique
import itertools
import matplotlib.pyplot as plt


LONGEST_NAME_FLOWER = 13
LONGEST_NAME_COLOR = 6


@unique
class Color(Enum):
  WHITE = auto()
  YELLOW = auto()
  PURPLE = auto()
  PINK = auto()
  RED = auto()


class Card:
  def __init__(self, name, color: Color, hearts, scoring):
    self.name = name
    self.color = color
    self.hearts = hearts
    self.keepsake = False
    self.position = 0
    self.scoring = scoring


def get_adjacent(cards: list[Card], position):
  adjacent = []
  before = position - 1
  after = position + 1
  if before >= 0:
    adjacent.append(cards[before])
  try:
    adjacent.append(cards[after])
  except IndexError:
    pass
  return adjacent


def cards_of_a_color(cards: list[Card], color: Color):
  return sum(1 for card in cards if card.color == color)


def display_arrangement(cards: list[Card], points):
  for card in cards:
    print("{}({})({})".format(
        card.name, card.color.name[0:2], 'K' if card.keepsake else 'B'), end='\t')
  print(points)


def no_scoring(*_):
  return 0


def calculate_points(cards: list[Card]):
  points = 0
  points += sum(card.hearts for card in cards)
  points += sum(card.scoring(cards, card.position) for card in cards)
  return points


all_points = []
all_arrangements = []


def analyze_arrangement(arrangement: list[Card]):
  length = len(arrangement)
  for keepsake_map in itertools.product([False, True], repeat=length):
    for i in range(length):
      arrangement[i].position = i
      arrangement[i].keepsake = keepsake_map[i]
    try:
      orchid_index = [card.name for card in arrangement].index("Orchid")
      max_points = 0
      max_arrangement = []
      for color in Color:
        arrangement[orchid_index].color = color
        points = calculate_points(arrangement)
        if points > max_points:
          max_points = points
          max_arrangement = arrangement
    except ValueError:
      max_points = calculate_points(arrangement)
      max_arrangement = arrangement
    all_points.append(max_points)
    all_arrangements.append([max_arrangement, max_points])
    # display_arrangement(max_arrangement, max_points)


def update_stats(stats, field_name, points):
  try:
    stats[field_name][0] += 1
    stats[field_name][1] += points
    stats[field_name][2] = max(stats[field_name][2], points)
    stats[field_name][3] = min(stats[field_name][3], points)

  except KeyError:
    stats[field_name] = [1, points, points, points]


def compute_and_print_stats(stats, longest_name):
  list_stats = list(stats.items())
  list_stats.sort(key=lambda stat: stat[1][1] / stat[1][0])

  for field_name, stats in list_stats:
    print("{}:\t{} max\t{} min\t{:.2f} avg".format(field_name + " " *
          (longest_name - len(field_name)), stats[2], stats[3], stats[1]/stats[0]))


if __name__ == "__main__":
  cards = [
      Card("Hyacinth", Color.PURPLE, 0, lambda cards, _: 3 if sum(
          card.hearts for card in cards) == 0 else 0),
      Card("Honeysuckle", Color.YELLOW, 1, lambda cards, position: sum(
          not card.keepsake for card in get_adjacent(cards, position))),
      Card("Forget-Me-Not", Color.PURPLE, 1, lambda cards,
           position: sum(card.hearts for card in get_adjacent(cards, position))),
      Card("Carnation", Color.YELLOW, 0, lambda cards, _: len(
          {card.color for card in cards})),
      Card("Peony", Color.PINK, 1, lambda cards, _: 2 if sum(
          not card.keepsake for card in cards) == 2 else 0),
      Card("Red Rose", Color.RED, 0, lambda cards,
           _: sum(card.hearts for card in cards)),
      Card("Gardenia", Color.WHITE, 0, lambda cards,
           _: sum(card.keepsake for card in cards)),
      Card("Amaryllis", Color.RED, 0, lambda cards,
           _: sum(not card.keepsake for card in cards)),
      Card("Pink Rose", Color.PINK, 0,
           lambda cards, _: cards_of_a_color(cards, Color.PINK)),
      Card("Red Tupid", Color.RED, 0,
           lambda cards, _: cards_of_a_color(cards, Color.RED)),
      Card("Violet", Color.PURPLE, 0,
           lambda cards, _: cards_of_a_color(cards, Color.PURPLE)),
      Card("Daisy", Color.WHITE, 0, lambda cards, _: sum(
          1 for card in cards if card.hearts == 0) - 1),
      Card("Camellia", Color.RED, 1, no_scoring),
      Card("Phlox", Color.PINK, 2, no_scoring),
      Card("Orchid", Color.WHITE, 1, no_scoring),
      Card("Pink Larkspur", Color.PINK, 0, no_scoring),
      Card("Snapdragon", Color.PURPLE, 1, no_scoring),
      Card("Marigold", Color.YELLOW, 3, no_scoring)
  ]

  # NOTE: this assumes that "Marigold" is the last Card in the list.
  # "Marigold" arrangements are only 3 cards in length, so need this special case.
  for comb in itertools.combinations(cards[0:-1], 2):
    lcomb = list(comb)
    lcomb.append(cards[-1])
    for tup_arrangement in itertools.permutations(lcomb):
      arrangement = list(tup_arrangement)
      analyze_arrangement(arrangement)

  for tup_arrangement in itertools.permutations(cards[0:-1], 4):
    arrangement = list(tup_arrangement)
    analyze_arrangement(arrangement)

  # Data plotting, analysis

  flower_stats = {}
  color_stats = {}
  for arrangement in all_arrangements:
    points = arrangement[1]
    for flower in arrangement[0]:
      update_stats(flower_stats, flower.name, points)
      update_stats(color_stats, flower.color.name, points)

  compute_and_print_stats(flower_stats, LONGEST_NAME_FLOWER)
  compute_and_print_stats(color_stats, LONGEST_NAME_COLOR)

  fig, axs = plt.subplots(1, 1, sharey=True, tight_layout=True)
  counts, edges, bars = axs.hist(all_points, bins=14)

  sum_counts = 0
  sum_all = sum(counts)

  for i, count in enumerate(counts):
    sum_counts += count
    print("{} count: {} {:.2f}%".format(i+1, count, sum_counts/sum_all*100))

  plt.bar_label(bars)
  plt.show()
