import pandas as pd
import numpy as np
import csv
import os
import yaml
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

new_text = ["hello"]
new_vector = vectorizer.transform(new_text)
prediction = model.predict(new_vector)
print(f"Dự đoán: {prediction[0]}")

def load_yaml_by_label(label):
    yaml_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'cau_tra_loi', f"{label}.yml")
    if os.path.exists(yaml_path):
        with open(yaml_path, 'r', encoding='utf-8') as file:
            yaml_data = yaml.safe_load(file)
            return yaml_data
    else:
        print(f"No YAML file found for label: {label}")
        return None
yaml_content = load_yaml_by_label(prediction[0])
print("Dữ liệu từ file YAML:", yaml_content)