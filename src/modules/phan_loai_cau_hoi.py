import pandas as pd
import numpy as np
import os
import yaml
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from xu_ly_tra_loi import tra_loi_tu_van
def phan_loai_cau_hoi(new_text):
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

    #kiểm tra độ chính xác
    accuracy = model.score(X_test, y_test)
    print(f"Độ chính xác: {accuracy * 100:.2f}%")

    new_vector = vectorizer.transform([new_text])
    prediction = model.predict(new_vector)[0]
    with open('../data/cau_tra_loi/tu_van.yml','r', encoding='utf-8') as file_tuvan_yml:
        cau_tra_loi = yaml.safe_load(file_tuvan_yml)
        
    if prediction in cau_tra_loi:
        print(tra_loi_tu_van(du_doan=prediction))
    else:
        csv_path = os.path.join(os.path.dirname(__file__), '..','data', 'cau_hoi', 'pl_san_pham.csv')
        data_cau_hoi = pd.read_csv(csv_path)

        data_list = np.array(data_cau_hoi['data'])
        label_list = np.array(data_cau_hoi['label'])

        vectorizer = TfidfVectorizer()
        X = vectorizer.fit_transform(data_list)

        X_train, X_test, y_train, y_test = train_test_split(
            X, label_list, test_size=0.2, random_state=22)

        model = SVC(kernel="linear")
        model.fit(X_train, y_train)

        new_vector = vectorizer.transform([new_text])
        prediction = model.predict(new_vector)[0]
    print("Dự đoán: " + prediction)

# #ví dụ dự đoán
# new_text = ["áo đẹp nhất "]
# du_doan = phan_loai_cau_hoi(new_text)
# print(du_doan)

phan_loai_cau_hoi("Ưu đãi")