import pandas as pd
import os


def tienXuLyDuLieu():
    all_files = [f for f in os.listdir("./src/data/cau_hoi/")]
    for file in all_files:
        file_path = os.path.join("./src/data/cau_hoi/", file)
        data = pd.read_csv(file_path)
        # xóa giá trị null
        data = data.dropna()
        # xóa giá trị trùng lặp
        data = data.drop_duplicates(subset="data", keep="first")
        # lưu giá trị
        data.to_csv(file_path, index=False)
