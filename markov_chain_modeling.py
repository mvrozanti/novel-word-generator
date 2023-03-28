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
from plotter import plot

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

    def train(self, data):
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
            for word in tqdm(data):
                self.train(word)

    def maxsize(self):
        return max(wv.maxsize() for wv in self.connections.values())

    def next(self):
        generated = ''
        next_char = self.connections['\2'].get_random()
        while True:
            generated += next_char
            # code.interact(banner='', local=globals().update(locals()) or globals(), exitmsg='')
            next_char = self.connections[get_key(generated, len(generated)-1, self.order)].get_random()
            if next_char == '\0':
                break
        return generated

class Generator:
    
    def __init__(self, order):
        self.chain = MarkovChain(order)
        self.trainingData = {}

    def train(self, words):
        for w in words:
            self.trainingData[w] = False
        self.chain.train(trainingData)

    def next(self):
        return self.chain.next()

    def next_new(self):
        generated = ''
        while True:
            generated = self.next()
            if generated not in self.trainingData:
                break
        return generated

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='Markov Chain Model Generator')
    subparsers = parser.add_subparsers(dest='command')
    
    training_parser = subparsers.add_parser('train')
    training_parser.add_argument('-w', '--wordlist', type=str, help='word list to train on', required=True)
    training_parser.add_argument('-o', '--order', type=int, default=8, help='Markov chain order, defaults to 8')

    generation_parser = subparsers.add_parser('generate')
    generation_parser.add_argument('-n', '--number-of-words', type=int, help='generate N words, defaults to 1', default=1, metavar='N')
    generation_parser.add_argument('-m', '--model', help='model output in training step', required=True)
    generation_parser.add_argument('-p', '--plot', action='store_true', help='plot state-transition diagram')

    args = parser.parse_args()
    if args.command == 'train':
        trainingData = [w.strip() for w in open(args.wordlist).readlines()]
        g = Generator(args.order)
        g.train(trainingData)
        wordlist_filename = op.splitext(op.basename(args.wordlist))[0]
        pickle.dump(g, open(wordlist_filename + '.pkl', 'wb'))
    elif args.command == 'generate':
        g = pickle.load(open(args.model, 'rb'))
        if args.plot:
            while True:
                plot(g.chain)
        else:
            for i in range(args.number_of_words):
                print(g.next_new())
