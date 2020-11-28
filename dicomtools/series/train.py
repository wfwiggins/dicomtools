# AUTOGENERATED! DO NOT EDIT! File to edit: 02_series.train.ipynb (unless otherwise specified).

__all__ = ['train_setup', 'train_fit']

# Cell
from ..basics import *

np.random.seed(42)

from sklearn.ensemble import RandomForestClassifier
from joblib import dump

# Cell
def train_setup(df):
    "Extract labels for training data and use 'unknown' as test set"
    df1 = preprocess(df)
    labels = extract_labels(df1)
    df1 = df1.join(labels[['plane', 'contrast', 'seq_label']])
    filt = df1['seq_label'] == 'unknown'
    train = df1[~filt].copy().reset_index(drop=True)
    test = df1[filt].copy().reset_index(drop=True)
    y, y_names = pd.factorize(train['seq_label'])
    return train, test, y, y_names


# Cell
def train_fit(train, y, features, fname='model-run.skl'):
    "Train a Random Forest classifier on `train[features]` and `y`, then save to `fname` and return."
    clf = RandomForestClassifier(n_jobs=2, random_state=0)
    clf.fit(train[features], y)
    dump(clf, fname)
    return clf
