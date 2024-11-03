import pandas as pd
import numpy as np
import csv
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split

csv_path = os.path.join(os.path.dirname(__file__), '..','data', 'cau_hoi', 'pl_cau_hoi.csv')
data_cau_hoi = pd.read_csv(csv_path)

data_list = np.array(data_cau_hoi['data'])
label_list = np.array(data_cau_hoi['label'])

vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(data_list)

X_train, X_test, y_train, y_test = train_test_split(
    X, label_list, test_size=0.2, random_state=22)

model = SVC(kernel="linear")
model.fit(X_train, y_train)
y_pred = model.predict(X_test)

accuracy = model.score(X_test, y_test)
print(f"Độ chính xác: {accuracy * 100:.2f}%")

new_text = ["cái vest này giá bao nhiêu"]
new_vector = vectorizer.transform(new_text)
prediction = model.predict(new_vector)
print(f"Dự đoán: {prediction[0]}")