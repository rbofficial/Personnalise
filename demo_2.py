from trainer import cnn_model_demo
import numpy as np
import os
import pandas as pd
import pickle
import shutil
import tensorflow as tf

from sklearn import metrics
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import word_tokenize
from os.path import join
from os.path import normpath

stemmer = PorterStemmer()
stop_words = set(stopwords.words('english'))

MODEL_OUTPUT_DIR = normpath(join(os.path.dirname(__file__), '../model/'))
VARS_FILE = normpath(join(os.path.dirname(__file__), '../model/vars'))
VOCAB_PROCESSOR_SAVE_FILE = normpath(join(os.path.dirname(__file__), '../model/vocab_procesor_save_file'))

learn = tf.contrib.learn
DATA_SET_FILE = r'C:\Users\Riya Banerjee\Desktop\Riya\news-category-dataset\sqlify-result-ba7298645de74.csv'
REMOVE_PREVIOUS_MODEL = True


def run():
    if REMOVE_PREVIOUS_MODEL:  # i think its for removing previous cnn model # why tho- search why is this necessary?
        # remove old model
        print("Removing previous model...")
        shutil.rmtree(MODEL_OUTPUT_DIR)
        os.mkdir(MODEL_OUTPUT_DIR)

    df = pd.read_csv(DATA_SET_FILE)
    # Random shuffle
    df.sample(frac=1)

    train_df = df[0:468660]  # is this too taken randomly?
    # train_df[2}.dropna(inplace=True)
    test_df = df.drop(train_df.index)
    # print(train_df)

    x_train = train_df[2]
    y_train = train_df[0]
    x_test = test_df[2]
    y_test = test_df[0]

    # print(type(x_train.tolist()))

    # # tokenize sentences
    x_train = [word_tokenize(str(sentence)) for sentence in x_train.tolist()]
    # print(x_train)
    x_test = [word_tokenize(str(sentence)) for sentence in x_test.tolist()]

    # Stemming words.
    norm_x_train = []
    norm_x_test = []
    for tokens in x_train:
        stemmed_tokens = [stemmer.stem(w.lower()) for w in tokens if not w in stop_words]
        norm_sentence = ' '.join(stemmed_tokens)
        norm_x_train.append(norm_sentence)

    for tokens in x_test:
        stemmed_tokens = [stemmer.stem(w.lower()) for w in tokens if not w in stop_words]
        norm_sentence = ' '.join(stemmed_tokens)
        norm_x_test.append(norm_sentence)

    x_train = norm_x_train
    x_test = norm_x_test

    # print(x_train)

    vocab_processor = learn.preprocessing.VocabularyProcessor(200)
    # print(vocab_processor.fit_transform(x_train))
    x_train = np.array(list(vocab_processor.fit_transform(x_train)))
    # print(len(vocab_processor.vocabulary_))
    x_test = np.array(list(vocab_processor.transform(x_test)))

    n_words = len(vocab_processor.vocabulary_)  # what is this
    print('Total words: %d' % n_words)

    with open(VARS_FILE, 'wb') as f:  # needs to be opened in binary mode.
        pickle.dump(n_words, f)

        # Build model-0.406897
    classifier = learn.Estimator(
        model_fn=cnn_model_demo.generate_cnn_model(41, n_words),
        model_dir=MODEL_OUTPUT_DIR)

    # Train and predict
    classifier.fit(x_train, y_train, steps=10)

    # Evaluate model
    y_predicted = [
        p['class'] for p in classifier.predict(x_test, as_iterable=True)
    ]

    score = metrics.accuracy_score(y_test, y_predicted)
    print('Accuracy: {0:f}'.format(score))


if __name__ == '__main__':
    run()
