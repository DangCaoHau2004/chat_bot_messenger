import pandas as pd
import numpy as np
import yaml
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from modules.xu_ly_tra_loi import tra_loi_tu_van
from modules.goi_y_san_pham import goi_y_san_pham
from modules.goi_y_san_pham import tien_xu_ly_vb


def phan_loai_cau_hoi(new_text, psid):
    # Load và xử lý dữ liệu câu hỏi tư vấn
    data_cau_hoi = pd.read_csv('./src/data/cau_hoi/pl_cau_hoi.csv')
    data_list = np.array(data_cau_hoi['data'])
    label_list = np.array(data_cau_hoi['label'])

    # Khởi tạo TF-IDF Vectorizer và SVM model
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(data_list)

    X_train, X_test, y_train, y_test = train_test_split(
        X, label_list, test_size=0.2, random_state=22
    )

    model = SVC(kernel="linear")
    model.fit(X_train, y_train)

    # Kiểm tra độ chính xác
    accuracy = model.score(X_test, y_test)
    print(f"Độ chính xác: {accuracy * 100:.2f}%")
    new_text = tien_xu_ly_vb(new_text)
    print(new_text)
    new_vector = vectorizer.transform(new_text)
    prediction = model.predict(new_vector)[0]

    # Kiểm tra trong câu trả lời tư vấn
    with open('./src/data/cau_tra_loi/tu_van.yml', 'r', encoding='utf-8') as file_tuvan_yml:
        cau_tra_loi = yaml.safe_load(file_tuvan_yml)

    if prediction in cau_tra_loi:
        return tra_loi_tu_van(du_doan=prediction, psid=psid)
    else:
        data_san_pham = pd.read_csv('./src/data/cau_hoi/pl_san_pham.csv')
        data_list_sp = np.array(data_san_pham['data'])
        label_list_sp = np.array(data_san_pham['label'])

        vectorizer_sp = TfidfVectorizer()
        X_sp = vectorizer_sp.fit_transform(data_list_sp)

        X_train_sp, X_test_sp, y_train_sp, y_test_sp = train_test_split(
            X_sp, label_list_sp, test_size=0.2, random_state=22
        )

        model_sp = SVC(kernel="linear")
        model_sp.fit(X_train_sp, y_train_sp)

        new_vector_sp = vectorizer_sp.transform(new_text)
        prediction_sp = model_sp.predict(new_vector_sp)[0]

        return goi_y_san_pham(loai_sp=prediction_sp, cau_hoi=new_text, psid=psid)
