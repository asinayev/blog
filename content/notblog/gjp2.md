Title: Choosing Multiple Labels for Text, Part 2: Word2Vec.
Date: 2015-12-18 16:27
Modified: 2015-12-18 16:27
Category: Python
Tags: word2vec, machine learning, multilabel
Author: Aleksandr Sinayev
Summary: There is not always enough data to train a model using supervised learning. In these cases, using an unsupervised model may be beneficial. In this blog post I show how a pre-trained word2vec model can be used for labeling text.

In part 1, I used random forests trained on this dataset to label the questions. However, this approach failed to label many of the questions. For example, the random forests could not find a label for the question "Will the United Nations General Assembly recognize a Palestinian state by 30 September 2011?". Of the available labels, one potentially good label for this question is "Israel" since crude oil is a commonly traded commodity. However, the association between crude oil and commodities is absent in the training dataset. One possible solution to this is to use a pre-trained model that has learned many associations.

Luckily, Google has recently trained a Word2Vec [model](https://code.google.com/p/word2vec/) on a giant corpus of news articles. Word2Vec models are neural networks that use a corpus to create vector representations of words, such that words that co-occur frequently will have similar vectors and words that co-occur infrequently will have different vectors. These vectors have nice properties. For example, adding and subtracting them should give you sensible results (e.g., king - man + woman = queen). The vectors are intended to store the meaning of the words, with meaning operationalized as co-occurrence.

```
from gensim.models import Word2Vec

model = Word2Vec.load_word2vec_format( 'GoogleNews-vectors-negative300.bin.gz',binary=True)

def clean(sentence, model):
	"""Creates a list of terms that are represented in the model from a sentence"""
	regex = re.compile('[%s]' % re.escape(string.punctuation))
	tokens = str.split(sentence)
	cleans =[]
	for t in tokens:
		if t in model: 
			cleans.append(t)
		elif t.lower() in model: 
			cleans.append(t.lower())
		elif regex.sub('_', t) in model:
			cleans.append(regex.sub('_', t))
		elif len(str.split(regex.sub(' ', t))) > 1:
			for token in str.split(regex.sub(' ', t)):
				if clean(token): cleans.append(clean(token)[0])
	cleans = [w for w in cleans if w not in stopwords.words("english")]
	return cleans

def model_similarity (model, list1, list2, l1neg=[], l2neg=[]):
	"""finds the similarity according to a model of two lists of words
	also accepts 'negative' lists for analogies."""
    list1sum=sum([model[l] for l in list1])
    list2sum=sum([model[l] for l in list2])
    if l1neg: list1sum -= sum([model[l] for l in l1neg])
    if l2neg: list1sum -= sum([model[l] for l in l2neg])
    return 1-spatial.distance.cosine(list1sum,list2sum)

model_similarity(clean('king woman'),clean('queen'), l1neg=['man'])
0.71181934779762868
```

The similarity between king+woman-man and queen is quite high, so the model appears to be working. The idea is to use this tool to select, for a particular piece of text, one or more topics from a list by assessing the similarity between the text and the topic. First, we can add up the vectors for all the words in a question, then compare the resulting vector to each of the topic vectors. If the similarity is high enough, we can conclude that that label is appropriate.

```
import pandas
ifps = pandas.read_csv('ifps.csv')
def flatten (l): 
	""" flatten a list of lists """
	return [item for sublist in l for item in sublist]


def union(a, b):
    """ returns the union of two lists """
    return list(set(a) | set(b))

#Get a list of all the possible tags
tags = ifps['tags'].apply(str).apply(str.split, args=('|')).tolist()
tags = list(set(flatten(tags)))
tags = [clean(t) for t in tags if clean(t)]

sims1 = [[model_similarity(clean(q),t) for t in tags] for q in ifps['q_text']]
#a list of lists of similarities of each question to each label. Each outside list corresponds to a question. Each inside list corresponds to a label.
bigsims = [ [l.index(e) for e in l if e>.4] for l in sims1]
#a list of list of indices of appropriate labels
labels = [[tags[j] for j in i] for i in bigsims]
#a list of lists of appropriate labels

labels[3]
[['Israel']]
```

Now, we can see that the fourth article (in Python, 0 is first, so 3 is fourth) is labeled "Israel", which is an appropriate label. In fact, below you can see that about 65% of articles are labeled, almost double of what we had using random forests, so we can declare this a success.

```
len([l for l in labels if l])/float(len(labels))
0.6434359805510534
```

#Conclusion
In these two blog posts, I showed how text can be given labels. The first used a supervised machine learning approach, in which the model learned from examples how to label data. The second used an unsupervised machine learning approach, in which a model trained on an external, unlabeled source was used to label text. The first approach is likely better if sufficient data are available. However, in this case, the second approach provided labels where the first failed to do so due to a small training set, and as a result was superior.

