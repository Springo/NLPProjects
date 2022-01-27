import csv
import numpy as np


def get_frequencies(filename, word_len):
    word_freq = dict()
    with open(filename, 'r') as f:
        reader = csv.reader(f, delimiter=',')
        next(reader)
        for row in reader:
            if len(row[0]) == word_len:
                word_freq[row[0]] = int(row[1])
    return word_freq


def weighted_letter_frequencies(words, word_freq, word_len):
    l_freq = [dict() for _ in range(word_len)]
    l_freq_all = dict()
    for word in words:
        for i in range(word_len):
            l_freq[i][word[i]] = l_freq[i].get(word[i], 0) + word_freq[word]
            l_freq_all[word[i]] = l_freq_all.get(word[i], 0) + word_freq[word]
    return l_freq, l_freq_all


def get_score(word, l_freq, l_freq_all, word_freq, word_len):
    score = 0
    # Calculate initial score via letter frequencies
    for i in range(word_len):
        score += l_freq[i].get(word[i], 0)

    # Adjust weighting by unique letter count
    word_chars = set(word)
    for c in word_chars:
        score += l_freq_all.get(c, 0)

    # Adjust weighting by word frequency
    score *= np.log(word_freq[word])

    return score


def get_best_words(words, l_freq, l_freq_all, word_freq, word_len, k=1):
    scored_words = []
    for word in words:
        score = get_score(word, l_freq, l_freq_all, word_freq, word_len)
        scored_words.append((word, score))
    largest_score = max(scored_words, key=lambda x: x[1])[1]
    scored_words.sort(key=lambda x: x[1], reverse=True)
    best_words = [(w[0], w[1] / largest_score) for w in scored_words[:min(k, len(scored_words))]]
    return best_words


def inp_valid(word, word_len):
    if word == "done":
        return True

    if len(word) != word_len:
        return False
    return word.isalpha()


def res_valid(result, word_len):
    if result == "done":
        return True

    if len(result) != word_len:
        return False

    for c in result:
        if c != '.' and c != 'x' and c != 'c':
            return False
    return True


def parse_rules(word, result, rules, word_len):
    if rules is None:
        correct = [None] * word_len
        incorrect = [set() for _ in range(word_len)]
        exists = dict()
    else:
        correct, incorrect, exists = rules
    new_exists = dict()

    checked = set()
    for i in range(word_len):
        r = result[i]
        c = word[i]
        if r == '.':
            if c not in checked:
                for j in range(word_len):
                    if correct[j] != c:
                        incorrect[j].add(c)
            else:
                incorrect[i].add(c)
        elif r == 'c':
            correct[i] = c
            new_exists[c] = new_exists.get(c, 0) + 1
            if c in incorrect[i]:
                incorrect[i].remove(c)
        elif r == 'x':
            incorrect[i].add(c)
            new_exists[c] = new_exists.get(c, 0) + 1
            checked.add(c)

    lets = set(exists.keys()).union(set(new_exists.keys()))
    for c in lets:
        counter = max(exists.get(c, 0), new_exists.get(c, 0))
        if counter > 0:
            exists[c] = counter

    return correct, incorrect, exists


def filter_words(words, rules, word_len):
    def is_valid(word):
        c_count = dict()
        for i in range(word_len):
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
    word_len = 5
    suggestions = 5
    word_freq = get_frequencies("unigram_freq.csv", word_len)
    poss_words = word_freq.keys()
    rules = None

    done = False
    while not done:
        l_freq, l_freq_all = weighted_letter_frequencies(poss_words, word_freq, word_len)
        best_words = get_best_words(poss_words, l_freq, l_freq_all, word_freq, word_len, k=suggestions)
        print("Possible answers: {}".format(len(poss_words)))
        print("Suggested answers:")
        for i in range(len(best_words)):
            print("\t{}) {} (Score: {})".format(i + 1, best_words[i][0], best_words[i][1]))

        chosen = ""
        while not inp_valid(chosen, word_len):
            chosen = input("Enter used guess (leave blank if used suggested best) -> ")
            chosen = chosen.lower()
            if len(chosen) == 0:
                chosen = best_words[0][0]
            if chosen == "done":
                done = True

        if not done:
            result = ""
            while not res_valid(result, word_len):
                result = input("Enter result -> ")
                if result == "done":
                    done = True

        if not done:
            rules = parse_rules(chosen, result, rules, word_len)
            poss_words = filter_words(poss_words, rules, word_len)

        print()

    print("Goodbye!")
