#!/usr/bin/env python
from os import path as op
from tqdm import tqdm
import argparse
import bisect
import code
import os
import pickle
import random
import sys

def get_key(s, index, order):
    assert(order > 0)
    key = ''
    if index < order - 1:
        key = '\2'*(order - index - 1)
        start = 0
    else:
        start = index - order + 1
    key += s[start:index+1]
    return key

class WeightedVector:

    def __init__(self):
        self.elements = []
        self.cummulative_weights = []

    def add(self, element, weight):
        if element in self.elements:
            for i in range(self.elements.index(element), len(self.elements)):
                self.cummulative_weights[i] += weight
            return
        self.elements += [element]
        self.cummulative_weights += [weight + self.maxsize()]

    def maxsize(self):
        return 0. if not self.cummulative_weights else self.cummulative_weights[-1]

    def get_random(self):
        return self.get(random.randint(0,self.maxsize()-1))

    def get(self, value):
        assert(value < self.maxsize())
        assert(value >= 0.0)
        return self.elements[bisect.bisect(self.cummulative_weights, value)]

class MarkovChain:

    def __init__(self, order):
        self.order = order
        self.connections = {}

    def train(self, data, verbose=False):
        if type(data) == str:
            if '\2' not in self.connections:
                self.connections['\2'] = WeightedVector()
            self.connections['\2'].add(data[0], 1.)
            for i in range(len(data)-1):
                k = get_key(data, i, self.order)
                if k not in self.connections:
                    self.connections[k] = WeightedVector()
                self.connections[k].add(data[i+1], 1.)
            k = get_key(data, len(data)-1, self.order)
            if k not in self.connections:
                self.connections[k] = WeightedVector()
            self.connections[k].add('\0', 1.)
        elif type(data) == list:
            for word in (tqdm(data) if verbose else data):
                self.train(word)

    def next(self):
        generated = ''
        next_char = self.connections['\2'].get_random()
        while True:
            generated += next_char
            next_char = self.connections[get_key(generated, len(generated)-1, self.order)].get_random()
            if next_char == '\0':
                break
        return generated

class Generator:
    
    def __init__(self, order):
        self.chain = MarkovChain(order)
        self.trainingData = {}

    def train(self, words, verbose=False):
        for w in words:
            self.trainingData[w] = False
        self.chain.train(trainingData, verbose)

    def next(self):
        return self.chain.next()

    def nextNew(self):
        generated = ''
        while True:
            generated = self.next()
            if generated not in self.trainingData:
                break
        return generated

# plot graph weighted arrows
def plot(generator):
    code.interact(banner='', local=globals().update(locals()) or globals(), exitmsg='')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=sys.argv[0])
    parser.add_argument('-m', '--model', help='use MODEL file', required=True)
    parser.add_argument('-t', '--training-data', help='training data')
    # parser.add_argument('-i', '--interact', action='store_true', help='interact')
    parser.add_argument('-o', '--order', type=int, default=8, help='Markov-chain order, defaults to 8')
    parser.add_argument('-g', '--generate', type=int, help='generate N words', default=0)
    parser.add_argument('-p', '--plot', action='store_true', help='plot state-transition diagram')
    parser.add_argument('-v', '--verbose', action='store_true', help='show progress bar')
    args = parser.parse_args()
    if args.training_data:
        trainingData = [w.strip() for w in open(args.training_data).readlines()]
        g = Generator(args.order)
        g.train(trainingData, verbose=args.verbose)
        pickle.dump(g, open(args.model, 'wb'))
    else:
        g = pickle.load(open(args.model, 'rb'))
    if args.plot:
        plot(g)
    if args.generate:
        for i in range(args.generate):
            print(g.nextNew())
