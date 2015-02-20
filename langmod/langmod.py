import sys
import numpy as np



def get_bigrams(filename):
    with open(filename) as File:
        lines = File.read().split('\n')
    lines = [line + ' &&&' for line in lines]
    lines[0] = '&&& ' + lines[0]
    toks = ' '.join(lines).split()
    bigrams = []
    for i in range(len(toks)-1):
        bigrams.append((toks[i],toks[i+1]))
    return toks, bigrams

def bigram_counts(bigrams):
    freq = {}
    for gram in bigrams:
        if gram in freq:
            freq[gram] += 1.
        else:
            freq[gram] = 1.
    return freq

def get_unigrams(filename):
    with open(filename) as File:
        toks = File.read().split()
    return toks

def unigram_counts(toks):
    freq = {}
    for word in toks:
        if word in freq:
            freq[word] += 1.
        else:
            freq[word] = 1.
    return freq

def bi_prob(bigrams, bi_freq, beta, uni_freq, n_words, alpha):
    n_types = len(uni_freq)
    prob = 0.0
    for gram in bigrams:
        if gram in bi_freq:
            nb = bi_freq[gram]
        else:
            nb = 0.0
        if gram[1] in uni_freq:
            na = uni_freq[gram[1]]
        else:
            na = 0.0
        if gram[0] in uni_freq:
            no = uni_freq[gram[0]]
        else:
            no = 0.0
        theta = (na + alpha)/(n_words + alpha*n_types)
        prob += np.log((nb + beta*theta)/(no + beta))
    return prob * -1


def uni_prob(toks, freq, alpha, n_words):
    n_types = len(freq)
    prob = 0.0
    for gram in toks:
        if gram in freq:
            prob += np.log((freq[gram] + alpha)/(n_words + alpha*n_types))
        else:
            prob += np.log((0. + alpha)/(n_words + alpha*n_types))
    return prob*-1

def beta_opt(ho_toks, bi_freq, uni_freq, n_words, alpha):
    tol = 0.001
    phi = 2/(1+np.sqrt(5))
    a = 0.01
    d = 200
    fa = bi_prob(ho_toks, bi_freq, a, uni_freq, n_words, alpha)
    fd = bi_prob(ho_toks, bi_freq, d, uni_freq, n_words, alpha)
    b = a + (1-phi)*(d-a)
    c = a + phi*(d-a)
    fb = bi_prob(ho_toks, bi_freq, b, uni_freq, n_words, alpha)
    fc = bi_prob(ho_toks, bi_freq, c, uni_freq, n_words, alpha)
    while abs(d-a) > tol:
        if fb <= fc:
            d = c
            fd = fc
            c = b
            fc = fb
            b = a + (1-phi)*(d-a)
            fb = bi_prob(ho_toks, bi_freq, b, uni_freq, n_words, alpha)
        else:
            a = b 
            fa = fb
            b =  c
            fb = fc
            c = a + phi*(d-a)
            fc = bi_prob(ho_toks, bi_freq, c, uni_freq, n_words, alpha)
    return a


def alpha_opt(ho_toks, freq, n_words):
    tol = 0.001
    phi = 2/(1+np.sqrt(5))
    a = 0.01
    d = 100
    fa = uni_prob(ho_toks, freq, a, n_words)
    fd = uni_prob(ho_toks, freq, d, n_words)
    b = a + (1-phi)*(d-a)
    c = a + phi*(d-a)
    fb = uni_prob(ho_toks, freq, b, n_words)
    fc = uni_prob(ho_toks, freq, c, n_words)
    while abs(d-a) > tol:
        if fb <= fc:
            d = c
            fd = fc
            c = b
            fc = fb
            b = a + (1-phi)*(d-a)
            fb = uni_prob(ho_toks, freq, b, n_words)
        else:
            a = b 
            fa = fb
            b =  c
            fb = fc
            c = a + phi*(d-a)
            fc = uni_prob(ho_toks, freq, c, n_words)
    return a

def guess_sents_uni(filename, freq, alpha, n_words):
    with open(filename) as File:
        lines = File.read().split('\n')
        del lines[-1]
        good = lines[::2]
        bad = lines[1::2]
    count = 0.
    for i in range(len(good)):
        p_good = uni_prob(good[i].split(), freq, alpha, n_words)
        p_bad = uni_prob(bad[i].split(), freq, alpha, n_words)
        if p_good < p_bad:
            count += 1
    return count/len(good)

def guess_sents_bi(filename, bi_freq, beta, uni_freq, alpha, n_words):
    with open(filename) as File:
        lines = File.read().split('\n')
        del lines[-1]
        good = lines[::2]
        bad = lines[1::2]
    good = ["&&& " + line + " &&&" for line in good]
    bad = ["&&& " + line + " &&&" for line in bad]
    
    count = 0.
    for i in range(len(good)):
        g_bigram = []
        b_bigram = []
        tempG = good[i].split()
        tempB = bad[i].split()
        for j in range(len(tempG)-1):
            g_bigram.append((tempG[j], tempG[j+1]))
        for j in range(len(tempB)-1):
            b_bigram.append((tempB[j], tempB[j+1]))
        p_good = bi_prob(g_bigram, bi_freq, beta, uni_freq, n_words, alpha)
        p_bad = bi_prob(b_bigram, bi_freq, beta, uni_freq, n_words, alpha)
        if p_good < p_bad:
            count += 1
    return count/len(good)

def uni_script():
    # filenames
    training = sys.argv[1]
    held_out = sys.argv[2]
    test = sys.argv[3]
    good_bad = sys.argv[4]
    # get training tokens and counts
    train_toks = get_unigrams(training)
    freq = unigram_counts(train_toks)
    # get test tokens
    test_toks = get_unigrams(test)
    # compute probability of test corpus
    prob = uni_prob(test_toks, freq, 1, len(train_toks))
    print "Log probaility of testdata with alpha = 1: " + str(prob)
    # get held out tokens
    ho_toks = get_unigrams(held_out)
    # optimize alpha   
    alpha = alpha_opt(ho_toks, freq, len(train_toks))
    opt_prob = uni_prob(test_toks, freq, alpha, len(train_toks))
    print "Log probability with optimized alpha: " + str(opt_prob)
    accuracy = guess_sents_uni(good_bad, freq, alpha, len(train_toks))
    print "Accuracy using unigram model: " + str(accuracy)
    print "Optimized alpha~ " + str(alpha)

def bi_script():
    # filenames
    training = sys.argv[1]
    held_out = sys.argv[2]
    test = sys.argv[3]
    good_bad = sys.argv[4]
    # get training bigrams and unigrams
    train_toks, train_bigrams = get_bigrams(training)
    # get bigram counts
    bi_freq = bigram_counts(train_bigrams)
    # get unigram counts
    uni_freq = unigram_counts(train_toks)
    # get test bigrams
    _, test_bigrams = get_bigrams(test)
    prob = bi_prob(test_bigrams, bi_freq, 1, uni_freq, len(train_toks), 1.599)
    print "Log probability with alpha = 1: " + str(prob)
    _, ho_bigrams = get_bigrams(held_out)
    beta = beta_opt(ho_bigrams, bi_freq, uni_freq, len(train_toks), 1.599)
    opt_prob = bi_prob(test_bigrams, bi_freq, 113.07, uni_freq, len(train_toks), 1.599)
    print "Log probability with optimized beta and alpha: " + str(opt_prob)
    accuracy =  guess_sents_bi(good_bad, bi_freq, beta, uni_freq, 1.599, len(train_toks))
    print "Accuracy using bigram model: " + str(accuracy)
    print "Optimized alpha~ 1.599"
    print "Optimized beta~ " + str(beta)

def main():
    
    if sys.argv[5] == 'uni':
        uni_script()
    else:
        bi_script()

if __name__ == '__main__':
    main()






