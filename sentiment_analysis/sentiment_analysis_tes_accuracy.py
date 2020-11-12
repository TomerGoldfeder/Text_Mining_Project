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

save_classifier = open('./model/lsvm.pickle', 'wb')
pickle.dump(lsvm, save_classifier)
save_classifier.close()


