import csv
import numpy as np


def get_frequencies(filename):
    word_freq = dict()
    with open(filename, 'r') as f:
        reader = csv.reader(f, delimiter=',')
        next(reader)
        for row in reader:
            if len(row[0]) == 5:
                word_freq[row[0]] = int(row[1])
    return word_freq


def letter_frequencies(words):
    l_freq = [dict() for _ in range(5)]
    for word in words:
        for i in range(5):
            l_freq[i][word[i]] = l_freq[i].get(word[i], 0) + 1
    return l_freq


def get_score(word, l_freq, word_freq):
    score = 0
    # Calculate initial score via letter frequencies
    for i in range(5):
        score += l_freq[i].get(word[i], 0)

    # Adjust weighting by word frequency
    score *= np.log(word_freq[word])

    # Adjust weighting by unique letter count
    score *= len(set(word))

    return score


def get_best_words(words, l_freq, word_freq, k=1):
    scored_words = []
    for word in words:
        score = get_score(word, l_freq, word_freq)
        scored_words.append((word, score))
    scored_words.sort(key=lambda x: x[1], reverse=True)
    best_words = [scored_words[i][0] for i in range(min(k, len(scored_words)))]
    return best_words


def inp_valid(word):
    if word == "done":
        return True

    if len(word) != 5:
        return False
    return word.isalpha()


def res_valid(result):
    if result == "done":
        return True

    if len(result) != 5:
        return False

    for c in result:
        if c != '.' and c != 'x' and c != 'c':
            return False
    return True


def parse_rules(word, result, rules):
    if rules is None:
        correct = [None] * 5
        incorrect = [set() for _ in range(5)]
        exists = dict()
    else:
        correct, incorrect, exists = rules
    new_exists = dict()

    for i in range(5):
        r = result[i]
        c = word[i]
        if r == '.':
            for j in range(5):
                if correct[j] != c:
                    incorrect[j].add(c)
        elif r == 'c':
            correct[i] = c
        elif r == 'x':
            incorrect[i].add(c)
            new_exists[c] = new_exists.get(c, 0) + 1

    cor_freq = dict()
    for c in correct:
        if c is not None:
            cor_freq[c] = cor_freq.get(c, 0) + 1

    lets = set(cor_freq.keys()).union(set(exists.keys())).union(set(new_exists.keys()))
    for c in lets:
        counter = max(cor_freq.get(c, 0), exists.get(c, 0), new_exists.get(c, 0))
        if counter > 0:
            exists[c] = counter

    return correct, incorrect, exists


def filter_words(words, rules):
    def is_valid(word):
        c_count = dict()
        for i in range(5):
            c = word[i]
            c_count[c] = c_count.get(c, 0) + 1
            if correct[i] != None and correct[i] != c:
                return False
            if c in incorrect[i]:
                return False

        for c in exists:
            if c not in c_count or c_count[c] < exists[c]:
                return False
        return True

    correct, incorrect, exists = rules
    new_words = []
    for word in words:
        if is_valid(word):
            new_words.append(word)
    return new_words


if __name__ == "__main__":
    word_freq = get_frequencies("unigram_freq.csv")
    poss_words = word_freq.keys()
    rules = None

    done = False
    while not done:
        l_freq = letter_frequencies(poss_words)
        best_words = get_best_words(poss_words, l_freq, word_freq, k=3)
        print("Possible answers: {}".format(len(poss_words)))
        print("Suggested answers: {}".format(best_words))

        chosen = ""
        while not inp_valid(chosen):
            chosen = input("Enter used guess (leave blank if used suggested best) -> ")
            chosen = chosen.lower()
            if len(chosen) == 0:
                chosen = best_words[0]
            if chosen == "done":
                done = True

        if not done:
            result = ""
            while not res_valid(result):
                result = input("Enter result -> ")
                if result == "done":
                    done = True

        if not done:
            rules = parse_rules(chosen, result, rules)
            poss_words = filter_words(poss_words, rules)

        print()

    print("Goodbye!")
