#!/usr/bin/python3
# -*- coding: utf-8 -*-
import random
import decimal as dec
LIST_MAX = 5
PARTIES_MAX = 3
# ----------------------------------------------------------------------
class Candidate:
    def __init__(self, name, party):
        self.name = name
        self.party = party
        self.n_votes = 0
        self.quotient = 0

    # def vote(self):
    #     self.n_votes += 1
    #     self.party.vote()
    def set_votes(self, n):
        self.n_votes = n

    def __str__(self):
        return self.name
# ----------------------------------------------------------------------
class Party:
    def __init__(self, name):
        self.name = name
        self.n_votes = 0
        self.candidates = []
    def add_candidate(self, candidate):
        self.candidates.append(candidate)
    # def vote(self):
    #     self.n_votes += 1
    def total_count(self):
        s = 0
        for c in self.candidates:
            s += c.n_votes
        self.n_votes = s
    def __str__(self):
        return self.name
# ----------------------------------------------------------------------
def register_candidates(parties):
    for party in parties:
        n = random.randint(1, LIST_MAX)
        for i in range(n):
            name = str(party) + '_Can_' + str(i + 1)
            cand = Candidate(name, party)
            party.add_candidate(cand)
# ----------------------------------------------------------------------
def create_parties():
    parties = [Party('Par_' + str(n + 1)) for n in range(PARTIES_MAX) ]
    return parties
# ----------------------------------------------------------------------
def print_candidates(parties):
    for party in parties:
        print(str(party) + ':')
        for c in party.candidates:
            print(c)
# ----------------------------------------------------------------------
def cast_votes(parties):
    total = 0
    for party in parties:
        for c in party.candidates:
            c.set_votes(random.randint(1, 100))
        party.total_count()
        print('Party: ', party, ' votes:', party.n_votes)
        total += party.n_votes
    print(f'Total votes {total}')
# ----------------------------------------------------------------------
def determine_quotients(parties):
    for party in parties:
        n = 1
        for c in sorted(party.candidates, key=lambda cand: cand.n_votes, reverse=True):
            c.quotient = dec.Decimal(c.party.n_votes) / n
            c.quotient = int(c.quotient.to_integral_value(rounding=dec.ROUND_HALF_UP))
            n += 1
# ----------------------------------------------------------------------
# TODO  seat limit
# TODO  resolve equal quotients
def print_results(parties):
    all_candidates = []
    for party in parties:
        all_candidates += party.candidates
    print('Candidate Quotient (Votes)')
    for c in sorted(all_candidates, key=lambda cand: cand.quotient, reverse=True):
        print(f'{c} {c.quotient} ({c.n_votes})')
# ----------------------------------------------------------------------
def main():
    print('Creating parties...')
    p = create_parties()
    print(f'There are {len(p)} parties.')
    for party in p:
        print(party)
    print('Registering the candidates...')
    register_candidates(p)
    print('The list of the candidates:')
    print_candidates(p)
    print('Voting started')
    cast_votes(p)
    print('Calculating quotients...')
    determine_quotients(p)
    print('Results:')
    print_results(p)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    main()
