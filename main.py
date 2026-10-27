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

# Khởi tạo giá trị mặc định phòng hờ
stats = {
    "total_days": 365,
    "avg_price": 100.0,
    "max_price": 120.0,
    "win_rate": "52.5%"
}

# Tự động đọc CSV và vẽ biểu đồ ngay khi ứng dụng khởi động
try:
    csv_path = "abc-6.csv"
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        numeric_cols = df.select_dtypes(include='number').columns
        if len(numeric_cols) > 0:
            col = numeric_cols[0]
            prices = df[col].dropna().values
            stats["total_days"] = len(prices)
            stats["avg_price"] = round(float(np.mean(prices)), 2)
            stats["max_price"] = round(float(np.max(prices)), 2)
            
            changes = np.diff(prices)
            win_days = np.sum(changes > 0)
            stats["win_rate"] = f"{round((win_days / len(changes)) * 100, 2)}%"
            
            # 1. Vẽ biểu đồ phân phối giá
            plt.figure(figsize=(6, 3.8))
            count, bins, ignored = plt.hist(prices, bins=12, edgecolor='black', alpha=0.6, color='#0ea5e9', density=True)
            mu, sigma = np.mean(prices), np.std(prices)
            if sigma > 0:
                xmin, xmax = plt.xlim()
                x = np.linspace(xmin, xmax, 100)
                p = np.exp(-((x - mu)**2 / (2 * sigma**2))) / (sigma * np.sqrt(2 * np.pi))
                plt.plot(x, p, 'k-', linewidth=1.5)
            plt.title("Phân phối giá đóng cửa (365 phiên)", fontsize=10)
            plt.xlabel("Mức giá", fontsize=9)
            plt.ylabel("Tần suất", fontsize=9)
            plt.grid(True, linestyle='--', alpha=0.5)
            plt.tight_layout()
            plt.savefig("static/chart_distribution.png", dpi=150)
            plt.close()

            # 2. Vẽ biểu đồ phân loại xu hướng
            tang_manh = np.sum(changes > 2.0)
            tang = np.sum((changes > 0) & (changes <= 2.0))
            di_ngang = np.sum(changes == 0)
            giam = np.sum((changes < 0) & (changes >= -2.0))
            giam_manh = np.sum(changes < -2.0)
            
            categories = ['Tăng mạnh', 'Tăng', 'Đi ngang', 'Giảm', 'Giảm mạnh']
            counts = [tang_manh, tang, di_ngang, giam, giam_manh]
            colors = ['#22c55e', '#86efac', '#eab308', '#fca5a5', '#ef4444']

            plt.figure(figsize=(6, 3.8))
            plt.bar(categories, counts, color=colors, alpha=0.85, edgecolor='black', linewidth=0.5)
            plt.title("Phân loại phiên giao dịch theo biên độ", fontsize=10)
            plt.xlabel("Phân loại xu hướng", fontsize=9)
            plt.ylabel("Số phiên", fontsize=9)
            plt.grid(True, linestyle='--', alpha=0.5, axis='y')
            plt.tight_layout()
            plt.savefig("static/chart_classification.png", dpi=150)
            plt.close()
except Exception as e:
    print("Lỗi xử lý dữ liệu hoặc vẽ biểu đồ:", e)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(request, "index.html", {"stats": stats})

@app.get("/health")
async def health():
    return {"status": "ok"}