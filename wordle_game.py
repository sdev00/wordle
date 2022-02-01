from collections import Counter
import numpy as np
import random
ALPHABET = 'abcdefghijklmnopqrstuvwxyz'
WORD_LEN = 5
MIN_FREQ = 5e-7

def load_words(path):
    words = []
    with open(path) as file:
        for line in file:
            word = line.split('\n')[0]
            words.append(word)
    return(words)

wordles = load_words('wordles_shuffled')
accepted_words = load_words('words')
accepted_words.extend(wordles)
accepted_words.sort()

RESTRICT = lambda word: word.islower() and word.isalpha() and len(word) == WORD_LEN \
    and word_frequency(word, 'en') >= MIN_FREQ

def removeProperNouns(words):
    result = words.copy()
    for word in words:
        if word[0].isupper():
            result.remove(word)
    return result

def restrictWordLength(words, length):
    result = words.copy()
    for word in words:
        if len(word) != length:
            result.remove(word)
    return result

def restrictSet(words, key):
    result = words.copy()
    for word in words:
        if not key(word):
            result.remove(word)
    return result

def getLetterFrequencies(words, weighted=True):
    freqs, overall = [{letter: 0 for letter in ALPHABET} for i in range(5)], {letter: 0 for letter in ALPHABET}
    for word in words:
        weight = WEIGHTS[word] if weighted else 1
        for index, letter in enumerate(word):
            freqs[index][letter] += weight
            overall[letter] += weight
            
    return freqs, overall

ORDINALS = ['1st', '2nd', '3rd', '4th', '5th', '6th']
def printMaxIndexFreqs(freqs, overall):
    letters = sorted(ALPHABET, reverse=True, key=lambda letter: overall[letter])
    print(f'Overall frequency order:\t{"|".join(letters)}')
    
    for index, dic in enumerate(freqs):
        letters = sorted(ALPHABET, reverse=True, key=lambda letter: dic[letter] if letter in dic else 0)
        print(f'Frequency order for {ORDINALS[index]} letter:\t{"|".join(letters)}')

def satisfies(word, exact, contains, absent):
    word = list(word)
    for index, letter in exact:
        if word[index] != letter:
            return False
        word[index] = '_'
        
    for index, letter in contains:
        if (word[index] == letter or letter not in word):
            return False
        word[word.index(letter)] = '_'
        
    for index, letter in absent:
        if letter in word:
            return False
        
    return True

def score(words, guess, word, print_possible=False):
    exact, contains, absent = [], [], []
    if guess not in accepted_words:
        if print_possible:
            print(f'Warning: "{guess}" not in word list')
        
    counts = Counter(word)
    for index, letter in enumerate(guess):
        if word[index] == letter:
            exact.append((index, letter))
            counts[letter] -= 1
        elif letter in word and counts[letter] > 0:
            contains.append((index, letter))
            counts[letter] -= 1
        else:
            absent.append((index, letter))
            
    possible = set()
    for word in words:
        if satisfies(word, exact, contains, absent):
            possible.add(word)
    
    score = len(words) - len(possible)
    if print_possible:
        print(f'Green letters: {exact}')
        print(f'Yellow letters: {contains}')
        print(f'Gray letters: {absent}')
        print(f'All possible words ({len(possible)}): {possible}')
        print(f'Score ({len(words)}-{len(possible)})): {score}')
        
    return score

def computeAverageScore(words, guess):
    sc = 0
    for word in words:
        sc += score(words, guess, word)
        
    return np.round(sc/len(words), 3)

def prof():
    computeAverageScore(wordles, 'rates')

def scoreGuesses(words, saved_scores, *args, list_all=False):
    best = 0
    for guess in args:
        if guess not in saved_scores:
            sc = computeAverageScore(words, guess)
            saved_scores[guess] = sc
        
        if saved_scores[guess] > best:
            best = saved_scores[guess]
            print(f'New best! Average score for {guess}: {saved_scores[guess]}')
        elif list_all:
            print(f'Average score for {guess}: {saved_scores[guess]}')

def save_scores(path, scores_list):
    words = []
    with open(path, 'w') as file:
        for word, score in scores_list:
            file.write(f'{word} {score}\n')

BASIC_RESTRICTION = lambda word: word.islower() and word.isalpha() and len(word) == WORD_LEN
RESULTS_RESTRICTION = lambda word: BASIC_RESTRICTION(word) and sum((1 if letter in 'eca' else 0) for letter in word) == 5
GUESS_RESTRICTION = lambda word: BASIC_RESTRICTION(word) and word in accepted_words

# e = exact, c = contains, a = absent
def solver(wordles, accepted_words):
    words = accepted_words.copy()
    
    for guess_count in range(6):
        guess = ''

        while not GUESS_RESTRICTION(guess):
            guess = input(f'{ORDINALS[guess_count]} guess: ')
            
            if len(words) == 1 and guess == next(iter(words)):
                print(f'Congratulations, you won in {guess_count + 1} turns!')
                return
            
        results = ''
        while not RESULTS_RESTRICTION(results):
            results = input('Result (ex. caace): ')
            
        exact, contains, absent = [], [], []

        for index, result in enumerate(results):
            letter = guess[index]
            if result == 'e':
                exact.append((index, letter))
            elif result == 'c':
                contains.append((index, letter))
            elif result == 'a':
                absent.append((index, letter))
                
        # print(f'Green letters: {exact}')
        # print(f'Yellow letters: {contains}')
        # print(f'Gray letters: {absent}')
        
        if len(exact) == 5 and guess in words:
            print(f'Congratulations, you won in {guess_count + 1} turns!')
            return
        elif len(exact) == 5:
            print(f'Invalid input, please restart.')
            return
        
        possible = set()
        for word in words:
            if satisfies(word, exact, contains, absent):
                possible.add(word)
                
        if len(possible) == 0:
            print(f'Invalid input, please restart.')
            return
        print(f'Possible words ({len(possible)}): {possible}\n')
        words = possible
        
    print('You lost :(')

GREEN_STYLE = '\033[92m'
YELLOW_STYLE = '\033[33m'
GRAY_STYLE = '\033[30m'

def wordle_start():
    print('Welcome to Wordle!')
    response = ''
    while response.lower() not in ['0', '1', '2']:
        response = input('What assistance level would you like? (0/1/2): ')
        
    return int(response)

def play_main(wordles, accepted_words, wordle=None, assistance=None):
    if assistance is None:
        assistance = wordle_start()
        
    if wordle is None:
        wordle = random.choice(wordles)
        
    words = accepted_words.copy()
    wordle_print = ['\033[30m_'] * 5
    overall_exact_indices, overall_contains, overall_absent = set(), {}, set()
    guesses = []
    
    for guess_count in range(6):
        guess = ''

        while not GUESS_RESTRICTION(guess):
            guess = input(f'{ORDINALS[guess_count]} guess: ')
            
            if guess == wordle:
                print(f'Congratulations, you won in {guess_count + 1} turns!')
                return
        
        counts = Counter(wordle)
        exact, contains, absent = [], [], []
        colors = []
        indices = list(range(5))
        
        contains_counts = {}
        absent_set = set()
        
        # green handling
        i = 0
        while i < len(indices):
            index = indices[i]
            letter = guess[index]
            if wordle[index] == letter:
                exact.append((index, letter))
                counts[letter] -= 1
                indices.pop(i)
                
                overall_exact_indices.add(index)
                contains_counts[letter.upper()] = contains_counts[letter.upper()] + 1 if \
                    letter.upper() in contains_counts else 1
                
                stylized_letter = GREEN_STYLE + letter.upper()
                colors.append((index, stylized_letter))
                wordle_print[index] = stylized_letter
            else:
                i += 1
        
        # yellow handling
        i = 0
        while i < len(indices):
            index = indices[i]
            letter = guess[index]
            if letter in wordle and counts[letter] > 0:
                contains.append((index, letter))
                counts[letter] -= 1
                indices.pop(i)
                
                contains_counts[letter.upper()] = contains_counts[letter.upper()] + 1 if \
                    letter.upper() in contains_counts else 1
                
                stylized_letter = YELLOW_STYLE + letter.upper()
                colors.append((index, stylized_letter))
            else:
                i += 1

        # gray handling
        for index in indices:
            letter = guess[index]
            absent.append((index, letter))
            absent_set.add(letter.upper())
            
            stylized_letter = GRAY_STYLE + letter.upper()
            colors.append((index, stylized_letter))
        
        # printing basic assistance
        if assistance > 0:
            overall_exact = {}
            for idx in overall_exact_indices:
                letter = wordle[idx]
                overall_exact[letter.upper()] = overall_exact[letter.upper()] + 1 if \
                    letter.upper() in overall_exact else 1
                
            absent_set -= contains_counts.keys()
            absent_set -= overall_exact.keys()
            
            overall_contains = {key:max(overall_contains[key] if key in overall_contains else -np.inf,
                contains_counts[key] if key in contains_counts else -np.inf) for key in
                   set(list(overall_contains.keys())).union(contains_counts.keys())}
            
            overall_contains_copy = overall_contains.copy()
            for letter in overall_exact:
                if letter in overall_contains_copy:
                    overall_contains_copy[letter] -= overall_exact[letter]
                    if overall_contains_copy[letter] == 0:
                        del overall_contains_copy[letter]
            
            overall_absent = overall_absent.union(absent_set)
        
        guesses.append(''.join(map(lambda x: x[1], sorted(colors, key=lambda x: x[0]))))
        
        print('\033[1m')
        if assistance > 0:
            remaining = (set(ALPHABET.upper()) - overall_absent) - overall_contains.keys()
            print(f'{"".join(wordle_print)}\t{YELLOW_STYLE}Required: {overall_contains_copy}\t{GRAY_STYLE}Remaining: {sorted(remaining) if len(remaining) > 0 else "{}"}')
        for g in guesses:
            print(g)
        print('\033[0m')
        
        if assistance > 1:
            possible = set()
            for word in words:
                if satisfies(word, exact, contains, absent):
                    possible.add(word)

            print(f'Possible words ({len(possible)}): {possible}\n')
            words = possible
        
    print(f'You lost :(\nWordle: {wordle}')
    
def play(wordles, accepted_words):
    assistance = wordle_start()
    playagain = True
    while playagain:
        play_main(wordles, accepted_words, assistance=assistance)
        
        response = ''
        while response.lower() not in ['y', 'n', 'yes', 'no']:
            response = input('Would you like to play again? (y/n): ')

        playagain = (response.lower()[0] == 'y')
        print()

play(wordles, accepted_words)