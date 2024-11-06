import yaml


def tra_loi_sp(du_doan, id_sp, loai_sp):
    danh_sach_sp_mua = [id_sp[i] for i in range(len(du_doan)) if du_doan[i]]

    if not danh_sach_sp_mua:
        return "Không tồn tại sản phẩm!"

    thong_tin_cac_san_pham = ""

    # Đọc dữ liệu từ file YAML
    with open("../data/cau_tra_loi/san_pham.yml", "r", encoding="utf-8") as f:
        san_pham = yaml.safe_load(f)

        # Tìm và ghép thông tin sản phẩm
        for label_id in danh_sach_sp_mua:
            for product in san_pham[loai_sp]:
                if product["id"] == int(label_id):
                    if loai_sp != "phu_kien":
                        thong_tin_cac_san_pham += (
                            f"\nTên: {product['ten']}\n"
                            f"Màu sắc: {product['mau_sac']}\n"
                            f"Kích cỡ: {product['kich_co']}\n"
                            f"Giá: {product['gia']} VND\n"
                            f"Mô tả: {product['mo_ta']}\n\n"
                        )
                    else:
                        thong_tin_cac_san_pham += (
                            f"\nTên: {product['ten']}\n"
                            f"Màu sắc: {product['mau_sac']}\n"
                            f"Giá: {product['gia']} VND\n"
                            f"Mô tả: {product['mo_ta']}\n\n"
                        )

    return {"text": thong_tin_cac_san_pham}


def tra_loi_tu_van(du_doan):
    with open('../data/cau_tra_loi/tu_van.yml', 'r', encoding='utf-8') as file_tuvan_yml:
        cau_tra_loi = yaml.safe_load(file_tuvan_yml)
        if du_doan == "dat_hang":
            return {"text": cau_tra_loi[du_doan]["tra_loi"]}
    return {"text": cau_tra_loi[du_doan]}
