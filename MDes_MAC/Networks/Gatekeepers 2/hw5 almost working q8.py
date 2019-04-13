from math import log
from copy import deepcopy
import numpy as np

class TextClassifier:
    """
    In this question, you will implement a classifier that predicts
    the number of stars a reviewer gave a movie from the text of the review.

    You will process the reviews in the dataset we provide, then
    implement a Naive Bayes classifier to do the prediction.

    But first, some math!
    """

    def q0(self):
        """
        Return your full name as it appears in the class roster as well as all collaborators as a list of strings
        """
        return ["Lara Tomholt"]
#        return ["Scott Kuindersma", "Brian Plancher"]

    def q1(self):
        """
        Suppose you roll a 4-sided die of unknown bias, and you observe
        the following sequence of values:
        3   1   4   4   2   1   2   4   2   1   2   1   1   1   1   4   3   4   4   1
        Given only this information, what are the most likely
        probabilities of rolling each side? (Hardcoding is fine)
        """
        values = [3,1,4,4,2,1,2,4,2,1,2,1,1,1,1,4,3,4,4,1]
        amount_1 = 0
        amount_2 = 0
        amount_3 = 0
        amount_4 = 0
        for value in values:
            if value == 1:
                amount_1 += 1
            elif value == 2:
                amount_2 += 1
            elif value == 3:
                amount_3 += 1
            else:
                amount_4 += 1
        totalRolls = len(values)
        return [float(amount_1) / totalRolls, float(amount_2) / totalRolls, float(amount_3) / totalRolls, float(amount_4) / totalRolls]

    def q2(self):
        """
        You just fit a multinomial distribution!

        Now suppose you have a prior belief that the die is fair.
        After some omitted math involving a conjugate Dirichlet distribution,
        you realize that you can encode this prior by simply adding
        some "fake" observations of each side. The number of observations
        is the "strength" of your prior belief.
        Using the same observations as in q1 and a prior with a per-side
        "strength" of 2, what are the probabilities of rolling each side??
        """
        values = [3,1,4,4,2,1,2,4,2,1,2,1,1,1,1,4,3,4,4,1]
        
        strength = 2
        diceNrSides = 4
        for i in range(strength):
            for j in range(diceNrSides):
                values.append(j)
                
        amount_1 = 0
        amount_2 = 0
        amount_3 = 0
        amount_4 = 0
        for value in values:
            if value == 1:
                amount_1 += 1
            elif value == 2:
                amount_2 += 1
            elif value == 3:
                amount_3 += 1
            else:
                amount_4 += 1
        totalRolls = len(values)
        return [float(amount_1) / totalRolls, float(amount_2) / totalRolls, float(amount_3) / totalRolls, float(amount_4) / totalRolls]

    def q3(self, counts=[1,1,3,8]):
        """
        You might be wondering what dice have to do with NLP.
        We will model each possible rating (one of the five numbers of stars)
        as a die, with each word in the dictionary as a face.

        This is a multinomial Naive Bayes classifier, because the words are
        drawn from a per-rating multinomial distribution and we treat
        each word in a review as independent (conditioned on the rating). That is,
        once the rating has emitted one word to the review, the next word
        has the same distribution over possible values as the first.

        In this question, you will write a function that computes p(word|rating), the
        probability that the rating under question will produce
        each of the four words in our dictionary. We will run this function
        5 times, once for each rating. We pass in the number of times each
        word shows up in any review corresponding to the current rating.
        """

        total = sum(counts)
        listProb = []
        for i in range(len(counts)):
            prob = float(counts[i]) / total
            listProb.append(prob)
            
        return listProb

    def q4(self, infile):
        """
        You'll notice that actual words didn't appear in the last question.
        Array indices are nicer to work with than words, so we typically
        write a dictionary encoding the words as numbers. This turns
        review strings into lists of integers. You will count the occurrences
        of each integer in reviews of each class.

        The infile has one review per line, starting with the rating and then a space.
        Note that the "words" include things like punctuation and numbers. Don't worry
        about this distinction for now; any string that occurs between spaces is a word.

        You must do three things in this question: build the dictionary,
        count the occurrences of each word in each rating and count the number
        of reviews with each rating.
        The words should be numbered sequentially in the order they first appear.
        counts[ranking][word] is the number of times word appears in any of the
        reviews corresponding to ranking
        nrated[ranking] is the total number of reviews with each ranking
        """
        
        f = open(infile)
        text = f.read()
        lines = text.split('\n')
        del lines[-1] #remove last empty line from list
        dictWords = {}
        index = 0
        nrated = [0,0,0,0,0]
        
        for line in lines:
            usedWords = line.split() #splits line into words based on white spaces, returns list.
            rating = int(usedWords[0])
            nrated[rating] += 1
            
            
            for i in range(1,len(usedWords)):
                if usedWords[i] not in dictWords.keys():
                    dictWords[usedWords[i]] = index
                    index += 1
        
        #create empty counts list
        countsPerRating = []
        for j in range(len(dictWords)):
            countsPerRating.append(0)
            
        counts = []
        for i in range(5):
            counts.append(countsPerRating)
        counts = np.array(counts)
        for line in lines:
            usedWords = line.split()
            rating = int(usedWords[0])
            for i in range(1,len(usedWords)):
                wordIndex = dictWords.get(usedWords[i])
                counts[rating][wordIndex] += 1
        
        self.dict = dictWords            #{"compsci": 0, "182": 1, ".": 2}
        self.counts = counts.tolist()              #[[0,0,0],[0,0,0],[1,1,1],[0,0,0],[0,0,0]]
        self.nrated = nrated                  #[0,0,1,0,0]
        

    def q5(self, alpha=1):
        """
        Now you'll fit the model. For historical reasons, we'll call it F.
        F[rating][word] is -log(p(word|rating)).
        The ratings run from 0-4 to match array indexing.
        Alpha is the per-word "strength" of the prior (as in q2).
        (What might "fairness" mean here?)
        """

        countsWithStrength = deepcopy(self.counts)
        for i in range(len(countsWithStrength)):         
            for j in range(len(countsWithStrength[i])):
                countsWithStrength[i][j] += alpha
                
        F = []        
        
        # p(word|rating)
        for lst in countsWithStrength:
            f = []
            totalNrWords = sum(lst)
            for count in lst:
                if count == 0:
                    probLog = float(0.0000000000000001)
                else:
                    prob = float(count)/totalNrWords
                    probLog = -log(prob)
                f.append(probLog)
            F.append(f)
        
        self.F = F           #[[0,0,0], [0,0,0], [1,8,2], [0,0,0], [0,0,0]]


    def q6(self, infile):
        """
        Test time! The infile has the same format as it did before. For each review,
        predict the rating. Ignore words that don't appear in your dictionary.
        Are there any factors that won't affect your prediction?
        You'll report both the list of predicted ratings in order and the accuracy.
        """

        #P(rating | word) proportional to P(rating) x P (word | rating)

        
        f = open(infile)
        text = f.read()
        lines = text.split('\n')
        del lines[-1] #remove last empty line from list
     
        ratingList = []
        accuracy = 1
        for line in lines:
            prob = [0,0,0,0,0] #P P (word | rating)
            usedWords = line.split() #splits line into words based on white spaces, returns list.         
            for i in range(1,len(usedWords)):
                word = usedWords[i]
                if word in self.dict.keys():
                    wordIndex = self.dict.get(word)
                    for i in range(5):
                        prob[i] = prob[i] + self.F[i][wordIndex] #because we're using log we can add instead of multiply
            ratingHighestProb = prob.index(min(prob)) #use min instead of max because we're using -log
            ratingList.append(ratingHighestProb)

        nrAccurate = 0
        for i in range(len(lines)):
            line = lines[i]
            usedWords = line.split() 
            if ratingList[i] == int(usedWords[0]):
                nrAccurate += 1
        accuracy = float(nrAccurate) / len(ratingList)
            
        return (ratingList, accuracy)


    def q7(self, infile):
        """
        Alpha (q5) is a hyperparameter of this model - a tunable option that affects
        the values that appear in F. Let's tune it!
        We've split the dataset into 3 parts: the training set you use to fit the model
        the validation and test sets you use to evaluate the model. The training set
        is used to optimize the regular parameters, and the validation set is used to
        optimize the hyperparameters. (Why don't you want to set the hyperparameters
        using the test set accuracy?)
        Find and return a good value of alpha (hint: you will want to call q5 and q6).
        What happens when alpha = 0?
        """
        
        # Piazza note:
        # q7: Scott suggests testing values that are close to 0. 
        # I've also gotten solutions by testing a wider range of integers. 
        # Also a quirk in the autograder wanted you to update the alpha on 
        # a tie so make sure you do that (That was my mistake for a while)!       
        
        # Piazza note:
        # You shouldn't have to test alpha=0, but make sure you might want to try values close to 0 in your sweep. 
        
#        predictedRating = self.q6(infile)
        
        accuracy = 0.0
        alpha = 0.0
        for i in np.arange(0, 4, 0.001):  # also test floats, in particular values close to zero
            self.q5(i)
            predictedRating = self.q6(infile)
            a = predictedRating[1]
            if a > accuracy:
                accuracy = a
                alpha = i  
        
        return alpha

    def q8(self):
        """
        We can also "hallucinate" reviews for each rating. They won't make sense
        without a language model (for which you'll have to take CS287), but we can
        list the 3 most representative words for each class. Representative here
        means that the marginal information it provides (the minimal difference between
        F[rating][word] and F[rating'][word] across all rating' != rating) is maximal.
        You'll return the strings rather than the indices, and in decreasing order of
        representativeness.
        """
        
        
        # Piazza note:
        # q8: The order of self.F[rating][word] - self.F[rating'][word] matters. 
        # Try both and then convince yourself why one works and the other doesn't 
        # (also why abs doesn't work). This should also fix the tiebreaking issue 
        # (again that was my mistake last night). I have checked the answers and 
        # I don't think there are any more tiebreaking issues for stsa for q8. 
                
        reps = []
        wordprobtotal = list(range(len(self.F[0])))
        probdict = {}

        for j in range(len(self.F[0])):
            probdict[j] = []

        # probdict[wordindex] = [ prob0, prob1, prob2, prob3, prob4 ]
        for i in range(len(self.F)):
            for j in range(len(self.F[i])):
                wordprobtotal[j] += self.F[i][j]
                # if not probdict[j]:
                #     probdict[j] = [self.F[i][j]]
                # else:
                #     probdict[j].append(self.F[i][j])
                probdict[j].append(self.F[i][j])

        wordprobavg = [x/len(self.F) for x in wordprobtotal]

        for i in range(len(self.F)):
            repsByRating = []
            topwords = []
            for j in range(len(self.F[i])):
                wordprob = self.F[i][j]
                otherprob = float('Inf')
                for k, v in probdict.iteritems():
                    if k == j:
                        for l in range(len(probdict[j])):
                            if l != i:
                                if wordprob - probdict[j][l] < otherprob:
                                    otherprob = wordprob - probdict[j][l]
                
                wordrep = otherprob
                repsByRating.append(wordrep)

            orderedindices = sorted(range(len(repsByRating)), key=lambda k: repsByRating[k])

            ordered = ['','','']
            for k, v in self.dict.iteritems():
                if v == orderedindices[0]:
                    ordered[0] = k
                if v == orderedindices[1]:
                    ordered[1] = k
                if v == orderedindices[2]:
                    ordered[2] = k

            reps.append( [ ordered[0], ordered[1], ordered[2] ] )

        print reps
        return reps
        
        
        
        #return [["182", "compsci", "."] for _ in range(5)]

    """
    You did it! If you're curious, the dataset came from (Socher 2013), which describes
    a much more sophisticated model for this task.
    Socher, R., Perelygin, A., Wu, J. Y., Chuang, J., Manning, C. D., Ng, A. Y., and Potts, C. (2013). Recursive deep models for semantic compositionality over a sentiment treebank. In Proceedings of the conference on empirical methods in natural language processing (EMNLP), volume 1631, page 1642. Citeseer.
    """

if __name__ == '__main__':
    c = TextClassifier()
    print "Processing training set..."
    c.q4('mini.train')
    print len(c.dict), "words in dictionary"
    print "Fitting model..."
    c.q5()
    print "Accuracy on validation set:", c.q6('mini.valid')[1] #should be between 0 and 1, will probably be about 1/3
    print "Good alpha:", c.q7('mini.valid')
    c.q5() #reset alpha
    print "Happy words:", " and ".join(c.q8()[4][:2]) #The happy words will probably be "rocks" and "!"
