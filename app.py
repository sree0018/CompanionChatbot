from flask import Flask,render_template, request,redirect, session
from flask_pymongo import PyMongo
import pickle
import tensorflow as tf
from methods import *
from dotenv import load_dotenv
import os
import google.generativeai as genai

load_dotenv()
API_KEY = os.environ['OPENAI_API_KEY']
genai.configure(api_key=API_KEY)
## function to load Gemini Pro model and get repsonses
aimodel=genai.GenerativeModel("gemini-pro") 
def get_gemini_response(question,history=[]):
    chat = aimodel.start_chat(history=history)
    response=chat.send_message(question,stream=True)
    return response
# Load preprocessed data
words = pickle.load(open('words.pkl', 'rb'))
classes = pickle.load(open('classes.pkl', 'rb'))
# Load trained model
model = tf.keras.models.load_model('chatbot_model.h5')


app = Flask(__name__,static_folder='C:\proj\static',template_folder='C:\proj\\template')
app.config["MONGO_URI"] = 'mongodb+srv://namithafreakygirl007:Qwerty*123@cluster0.srvz1so.mongodb.net/users?retryWrites=true&w=majority&appName=Cluster0'
mongo = PyMongo(app)
import pymongo
# Initialize MongoDB client
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["chatbot_db"]
def store_conversation(username, conversation):
    # Store or update conversation for the given username
    conversation_data = {"username": username, "conversation": conversation}
    db["conversations"].replace_one({"username": username}, conversation_data, upsert=True)
def retrieve_conversation(username):
    # Retrieve conversation for the given username
    conversation_data = db["conversations"].find_one({"username": username})
    if conversation_data:
        return conversation_data["conversation"]
    else:
        return []


@app.route('/')
def mainpage():
    return render_template('index.html')

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            user = mongo.db.users.find_one({'username':username, 'password':password})
            if user:
                session['username'] = username
                return redirect('/dashboard')
            else:
                return "Invalid username or password"
    return render_template('login.html')

@app.route('/signup',methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
            
        # Check if username already exists
        existing_user = mongo.db.users.find_one({'username': username})
        if existing_user:
         return 'Username already exists. Please choose a different username.'
        user_data = {'username': username, 'password': password}
        mongo.db.users.insert_one(user_data)
        session['username'] = username
        return redirect('/login')
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')


@app.route('/bot')
def botpage():
    if 'username' in session:
        return render_template('index.html')
    else:
        return redirect('/login')
    # return render_template('index.html')
@app.route("/get")
def get_bot_response():
    global context_window
    inp = request.args.get('msg')
    emotion = detect_emotion(inp)
    results = classify(inp+' '+emotion,words,classes,model)
    if results:
        text = get_response(results)
        # response_g=get_gemini_response(f'rewrite the rsponse here input is {inp} and the reponse is {text}')
        response_g=get_gemini_response('write postive response also ask reason if any in 30 words for '+inp+' '+text)
        response=[]
        for chunk in response_g:
                response_text = chunk.text
                print("Bot:", response_text)
                response.append(response_text)
    else:
        print("Bot: I'm sorry, I didn't understand that.")
    print('##########################################################')
    print(inp)
    print('----------------------------------------------------------')
    print("Bot:", response)
    print('##########################################################')
    response_text = ''.join(response)
    return response_text

#app.run(debug=True)
app.run()

