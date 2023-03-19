#!/usr/bin/python3
# -*- coding: utf-8 -*-
import random
import collections

MAX_NUMBER = 6
N_DICE = 5
N_RETRIES = 2

ONES = 0
TWOS = 1
THREES = 2
FOURS = 3
FIVES = 4
SIXES = 5
ONE_PAIR = 6
TWO_PAIRS = 7
THREE_OF_A_KIND = 8
FOUR_OF_A_KIND = 9
SMALL_STRAIGHT = 10
LARGE_STRAIGHT = 11
FULL_HOUSE = 12
CHANCE = 13
YATZY = 14

SCORE_YATZY = 50
BONUS_THRESHOLD = 63
BONUS = 50
N_COMBINATIONS = YATZY + 1

COMBINATION_STR = ('Ones', 'Twos', 'Threes', 'Fours', 'Fives', 'Sixes',
                  'One Pair', 'Two Pairs', 'Three of a Kind',
                  'Four of a Kind', 'Small Straight', 'Large Straight',
                  'Full House', 'Chance', 'Yatzy')
COMBINATIONS = [i for i in range(N_COMBINATIONS)]
MAX_SCORE = [1 * N_DICE, 2 * N_DICE, 3 * N_DICE, 4 * N_DICE, 5 * N_DICE,
             6 * N_DICE, 2 * 6, 2 * 6 + 2 * 5, 3 * 6, 4 * 6, 15, 
             20, 3 * 6 + 2 * 5, 6 * N_DICE, SCORE_YATZY]
# ----------------------------------------------------------------------
def roll_dice(n=1):
    return random.choices(range(1, MAX_NUMBER + 1), k=n)
# ----------------------------------------------------------------------
def determine_combinations(dice):
    pips = collections.Counter()
    for die in dice:
        pips[die] += 1
    total_count = collections.Counter()
    for v in pips.values():
        total_count[v] += 1

    # combinations = []
    scores = {}
    s = sum(dice)
    mc = pips.most_common(1)[0][0]
    if total_count[5] == 1:
        # combinations.append(YATZY)
        scores[YATZY] = SCORE_YATZY
    elif total_count[4] == 1:
        # combinations.append(FOUR_OF_A_KIND)
        scores[FOUR_OF_A_KIND] = 4 * mc
    elif total_count[3] == 1 and total_count[2] == 1:
        # combinations.append(FULL_HOUSE)
        scores[FULL_HOUSE] = s
    elif total_count[1] == 5 and s == 15:
        # combinations.append(SMALL_STRAIGHT)
        scores[SMALL_STRAIGHT] = s
    elif total_count[1] == 5 and s == 20:
        # combinations.append(LARGE_STRAIGHT)
        scores[LARGE_STRAIGHT] = s
    elif total_count[3] == 1 and total_count[1] == 2:
        # combinations.append(THREE_OF_A_KIND)
        scores[THREE_OF_A_KIND] = 3 * mc
    elif total_count[2] == 2 and total_count[1] == 1:
        # combinations.append(TWO_PAIRS)
        elems = pips.most_common(2)
        mc = elems[0][0]
        mc2 = elems[1][0]
        scores[TWO_PAIRS] = 2 * mc + 2 * mc2
    elif total_count[2] == 1 and total_count[1] == 3:
        # combinations.append(ONE_PAIR)
        scores[ONE_PAIR] = 2 * mc

    # combinations.append(CHANCE)
    scores[CHANCE] = s

    for item in pips.items():
        n, c = item
        # combinations.append(n - 1)
        scores[n - 1] = n * c
    return scores
# ----------------------------------------------------------------------
def print_score_table(players):
    print('=============================================')
    print(' '.ljust(23), end='')
    for p in players:
        print(p.name.ljust(5), end='')
    print()

    for i in range(N_COMBINATIONS):
        c = i + 1
        index_str = f'[{c}]'
        print(f'{index_str:5}{COMBINATION_STR[i]:18}', end='')
        for p in players:
            if i in p.used_combinations:
                print(str(p.score[i]).rjust(4), end='')
            else:
                print(' '.rjust(4), end='')

        if i == SIXES:
            print('\n=============================================')
            print('     {0:18}'.format('Sum'), end='')
            for p in players:
                print(str(p.upper_score()).rjust(4), end='')
            print('\n---------------------------------------------')
            print('     {0:18}'.format('Bonus'), end='')
            for p in players:
                print(str(p.bonus).rjust(4) , end='')
            print('\n---------------------------------------------')
        elif i == YATZY:
            print('\n---------------------------------------------')
            print('     {0:18}'.format('Sum'), end='')
            for p in players:
                print(str(p.total_score()).rjust(4) , end='')
            print('\n=============================================')
        else:
            print('\n---------------------------------------------')

# ----------------------------------------------------------------------
# convert string input to an integer
def parse_input(inp):
    v = -1
    try:
        v = int(inp)
    except ValueError:
        print(f'{inp} not an accepted number. Must be an integer.')
    return v
# ----------------------------------------------------------------------
def humam_select_dice():
    redo = True
    while redo:
        redo = False
        indices = []
        selection = input('Dice to roll or none? ').strip().split(sep = ',')

        if selection[0] == '':
            break
        elif len(selection) > N_DICE:
            redo = True
        else:
            for item in selection:
                n = parse_input(item) - 1
                if not(0 <= n < N_DICE):
                    redo = True
                    break
                indices.append(n)

    return indices
# ----------------------------------------------------------------------
def scorable_combinations(player, dice):
    scores = determine_combinations(dice)
    possible = {}
    for k, v in scores.items():
        if k not in player.used_combinations:
            possible[k] = v
    return possible
# ----------------------------------------------------------------------
def dice_prompt(player, dice):
    possible = scorable_combinations(player, dice)

    print(player.name, ', your dice:', dice)
    for k, v in possible.items():
        hint = ' (max: ' + str(MAX_SCORE[k]) + ' Loss: ' + str(MAX_SCORE[k] - v) + ')'
        index_str = '[{0}]:'.format(k + 1)
        print(index_str, COMBINATION_STR[k], ':', v, hint)

    zeros = list((set(COMBINATIONS) - player.used_combinations) - set(possible.keys()))
    if zeros:
        print('Other(s): 0')
        for i in zeros:
            print(COMBINATION_STR[i], ', Loss:', MAX_SCORE[i])
    return possible
# ----------------------------------------------------------------------
def human_play(player, dice):
    possible = dice_prompt(player, dice)
    for tries in range(N_RETRIES):
        reroll = humam_select_dice()
        if not reroll:
            break
        else:
            for i in reroll:
                dice[i] = roll_dice(1)[0]
            possible = dice_prompt(player, dice)

    left = None
    if (N_COMBINATIONS - len(player.used_combinations)) == 1:
        left = list(set(COMBINATIONS) - player.used_combinations)[0]

    redo = True
    while redo:
        redo = False
        if left is None:
            selection = input('Place? ').strip()
            n = parse_input(selection) - 1
        else:
            n = left

        if not(0 <= n < N_COMBINATIONS):
            redo = True
        else:
            ret, points = player.fill_combination(n, possible)
            redo = not ret
    print('Scoring:', COMBINATION_STR[n], ', score:', points)
    input('Press Enter')
# ----------------------------------------------------------------------
class Player:
    def __init__(self, n, h = None):
        self.name = n
        if h is None:
            self.human = False
        else:
            self.human = h
        self.score = [0 for i in range(N_COMBINATIONS) ]
        self.bonus = 0
        self.total = 0
        self.used_combinations = set()
    def upper_score(self):
        us = sum(self.score[ONES:ONE_PAIR])
        if us >= BONUS_THRESHOLD:
            self.bonus = BONUS
        return us
    def lower_score(self):
        return sum(self.score[ONE_PAIR:])
    def total_score(self):
        self.total =  self.upper_score() + self.bonus + self.lower_score()
        return self.total
    def fill_combination(self, comb, scores):
        if not(ONES <= comb <= YATZY):
            return False, 0
        if comb in self.used_combinations:
            return False, 0

        try:
            points = scores[comb]
        except KeyError:
            points = 0

        self.score[comb] = points
        self.used_combinations.add(comb)
        return True, points
# ----------------------------------------------------------------------
def main():
    p = Player('hk', True)
    p2 = Player('mm', True)
    # p.fill_combination(YATZY, x)
    # print(p.total_score())
    # p.fill_combination(ONE_PAIR, x)
    # print(p.total_score())
    # p.fill_combination(TWO_PAIRS, x)
    # print(p.total_score())
    # p.score = [ 1, 10, 15, 20, 25, 30, 12, 22, 0, 24, 15, 20, 28, 30, 50]
    p.total_score()
    # p.used_combinations = set(COMBINATIONS)
    # p2.score = [ 2, 10, 15, 20, 25, 30, 12, 22, 18, 24, 0, 20, 28, 14, 50]
    p2.total_score()
    # p2.used_combinations = set(COMBINATIONS)
    players = [p]
    n_score_card_ready = 0

    while n_score_card_ready < len(players):
        print_score_table(players)

        for p in players:
            dice = roll_dice(N_DICE)

            if p.human:
                human_play(p, dice)

            if len(p.used_combinations) >= N_COMBINATIONS:
                   n_score_card_ready += 1

    print('Final scores:')
    print_score_table(players)
    print()
# ----------------------------------------------------------------------
if __name__ == "__main__":
    main()
