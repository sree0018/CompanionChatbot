import tensorflow as tf
import random
import json
import pickle
import numpy as np
from textblob import TextBlob
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
nltk.download('punkt')
nltk.download('wordnet')

def clean_up_sentence(sentence):
    lemmatizer = WordNetLemmatizer()
    tokens = word_tokenize(sentence)
    tokens = [lemmatizer.lemmatize(word.lower()) for word in tokens]
    return tokens

def detect_emotion(text):
    blob = TextBlob(text)
    sentiment = blob.sentiment.polarity

    if sentiment > 0:
        return "Happy"
    elif sentiment < 0:
        return "Sad"
    else:
        return "Neutral"

def bow(sentence, words, show_details=True):
    sentence_words = clean_up_sentence(sentence)
    bag = [0]*len(words)
    for s in sentence_words:
        for i,w in enumerate(words):
            if w == s:
                bag[i] = 1
                if show_details:
                    print ("found in bag: %s" % w)
    return(np.array(bag))

def classify(sentence,words,classes,model):
    ERROR_THRESHOLD = 0.15
    p = bow(sentence, words,show_details=False)
    res = model.predict(np.array([p]))[0]
    results = [[i,r] for i,r in enumerate(res) if r>ERROR_THRESHOLD]
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    return return_list

def get_response(ints):
    tag = ints[0]['intent']
    intents = json.loads(open('intents.json').read())
    for intent in intents['intents']:
        if intent['tag'] == tag:
            return random.choice(intent['responses'])