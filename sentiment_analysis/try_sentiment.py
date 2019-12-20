from sentiment_analysis import detect_sentiment


def main():
    text = "It is a beautiful day"
    prediction = detect_sentiment(text)
    print(prediction[0])

    '''
    printed: happiness
    '''


if __name__ == "__main__":
    main()