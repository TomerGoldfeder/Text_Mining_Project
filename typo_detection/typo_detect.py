from autocorrect import spell


def check_classification(org_word, cor_word):
    # got here means the words are not the same
    # checking the length of the words
    if len(org_word) < len(cor_word):
        return "Delete"
    elif len(org_word) > len(cor_word):
        return "Insertion"

    # got here -> lens of words are the same
    # will check if the set of letters are the same for both words
    #   1. if set of letters are the same -> we have transpose if the word
    #   2. if the sets are not the same -> we have replace of the word
    l_org_word = list(org_word)
    l_cor_word = list(cor_word)

    if set(l_org_word) != set(l_cor_word):
        return "Replace"

    return "Transpose"


def detect_typo(text):
    words = text.replace(".","").replace(".","").replace("!","").replace("?","").split(" ")
    corrections = []
    for origin_word in words:
        correct_word = spell(origin_word)
        if correct_word != origin_word:
            classified_mistake = check_classification(origin_word, correct_word)
            #print("Origin Word: {}\nCorrect Word: {}\nCorrection Type: {}\n\n".format(origin_word, correct_word, classified_mistake))
            corrections.append({
                "org_word": origin_word,
                "cor_word": correct_word,
                "type": classified_mistake
            })
        else:
            classified_mistake = "Correct"
            #print("Origin Word: {}\nCorrect Word: {}\nword spelled correctly\n\n".format(origin_word, correct_word))

    return corrections


if __name__ == "__main__":
    detect_typo("caaaar mussage survice hte correct word worsd wosrd corect")

'''
Insert -> len will be greater
Delete -> len will be smaller
Replace -> len will be the same -> one or more letters will be changed into another letter.
                                    check on the array which letter has been replaced
Transpose -> len will be the same -> one or more letters will be switched with another
'''