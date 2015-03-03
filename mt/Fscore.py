import sys


def F_score(translatedEnglish, realEnglish):
    with open(realEnglish, 'rb') as f:
        realLines = [line.split() for line in f.readlines()]
    with open(translatedEnglish, 'rb') as f:
        lines1 = [line.split() for line in f.readlines()]
   
    correct1 = 0
    for i in xrange(len(realLines)):
        for word in realLines[i]:
            if word in lines1[i]:
                correct1 += 1
    realLength = sum([len(sent) for sent in realLines])
    length1 = sum([len(sent) for sent in lines1])
    p1 = correct1/float(length1)
    r1 = correct1/float(realLength)
    f1 = 2*((p1 * r1)/(p1 + r1))
    print "F score: " + str(f1)


if __name__ == '__main__':
    F_score(sys.argv[1], sys.argv[2])