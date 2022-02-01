# wordle

## Motivation
I have been playing [Wordle](https://powerlanguage.co.uk/wordle/) for the last few weeks now, and have been enjoying it quite a bit. I was inspired to find out what the best starting word would be.

## Ideas
The way it works is actually really simple. I take the list of all the words accepted by the program (accepted words) and all the words the program might choose as a wordle (wordles). Note that there are about 5x more accepted words than wordles.

I then go through every accepted word and give it a score, based on how much information it gives you.

```
Scoring Algorithm (against a single wordle):

Score(S: start word, W: wordle):
1. Compute the information S provides about W
2. Compute [W*] = set of all wordles that would have provided the same exact information as W
3. return {score = number of wordles - size of [W*]}

Score (S: start word, [W]: all wordles):
1. Let W be a wordle in [W]
2. Compute Score(S, W)
3. Repeat 1-2 for all W in [W]
4. Return the average score
```

## Best Scores
The best* starting words can be found in `scores_linear.txt` and `scores_invsqrt.txt`.

```
Top 5 linear scores:
reast 457.179
slate 455.365
trace 455.291
crate 453.671
salet 452.58
``` 
```
Top 5 inverse sqrt scores:
roate 2254.575
raise 2253.999
raile 2253.669
soare 2252.699
arise 2251.274
```
\* best by the metric discussed above, these scores do not account for subsequent guesses, which is quite significant

## Notes
* I actually scored words using two slightly different algorithms. One is exactly as I describe above, while the other actually measures the score as the proportion by which the number of possible wordles is reduced.
    * It actually takes the square root of this proportion so as not to weight high scores too heavily.
* Scoring a word against a single wordle runs in time O(n), since it needs to iterate through every other possible wordle. Scoring a word against all wordles (what we want to do) takes time O(n^2), hopefully that's clear enough. This takes about 2 seconds. \
Scoring every word against every wordle takes time O(n^3), or around 20,000 seconds. I could have left my laptop running over night, but I decided to make a basic heuristic to find good words more easily. \
Before taking the time to score a word, I would first check if (1) 4 of its letters are in the 7 most common letters and (2) it has all unique letters. Interestingly, we can sort of invert this heuristic to try to score the worst possible words.

    ```
    Bottom 5 linear scores:
    xylyl 1446.953
    susus 1440.54
    fuffy 1432.276
    jujus 1409.61
    immix 1330.736
    ```