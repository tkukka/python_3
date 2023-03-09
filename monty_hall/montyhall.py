#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Monty Hall Problem
# https://en.wikipedia.org/wiki/Monty_Hall_problem
from random import shuffle, choice

GOAT = 0
CAR = 1
TEXT = ['goat', 'car']
N = 100000
PRIZES = [GOAT, GOAT, CAR]
DOORS = [0, 1, 2]

# ----------------------------------------------------------------------
# Monty must pick any door that hides a goat
def monty_pick(player_pick):
    s = set(DOORS)
    s2 = s - {player_pick}

    if PRIZES[player_pick] == CAR:
       #print(choice(list(s2)))
       return choice(list(s2))
   
    # Goat picked. Monty picks the other goat
    d = list(s2)
    
    if PRIZES[d[0]] == CAR:
        return d[1]
    
    return d[0]
# ----------------------------------------------------------------------
def door_switch(player_pick, monty_pick):
    s = set(DOORS) - {player_pick, monty_pick}
    #print(int(s.pop()))
    return int(s.pop())
# ----------------------------------------------------------------------
def main():
    print('Monty Hall problem. Iterations:', N)
    thresh = int(N / 10)
    wins_stick = 0
    wins_switch = 0
    
    for i in range(N):
    
        if i % thresh == 0:
            print('.', end = '')
        
        shuffle(PRIZES)
        # Player's first choice
        pick = choice(DOORS)
#        print('Person picks a door #', pick, '. The prize, not shown, is a', 
#              TEXT[PRIZES[pick]])
        
        mpick = monty_pick(pick)
#        print('Monty reveals a door #', mpick, '. The prize is a', 
#              TEXT[PRIZES[mpick]])
        
        # Player's alternative choice
        pick2 = door_switch(pick, mpick)
    
        if PRIZES[pick] == CAR:
            wins_stick += 1
            
        if PRIZES[pick2] == CAR:
            wins_switch += 1
           
    print()
#    print('Wins by sticking with the door:', wins_stick, '(', 100 * wins_stick
#                                                           / N, '%)')
#    
#    print('Wins by changing your mind:', wins_switch, '(', 100 * wins_switch /
#                                                        N, '%)') 
       
    print(f'Wins by sticking with the door: {wins_stick} '
                  f'({ 100 * wins_stick / N:.{3}}%)')
    
    print(f'Wins by changing your mind: {wins_switch} '
                  f'({ 100 * wins_switch / N:.{3}}%)')        
# ----------------------------------------------------------------------
if __name__ == "__main__":
    main()


