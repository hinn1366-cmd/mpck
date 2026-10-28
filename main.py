import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(title="Mô phỏng biến động giá chứng khoán")
os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Đọc dữ liệu và tự động sinh 2 biểu đồ khi khởi động
csv_path = "abc-6.csv"
if os.path.exists(csv_path):
    df_raw = pd.read_csv(csv_path, header=None)
    prices = df_raw.mean(axis=1).values
    
    # Tính phần trăm thay đổi để phân loại xu hướng
    pct_changes = (np.diff(prices) / prices[:-1]) * 100

    # 1. Vẽ biểu đồ 1: Phân phối giá đóng cửa
    plt.figure(figsize=(7, 4))
    plt.hist(prices, bins=12, edgecolor='black', alpha=0.7, color='#0ea5e9', density=True)
    plt.title(f"Phân phối giá đóng cửa ({len(prices)} phiên)", fontsize=11, fontweight='bold')
    plt.xlabel("Mức giá (VND)")
    plt.ylabel("Mật độ tần suất")
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig("static/chart_1.png", dpi=150)
    plt.close()

    # 2. Vẽ biểu đồ 2: Phân loại xu hướng phiên giao dịch (%)
    tang_manh = np.sum(pct_changes > 1.0)
    tang = np.sum((pct_changes > 0) & (pct_changes <= 1.0))
    di_ngang = np.sum(pct_changes == 0)
    giam = np.sum((pct_changes < 0) & (pct_changes >= -1.0))
    giam_manh = np.sum(pct_changes < -1.0)

    categories = ['Tăng mạnh (>1%)', 'Tăng nhẹ', 'Đi ngang', 'Giảm nhẹ', 'Giảm mạnh']
    counts = [tang_manh, tang, di_ngang, giam, giam_manh]
    
    plt.figure(figsize=(7, 4))
    plt.bar(categories, counts, color=['#22c55e', '#86efac', '#eab308', '#fca5a5', '#ef4444'], edgecolor='black', linewidth=0.5)
    plt.title("Phân loại xu hướng biến động giữa các phiên", fontsize=11, fontweight='bold')
    plt.xlabel("Nhóm biên độ")
    plt.ylabel("Số lượng phiên")
    plt.grid(True, linestyle='--', alpha=0.5, axis='y')
    plt.tight_layout()
    plt.savefig("static/chart_2.png", dpi=150)
    plt.close()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    # Truyền nội dung nhận xét trực tiếp ra web
    comments = {
        "cmt_1": "Biểu đồ phân phối giá phản ánh mật độ tập trung của mức giá cổ phiếu trong suốt chu kỳ năm. Phần lớn các phiên giao dịch tập trung ở vùng giá trung tâm, cho thấy sự ổn định tương đối trước khi có những nhịp bứt phá hoặc sụt giảm mạnh về phía đuôi phân phối.",
        "cmt_2": "Biểu đồ phân loại xu hướng cho thấy tỷ trọng phân bổ giữa các phiên tăng và giảm giá. Các phiên tăng/giảm nhẹ chiếm đa số, thể hiện thị trường vận động bám sát cung cầu tự nhiên, trong khi các phiên biến động mạnh (>1% hoặc <-1%) đánh dấu các thời điểm dòng tiền lớn hoặc thông tin tác động đột biến."
    }
    return templates.TemplateResponse(request, "index.html", {"comments": comments})S