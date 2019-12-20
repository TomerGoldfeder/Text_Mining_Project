import pandas as pd
import numpy as np
import sys
from textblob import Word
import re
from nltk.corpus import stopwords
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import SGDClassifier

stop = stopwords.words('english')
np.set_printoptions(threshold=sys.maxsize)


def repet_regex(text):
    pattern = re.compile(r"(.)\1{2,}")
    return pattern.sub(r"\1\1", text)


print("getting the data from csv...")
data = pd.read_csv('text_emotion.csv')

data = data.drop('author', axis=1)
data = data.drop(data[data.sentiment == 'hate'].index)
data = data.drop(data[data.sentiment == 'love'].index)
data = data.drop(data[data.sentiment == 'fun'].index)
data = data.drop(data[data.sentiment == 'relief'].index)
data = data.drop(data[data.sentiment == 'worry'].index)
data = data.drop(data[data.sentiment == 'boredom'].index)
data = data.drop(data[data.sentiment == 'enthusiasm'].index)
data = data.drop(data[data.sentiment == 'empty'].index)
print("dropped columns from csv...")

data['content'] = data['content'].apply(lambda x: " ".join(x.lower() for x in x.split()))
data['content'] = data['content'].str.replace('[^\w\s]', ' ')
data['content'] = data['content'].apply(lambda x: " ".join(x for x in x.split() if x not in stop))
data['content'] = data['content'].apply(lambda x: " ".join([Word(word).lemmatize() for word in x.split()]))
data['content'] = data['content'].apply(lambda x: " ".join(repet_regex(x) for x in x.split()))

# getting 10,000 most frequent words
freq = pd.Series(' '.join(data['content']).split()).value_counts()[-10000:]
freq = list(freq.index)
data['content'] = data['content'].apply(lambda x: " ".join(x for x in x.split() if x not in freq))

# save_word_features = open("./model/word_features.pickle", "wb")
# pickle.dump(data['content'], save_word_features)
# save_word_features.close()

labels_encode = preprocessing.LabelEncoder()
y = labels_encode.fit_transform(data.sentiment.values)
print("processed all data...")

X_train, X_val, y_train, y_val = train_test_split(data.content.values, y, stratify=y, random_state=42, test_size=0.1,
                                                  shuffle=True)
print("splitted all data...")

# Extracting TF-IDF parameters
tfidf = TfidfVectorizer(max_features=1000, analyzer='word', ngram_range=(1, 3))
X_train_tfidf = tfidf.fit_transform(X_train)
X_val_tfidf = tfidf.fit_transform(X_val)

# Extracting Count Vectors Parameters
count_vect = CountVectorizer(analyzer='word')
count_vect.fit(data['content'])
X_train_count = count_vect.transform(X_train)
X_val_count = count_vect.transform(X_val)

print("starting...")

# Model 2: Linear SVM

lsvm = SGDClassifier(alpha=0.001, random_state=5, max_iter=15, tol=None)
lsvm.fit(X_train_count, y_train)

# save_classifier = open('./model/lsvm.pickle', 'wb')
# pickle.dump(lsvm, save_classifier)
# save_classifier.close()

tweets = pd.DataFrame(['I am very happy today! The atmosphere looks cheerful',
                       'Things are looking great. It was such a good day',
                       'Success is right around the corner. Lets celebrate this victory',
                       'Everything is more beautiful when you experience them with a smile!',
                       'Now this is my worst, okay? But I am gonna get better.',
                       'I am tired, boss. Tired of being on the road, lonely as a sparrow in the rain',
                       'I am tired of all the pain I feel',
                       'This is quite depressing. I am filled with sorrow',
                       'His death broke my heart. It was a sad day',
                       'This is so annoying!!', 'I am beginning to think sun block is a hoax.',
                       "I do not understand why he is doing this",
                       'Where are you?', 'How sad that she would be too proud to have fun',
                       'Lana felt for the quiet woman as she fell in to a sad silence',
                       'It was real sad how Annie ended up.',
                       'He felt sad and depressed.',
                       'This day sucks!'
                       ])

# This is quite depressing. I am filled with sorrow - sadness 3
# I am beginning to think sun blcok is a haox. - anger 0
# I dont understand why he's doing this - surprise 4
# Raining...  I missed the rain so much...  I am grateful for it ;) - happiness 1
# neutral 2

labels = [1, 1, 1, 1, 3, 3, 3, 3, 3, 0, 0, 4, 2, 3, 3, 3, 3, 3]

tweets[0] = tweets[0].str.replace('[^\w\s]', ' ')
tweets[0] = tweets[0].apply(lambda x: " ".join(x for x in x.split() if x not in stop))
tweets[0] = tweets[0].apply(lambda x: " ".join([Word(word).lemmatize() for word in x.split()]))

tweet_count = count_vect.transform(tweets[0])
tweet_pred = lsvm.predict(tweet_count)
correct_tweet_analysis = 0
incorrect_tweet_analysis = 0

for i in range(len(tweet_pred)):
    if tweet_pred[i] == labels[i]:
        correct_tweet_analysis += 1
        print("Correct: {}, prediction: {}".format(i, tweet_pred[i]))
    else:
        print("Incorrect: {}, prediction: {}, true: {}".format(i, tweet_pred[i], labels[i]))
        incorrect_tweet_analysis += 1

print("\naccuracy: {}".format(correct_tweet_analysis/len(tweet_pred)))


