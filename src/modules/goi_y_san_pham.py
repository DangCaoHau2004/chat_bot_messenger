from sklearn.linear_model import LogisticRegression
from skmultilearn.problem_transform import BinaryRelevance
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, hamming_loss
import numpy as np
from sklearn.svm import SVC
import pandas as pd
from modules.xu_ly_tra_loi import tra_loi_sp
import yaml
import re
from modules.xu_ly_tra_loi import tra_loi_dat_hang
# từ viết tắt
import re

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
    "1": "một",
    "ghil": "ghile",
    "ghi lê": "ghile",
    "gil": "ghile"
}


def tien_xu_ly_vb(text):
    text = text.lower()
    # Thay thế các từ viết tắt
    text = re.sub(r'[^\w\s]', '', text)

    for tu_viet_tat_key, tu_viet_tat_value in tu_viet_tat.items():
        text = re.sub(r'\b' + tu_viet_tat_key +
                      r'\b', tu_viet_tat_value, text)

    # Loại bỏ dấu câu
    return [text]


def goi_y_san_pham(loai_sp, cau_hoi, psid):
    danh_sach_sp = []

    # Điền id sản phẩm vào danh_sach_sp
    with open("./src/data/cau_tra_loi/san_pham.yml", "r", encoding="utf-8") as f:
        san_pham = yaml.safe_load(f)
        danh_sach_sp = [str(sp["id"]) for sp in san_pham[loai_sp]]

    # Đọc file csv
    data_csv = pd.read_csv(f'./src/data/cau_hoi/pl_{loai_sp}.csv')
    data_list = np.array(data_csv['data'].to_list())
    label_list = data_csv[danh_sach_sp].to_numpy()

    vectorizer = TfidfVectorizer()
    X_tfidf = vectorizer.fit_transform(data_list)

    # Huấn luyện mô hình
    X_train, X_test, y_train, y_test = train_test_split(
        X_tfidf, label_list, test_size=0.2, random_state=42)

    # Giải thuật BR với SVM
    br_clf = BinaryRelevance(SVC(kernel='linear', probability=True))
    br_clf.fit(X_train.toarray(), y_train)

    y_pred = br_clf.predict(X_test.toarray())
    print("Hamming Loss:", hamming_loss(y_test, y_pred))
    print("Accuracy Score:", accuracy_score(y_test, y_pred.toarray()))

    new_text = cau_hoi
    new_X_tfidf = vectorizer.transform(new_text)
    new_y_pred = br_clf.predict(new_X_tfidf.toarray())

    du_doan = new_y_pred.toarray()[0]
    if set(du_doan) == {0}:
        return tra_loi_dat_hang(cau_tra_loi="Sản phẩm bạn hỏi hiện tại, shop chưa có bạn có thể tham khảo một vài sản phẩm dưới đây!", psid=psid, title="Các sản Phẩm")
    return tra_loi_sp(du_doan=du_doan, id_sp=danh_sach_sp, loai_sp=loai_sp, psid=psid)
