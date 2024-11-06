from skmultilearn.problem_transform import BinaryRelevance
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, hamming_loss
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import pandas as pd
from modules.xu_ly_tra_loi import tra_loi_sp
import yaml
import re
# từ viết tắt
tu_viet_tat = {
    "k": "không",
    "ko": "không",
    "kho": "không",
    "c": "có",
    "n mà": "nhưng mà",
    "mk": "mình",
    "e": "em",
    "a": "anh",
    "2": "hai",
    "3": "ba",
    "1": "một"
}


def tien_xu_ly_vb(text):
    text = text.lower()
    text = text.split()
    # Thay từ viết tắt
    for index in range(len(text)):
        if text[index] in tu_viet_tat:
            text[index] = tu_viet_tat[text[index]]

    # Loại bỏ dấu câu
    text = re.sub(r'[^\w\s]', '', ' '.join(text))
    text = [text]
    return text


def goi_y_san_pham(loai_sp, cau_hoi):
    danh_sach_sp = []

    # Điền id sản phẩm vào danh_sach_sp
    with open("./data/cau_tra_loi/san_pham.yml", "r", encoding="utf-8") as f:
        san_pham = yaml.safe_load(f)
        danh_sach_sp = [str(sp["id"]) for sp in san_pham[loai_sp]]
        print(danh_sach_sp)

    # Đọc file csv
    data_csv = pd.read_csv(f'./data/cau_hoi/pl_{loai_sp}.csv')
    data_list = np.array(data_csv['data'].to_list())
    label_list = data_csv[danh_sach_sp].to_numpy()

    vectorizer = TfidfVectorizer()
    X_tfidf = vectorizer.fit_transform(data_list)

    # Huấn luyện mô hình
    X_train, X_test, y_train, y_test = train_test_split(
        X_tfidf, label_list, test_size=0.2, random_state=42)

    # Giải thuật BR
    br_clf = BinaryRelevance(RandomForestClassifier(n_estimators=100))
    br_clf.fit(X_train.toarray(), y_train)

    y_pred = br_clf.predict(X_test.toarray())
    print("Hamming Loss:", hamming_loss(y_test, y_pred))
    print("Accuracy Score:", accuracy_score(y_test, y_pred.toarray()))

    new_text = cau_hoi
    print(new_text)
    new_text = tien_xu_ly_vb(new_text)
    print(new_text)
    new_X_tfidf = vectorizer.transform(new_text)
    new_y_pred = br_clf.predict(new_X_tfidf.toarray())

    du_doan = new_y_pred.toarray()[0]
    print(du_doan)
    print(tra_loi_sp(du_doan=du_doan, id_sp=danh_sach_sp, loai_sp=loai_sp))
