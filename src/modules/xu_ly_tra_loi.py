import yaml
import os
from dotenv import load_dotenv
URL_WEB_ORDER = os.getenv("URL_WEB_ORDER")

load_dotenv()


def tra_loi_sp(du_doan, id_sp, loai_sp, psid):
    danh_sach_sp_mua = [id_sp[i] for i in range(len(du_doan)) if du_doan[i]]

    if not danh_sach_sp_mua:
        return "Không tồn tại sản phẩm!"

    thong_tin_cac_san_pham = "Shop có một vài mẫu theo yêu cầu của bạn tham khảo nha\n\n"

    # Đọc dữ liệu từ file YAML
    with open("./src/data/cau_tra_loi/san_pham.yml", "r", encoding="utf-8") as f:
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


def tra_loi_tu_van(du_doan, psid):
    with open('./src/data/cau_tra_loi/tu_van.yml', 'r', encoding='utf-8') as file_tuvan_yml:
        cau_tra_loi = yaml.safe_load(file_tuvan_yml)
        if du_doan == "dat_hang":
            return tra_loi_dat_hang(cau_tra_loi=cau_tra_loi[du_doan]["tra_loi"], psid=psid)
    return {"text": cau_tra_loi[du_doan]}


def tra_loi_dat_hang(cau_tra_loi, psid):
    return {
        "attachment": {
            "type": "template",
            "payload": {
                    "template_type": "button",
                    "text": cau_tra_loi,
                    "buttons": [
                        {
                            "type": "web_url",
                            "url": URL_WEB_ORDER + f"?psid={psid}",
                            "title": "Đặt hàng",
                            "webview_height_ratio": "full",
                            "messenger_extensions": True,
                        }
                    ]
            }
        }
    }
