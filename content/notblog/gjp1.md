Title: Choosing Multiple Labels for Text, Part 1: Random Forests
Date: 2015-12-18 16:27
Modified: 2015-12-18 16:27
Category: R
Tags: random forests, machine learning, multilabel
Author: Aleksandr Sinayev
Summary: Here, I examine a machine learning approach to labeling text with one of many labels.

There are many ways to label text. In this post, I'm going to talk about applying one or more labels from a previously defined list to a piece of text using random forests in `R`.

# The Set Up

[The Good Judgment Project](https://www.gjopen.com/) attempts to take advantage of [crowd wisdom](https://en.wikipedia.org/wiki/Wisdom_of_the_crowd) to make geopolitical predictions. In it, people are asked to make predictions regarding various events. Previous research suggests retaining people who were most successful in earlier rounds for later rounds in order to hone in on a small but accurate group.

However, people's expertise likely varies by domain. For example, just because I am good at predicting the next president of Nicaragua does not necessarily mean I know anything about whether Google's stock will surge or plummet. 

#The Problem

In order to take advantage of this heterogeneity, we need accurate labels for the topics of the events. People were asked questions about over 500 different events. Only about half of these were labeled. Here, I'll try to automatically label the other events.

#A Proposed Solution

The approach I discuss here is to use a machine learning algorithm to learn what characteristics of the labeled questions give them the topics that they have and extrapolate that to the unlableled questions. I will do this in `R` using the `tm` and `randomForest` packages. There will be a separate model for each label.

```
> require(plyr)
> require(tm)
```

The first thing to do is to read in the file to see what we're dealing with. This file is made publically available by the Good Judgment Project.

```
> ifps = read.csv('ifps.csv', header=T, stringsAsFactors = F)
> head(ifps$q_text)
[1] "Will the Six-Party talks (among the US, North Korea, South Korea, Russia, China, and Japan) formally resume in 2011?"
[2] "Who will be inaugurated as President of Russia in 2012?"
[3] "Will Serbia be officially granted EU candidacy by 31 December 2011?"
[4] "Will the United Nations General Assembly recognize a Palestinian state by 30 September 2011?"
[5] "Will Daniel Ortega win another term as President of Nicaragua during the late 2011 elections?"
[6] "Will Italy restructure or default on its debt by 31 December 2011?"
> head(ifps$tags[ifps$tags!='']) #view the first six tags
[1] "|Middle-East|Law|"
[2] "|Middle-East|Conflict-Interstate|Diplomacy|Iran|"
[3] "|Asia-East|Pacific_Rim|Korea|Diplomacy|Military|"
[4] "|Asia-East|Europe|China|Economics|Law|"
[5] "|Asia-East|Pacific_Rim|Japan|Elections|"
[6] "|Middle-East|"
```

It seems that a question can be given more than one topic (or tag) and the tags are separated by the `|` character in the tags. 

We would like to be able to predict which topic(s) in `ifps$tags` are appropriate to a question based on the text in `ifps$q_text`. For that, we need one matrix that tells us which articles have which topics (that's what we want to predict) and a second matrix that tells us which words are in which article.

To get there, let's get a list of all the possible topics. These will be the names of the columns of the first matrix. First, we split them by the `|`character, and collect the output in one list and store the distinct elements of this list under topics.

```
> topics = unique(unlist(strsplit(ifps$tags, split='\\|')))
> topics = topics[c(-1,-length(topics))] #the first and last topics were "" and "0"
> length(topics) #how many topics are there?
[1] 59
```

We want a matrix with one row for each question and one column for each of the distinct topics, and for the entries, we want an indicator letting us know whether that question was labeled with that topic. The `ldply` function from the `plyr` package does just that. It applies a function to a list (in our case the list of topic vectors).
```
> require(plyr)
> topicMat = ldply( strsplit(ifps$tags, split='\\|'), 
+                   function(x) topics %in% x)
> names(topicMat) = topics #Give the columns the appropriate names
> topicMat = topicMat[colSums(topicMat)>10] #Get rid of any topics used less than 10 times.
```
Well, our topics are now in the right shape, but we still need a matrix with one row for each question and one column for each possible word, indicating whether that question has that word in it. `R`'s text mining package, `tm`, is perfect for this.
```
> mycorp = Corpus(VectorSource(q_text)) #turn the questions into a corpus
> mycorp = tm_map(mycorp, PlainTextDocument) #convenience function
> mycorp = tm_map(mycorp, content_transformer(tolower)) change everything to lowercase
> mycorp = tm_map(mycorp, removePunctuation) #remove punctuation
> dtm = DocumentTermMatrix(mycorp) #make a document-term matrix
> dtm = removeSparseTerms(dtm, .99) #remove terms that apeear in fewer than 1% of questions
> dtm2 = as.matrix(dtm) #change this into a regular matrix
> class(dtm2) = "numeric" #change the values to numeric, as required by regression
```
Now we're ready to train our algorithm. I find that random forests work really well for text data, so that is what I will use.

```
> train = !ifps$tags=='' #train on the rows that are labeled
> rfs = apply( topicMat[train,], 2, #for each column of the topic matrix
			   function(x) randomForest(dtm2[train,], factor(x), ntree=200)
			   #train a random forest with 200 trees
			   )
> chosennames = apply( dtm2[!train,], 1, function(row) { #for each row in the test set
	names(topicMat)[ #choose the topic labels so that 
		unlist(lapply( rfs, function(rf) predict(rf, row, 'prob')[2]>.4)) #its probability according to our model is greater than .4
		] 
})
```

# The Results
The results are stored in the `chosennames` vector. For example, let's look at question 1:

```
> ifps$q_text[1]
[1] "Will the Six-Party talks (among the US, North Korea, South Korea, Russia, China, and Japan) formally resume in 2011?"
> chosennames[1]
$`1`
[1] "Diplomacy"
```

I think this is a good label, and in general, I found all the labels the algorithm assigned were appropriate, though even in the training set they did not always agree wiht the labels originally provided. However, problematically, the labels were only available for about a quarter of the test cases. 
```
> mean(unlist(lapply(chosennames[!train], function(x)length(x)==0))) #proportion of test articles that weren't labeled
[1] 0.7282051
> ifps$q_text[4]
[1] "Will the United Nations General Assembly recognize a Palestinian state by 30 September 2011?"
> chosennames[4]
$`4`
character(0)```

Question 4 for example, was unlabeled, though a topic like "Israel" might be appropriate. That's because the word "Palestine" did not appear in any of the labeled questions. Without that word, it's hard to tell what the question is about.

#Conclusion
The random forests did a good job learning what they could from the data. Moreover, the models could be fit with only a few lines of code and were effective without modifying too many options. But it appears that there just weren't enough labeled data available here to label the questions appropriately. In Part 2 of this blog post, I consult an unsupervised machine learning approach to label these questions.

