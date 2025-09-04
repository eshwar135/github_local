from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression

class SimpleClassifier:
    def __init__(self):
        self.vectorizer = CountVectorizer()
        self.classifier = LogisticRegression()

    def train(self, X, y):
        X_vec = self.vectorizer.fit_transform(X)
        self.classifier.fit(X_vec, y)

    def predict(self, query):
        X_vec = self.vectorizer.transform([query])
        return self.classifier.predict(X_vec)[0]
