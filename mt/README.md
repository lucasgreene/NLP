This is a French-English Machine translation program. It uses IBM model 1 and EM to find transition probabilities between french and english words. The script verydumb runs the IBM 1 model with simple word to word decoding, and noisychannel runs IBM 1 with a bigram language model probability factored in for decoding. The simple model verydumb actually performs better (60%) F-score, due to the underlying assumptions in model 1. Bigram tranistion language probabilities don't make sense when you are translating a french sentence into english word by word - the order is not conducive to proper english.

To run:
  verydumb french-senate-0.txt english-senate-0.txt french-senate-2.txt
  

  fscore translated_french_1.txt english-senate-2.txt

  (takes around 10 minutes)

          OR

  noisychannel french-senate-0.txt english-senate-0.txt french-senate-2.txt
 

  fscore translated_french_2.txt english-senate-2.txt

  (takes around 45 minutes)

  NOTE: you can speed up the run time of both by about 10 minutes by using the serialized tau.p and words.p objects, that line of code is commented out.