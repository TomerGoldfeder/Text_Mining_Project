import pandas as pd
import pickle
from sklearn.feature_extraction.text import CountVectorizer
from nltk.corpus import stopwords
from textblob import Word

stop = stopwords.words('english')


def sentent_vectorizer(prediction):
    return ['anger', 'happiness', 'neutral', 'sadness', 'surprise'][prediction]


def get_sentiment(arr):
    tweets = pd.DataFrame(arr)

    # This is quite depressing. I am filled with sorrow - sadness 3
    # I am beginning to think sun blcok is a haox. - anger 0
    # I dont understand why he's doing this - surprise 4
    # Raining...  I missed the rain so much...  I am grateful for it ;) - happiness 1
    # neutral 2

    tweets[0] = tweets[0].str.replace('[^\w\s]', ' ')
    tweets[0] = tweets[0].apply(lambda x: " ".join(x for x in x.split() if x not in stop))
    tweets[0] = tweets[0].apply(lambda x: " ".join([Word(word).lemmatize() for word in x.split()]))

    count_vect = CountVectorizer(analyzer='word')
    save_classifier = open('./model/word_features.pickle', 'rb')
    data_content = pickle.load(save_classifier)
    save_classifier.close()
    count_vect.fit(data_content)

    save_classifier = open('./model/lsvm.pickle', 'rb')
    lsvm = pickle.load(save_classifier)
    save_classifier.close()

    tweet_count = count_vect.transform(tweets[0])
    tweet_pred = lsvm.predict(tweet_count)

    arr_of_sentences_vectorized = []
    for pr in tweet_pred:
        arr_of_sentences_vectorized.append(sentent_vectorizer(pr))

    return arr_of_sentences_vectorized


def detect_sentiment(text):
    return get_sentiment([text])