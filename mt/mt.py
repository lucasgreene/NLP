import sys
from time import time
import cPickle as pickle

def EM(file1, file2):
    tic = time()
    print "Expectation maximization, 10 iterations"
    with open(file1) as f:
        lines1 = [line.split() for line in f.readlines()]

    with open(file2) as f:
        lines2 = [line.split() for line in f.readlines()]

    initial = 1.0
    tau = {}
    getTau = tau.get
    tol = .01
    step = 0
    maximums = {}
    getMax = maximums.get
    initMax = (0, 'null')
    wordsAssociated = {}
    getWords = wordsAssociated.get
    while step < 10:
        counts = {}
        getCounts = counts.get
        wordTotals = {}
        getTotals = wordTotals.get
        for i in xrange(len(lines1)):
            for word1 in lines1[i]:
                pk = sum([getTau((word, word1),initial) for word in lines2[i]])

                for word2 in lines2[i]:
                    temp = getWords(word1, set())
                    temp.update([word2])
                    wordsAssociated[word1] = temp
                    partial = getTau((word2,word1),initial)/pk
                    counts[(word2,word1)] = getCounts((word2,word1),0) + partial
                    wordTotals[word2] = getTotals(word2,0) + partial 
        for (w2,w1), value in counts.iteritems():
            newProb = value/getTotals(w2)
            tau[(w2,w1)] = newProb
            maximums[w2] = max(getMax(w2, initMax), (newProb, w1))
        step += 1
        print "Iteration = %s" %step
    prune(tau, wordsAssociated)
    print "EM took: %s seconds" % (time()-tic)
    return tau, maximums, wordsAssociated

def prune(tauDict, wordsDict):
    for k,v in tauDict.items():
        if v < 0.001:
            del tauDict[k]
            wordsDict[k[1]].remove(k[0])



def decodeDumb(frenchFile, maximums):
    getMax = maximums.get
    with open(frenchFile) as f:
        lines = [line.split() for line in f.readlines()]
    with open('translated_french_1.txt', 'wb') as f:
        for sent in lines:
            for word in sent:
                (prob, translated,) = getMax(word, (0,word))
                f.write(translated + " ")
            f.write("\n")

def smooth(word1,word2, uni_freq):
    alpha = 1.6
    beta = 100
    n_words = 455126
    n_types = 16809
    nb = 0.0
    if word2 in uni_freq:
        na = uni_freq[word2]
    else:
        na = 0.0
    if word1 in uni_freq:
        no = uni_freq[word1]
    else:
        no = 0.0
    theta = (na + alpha)/(n_words + alpha*n_types)
    return (nb + beta*theta)/(no + beta)


def decodeBetter(frenchFile, tau, words):
    # tau[] = (english,french)
    tic = time()
    bigramFreq = pickle.load(open('pickled_bigrams.p', 'rb'))
    uni_freq = pickle.load(open('unigrams.p','rb'))
    getTheta = bigramFreq.get
    getWords = words.get

    with open(frenchFile) as f:
        lines = [line.split() for line in f.readlines()]
      
    print "translating sentences..."
    with open('translated_french_2.txt','wb') as f:
        sentences_processed = 0
        for sent in lines:
            out = ['&&&']
            for word in sent:
                index = 0
                lastMax = (0., 'null')
                # Skips the french word if it hasn't been seen before 
                for en in getWords(word, []):   # look up the set of english words that
                    val = tau[(en,word)] # have prove >0.01 of transitioning
                    prob = val * getTheta((out[index],en), 0.01)                 
                    lastMax = max((prob, en), lastMax)
                if lastMax != (0, 'null'):
                    out.append(lastMax[1])
                else:
                    out.append(word) #Use French word if havent seen before
            out.append('\n')
            f.write(' '.join(out))
            sentences_processed += 1
            if sentences_processed % 100 == 0:
                print "%s lines processed in %s minutes" %(sentences_processed, 
                                                            (time()-tic)/60)
                

def dumbScript():
    tic = time()
    source_lang = sys.argv[1]
    translation_lang = sys.argv[2]
    to_translate = sys.argv[3]
    tau, maximums = EM(translation_lang, source_lang)
    decodeDumb(to_translate, maximums)
    print (time() - tic)/60

def betterScript():
    tic = time()
    source_lang = sys.argv[1]
    translation_lang = sys.argv[2]
    to_translate = sys.argv[3]
    tau, maximums, words = EM(source_lang, translation_lang)
    #print "Loading pickled transition probabilities and associated words..."
    #tau = pickle.load(open('tau.p','rb'))
    #words = pickle.load(open('words.p','rb'))
    decodeBetter(to_translate, tau, words)
    print "Finished in %s minutes" % str((time() - tic)/60)
  

def main():
    if sys.argv[4] == 'dumb':
        dumbScript()
    else:
        betterScript()



if __name__ == '__main__':
    main()