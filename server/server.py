import numpy as np
from news_recommendation_service import news_class
from trainer import cnn_model
import tensorflow as tf
import pandas as pd
import pickle
import time

from jsonrpclib.SimpleJSONRPCServer import SimpleJSONRPCServer
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from watchdog.observers import Observer # to watch the changes in log file
from watchdog.events import FileSystemEventHandler

learn= tf.contrib.learn

SERVER_HOST = 'localhost'
SERVER_PORT = 6060  # it is for tcp-udp

#PORT 6060 makes possible the transmission of a datagram message from one computer to an application running in another computer.

MODEL_DIR = r'C:\Users\Riya Banerjee\PycharmProjects\news-rec_demo\model' # i will have to create a package called model in this dir
MODEL_UPDATE_LAG_IN_SECONDS = 10  # why?

N_CLASSES = 8 # no of topics

VARS_FILE = r'C:\Users\Riya Banerjee\PycharmProjects\news-rec_demo\model\vars' # left
VOCAB_PROCESSOR_SAVE_FILE = r'C:\Users\Riya Banerjee\PycharmProjects\news-rec_demo\model\vocab_procesor_save_file' # left

n_words = 0 # len of vocabulary

MAX_DOCUMENT_LENGTH = 500  # it was 400 back then why now 500?
vocab_processor = None
classifier = None

stemmer = PorterStemmer()
stop_words = set(stopwords.words('english'))

def restoreVars():
    with open(VARS_FILE,'rb') as f:
        global n_words
        global vocab_processor
        n_words=pickle.load(f)
        # Python pickle module is used for serializing and de-serializing a Python object structure. ...
        # Pickling is a way to convert a python object (list, dict, etc.) into a character stream. The idea is that this character stream contains all t
        # the information necessary to reconstruct the object in another python script.

        # print(n_words)
        vocab_processor=learn.preprocessing.VocabularyProcessor.restore(VOCAB_PROCESSOR_SAVE_FILE) #Restores vocabulary processor from given file.
        # print(vocab_processor)

def loadModel():
    global classifier
    classifier=tf.estimator.Estimator(model_fn= cnn_model.generate_cnn_model(N_CLASSES, n_words), model_dir= MODEL_DIR)
    classifier = learn.Estimator(model_fn=cnn_model.generate_cnn_model(N_CLASSES, n_words), model_dir=MODEL_DIR)
    # this is a custom estimator. hence we need to specify the model_fn and if model_dir is not set, a temp dir will be used.
    # custom estimators-https://www.tensorflow.org/guide/custom_estimators

    df = pd.read_csv('../data/labeled_news.csv', header=None)

    # TODO: fix this until https://github.com/tensorflow/tensorflow/issues/5548 is solved.
    # We have to call evaluate or predict at least once to make the restored Estimator work.
    train_df = df[0:400]
    x_train = train_df[1]
    x_train = np.array(list(vocab_processor.transform(x_train)))
    y_train = train_df[0]
    classifier.evaluate(x_train, y_train)
    print("model update")


# restoreVars()
loadModel()

print("model loaded")

class ReloadModelHandler(FileSystemEventHandler):
    def on_any_event(self, event): # any event of whom????
        # Reload model
        print("Model update detected. Loading new model.")
        time.sleep(MODEL_UPDATE_LAG_IN_SECONDS)
        restoreVars()
        loadModel()


# Setup watchdog
observer = Observer()
observer.schedule(ReloadModelHandler(), path=MODEL_DIR, recursive=False)
observer.start()


def classify(text):
    # text_tokens = word_tokenize(text)
    # stemmed_tokens = [stemmer.stem(w.lower()) for w in text_tokens if not w in stop_words]
    # norm_sentence = ' '.join(stemmed_tokens)

    text_series = pd.Series([text])
    predict_x = np.array(list(vocab_processor.transform(text_series)))
    print(predict_x)

    y_predicted = [
        p['class'] for p in classifier.predict(
            predict_x, as_iterable=True)
    ]
    print(y_predicted[0])
    topic = news_class.class_map[str(y_predicted[0])]
    return topic


# Threading RPC Server
RPC_SERVER = SimpleJSONRPCServer((SERVER_HOST, SERVER_PORT))
RPC_SERVER.register_function(classify, 'classify')

print(("Starting RPC server on %s:%d" % (SERVER_HOST, SERVER_PORT)))

RPC_SERVER.serve_forever()
