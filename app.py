from flask import Flask, render_template, request, redirect, session, url_for
from typo_detection.typo_detect import detect_typo
from sentiment_analysis.sentiment_analysis import detect_sentiment
import json
app = Flask(__name__)

typos_list = ['Delete', 'Insertion', 'Replace', 'Transpose']


@app.route("/")
def home():
    return render_template("index.html")


def check_typo(user_text):
    typo = detect_typo(user_text)
    if len(typo) == 0:
        st = "No typo in tweet"
    else:
        deletes = ["{}, {}".format(x['org_word'], x['cor_word']) for x in typo if x['type'] == "Delete"]
        inserts = ["{}, {}".format(x['org_word'], x['cor_word']) for x in typo if x['type'] == "Insertion"]
        replaces = ["{}, {}".format(x['org_word'], x['cor_word']) for x in typo if x['type'] == "Replace"]
        transposes = ["{}, {}".format(x['org_word'], x['cor_word']) for x in typo if x['type'] == "Transpose"]

        st = "You had several ({}) mistakes in the tweet.<br>".format(
            len(deletes) + len(inserts) + len(replaces) + len(transposes))
        if len(deletes) > 0:
            st += " Delete: {}<br>".format("<br>".join(deletes))
        if len(inserts) > 0:
            st += " Insertion: {}<br>".format("<br>".join(inserts))
        if len(replaces) > 0:
            st += " Replace: {}<br>".format("<br>".join(replaces))
        if len(transposes) > 0:
            st += " Transpose: {}<br>".format("<br>".join(transposes))

    return st, typo


def check_emotion(user_text):
    prediction = detect_sentiment(user_text)
    return prediction[0]


def get_emotion_response(emotion):
    # emotions = ['anger', 'happiness', 'neutral', 'sadness', 'surprise']
    if emotion in ['happiness', 'sadness']:
        return "happy" if emotion == "happiness" else "sad"
    else:
        return emotion

def write_to_json(emotion, corrections):
    '''
    {
      "org_word": origin_word,
      "cor_word": correct_word,
      "type": classified_mistake
    }
    '''
    data = ""
    with open("statistics.json", "r") as json_file:
        data = json.load(json_file)
        stats = data['stats']
        emotions_stats = stats[emotion]
        for cor in corrections:
            emotions_stats[cor['type']] += 1

    with open("statistics.json", "w") as json_file:
        json.dump(data, json_file)


def print_stats():
    emotions_stats = {}
    with open("statistics.json", "r") as json_file:
        data = json.load(json_file)
        stats = data['stats']
        #['anger', 'happiness', 'neutral', 'sadness', 'surprise']
        #"Delete": 0, "Insertion": 0, "Replace": 0, "Transpose": 0
        emotions_stats.update({
            "anger": {
                "Delete": stats['anger']['Delete'],
                "Insertion": stats['anger']['Insertion'],
                "Replace": stats['anger']['Replace'],
                "Transpose": stats['anger']['Transpose']
            }
        })
        emotions_stats.update({
            "happiness": {
                "Delete": stats['happiness']['Delete'],
                "Insertion": stats['happiness']['Insertion'],
                "Replace": stats['happiness']['Replace'],
                "Transpose": stats['happiness']['Transpose']
            }
        })
        emotions_stats.update({
            "neutral": {
                "Delete": stats['neutral']['Delete'],
                "Insertion": stats['neutral']['Insertion'],
                "Replace": stats['neutral']['Replace'],
                "Transpose": stats['neutral']['Transpose']
            }
        })
        emotions_stats.update({
            "sadness": {
                "Delete": stats['sadness']['Delete'],
                "Insertion": stats['sadness']['Insertion'],
                "Replace": stats['sadness']['Replace'],
                "Transpose": stats['sadness']['Transpose']
            }
        })
        emotions_stats.update({
            "surprise": {
                "Delete": stats['surprise']['Delete'],
                "Insertion": stats['surprise']['Insertion'],
                "Replace": stats['surprise']['Replace'],
                "Transpose": stats['surprise']['Transpose']
            }
        })

        return json.dumps(emotions_stats)


@app.route("/get_stats")
def get_stats():
    messages = print_stats()
    return messages


@app.route("/stats_view")
def build_stats_view():
    return render_template("stats_view.html")
    #return messages


@app.route("/get")
def get_bot_response():
    user_text = request.args.get('msg')

    if user_text in ["show stats","show statistics"]:
        return redirect(url_for('.build_stats_view'))
        #return_text = print_stats()
    else:
        typo_or_not, corrections = check_typo(user_text)
        which_emotion = check_emotion(user_text)
        return_text = "You feel {} about this<br>".format(get_emotion_response(which_emotion))
        if typo_or_not != "No typo in tweet":
            return_text += typo_or_not

        write_to_json(which_emotion, corrections)

    return return_text


if __name__ == "__main__":
    app.run()
