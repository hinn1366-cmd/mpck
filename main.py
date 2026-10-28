import os
import matplotlib
matplotlib.use('Agg') # Ép Matplotlib chạy ngầm không cần màn hình
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Khởi tạo FastAPI
app = FastAPI(title="Phân tích biến động giá chứng khoán theo tháng")

os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Nội dung nhận xét ngắn gọn cho 2 biểu đồ Câu 1
comments = {
    "cmt_mean": "Biểu đồ cột phản ánh giá trung bình qua các tháng, giúp nhận diện nhanh chóng chu kỳ tăng giảm và xu thế dịch chuyển của dòng tiền trong năm.",
    "cmt_boxplot": "Biểu đồ hộp (Boxplot) thể hiện độ phân tán và khoảng tứ phân vị của giá theo từng tháng. Râu hộp kéo dài và các điểm ngoại lệ cho thấy những phiên có biến động mạnh."
}

# Đọc dữ liệu và tự động vẽ 2 biểu đồ Câu 1 khi khởi động
csv_path = "abc-6.csv"
if os.path.exists(csv_path):
    try:
        df_raw = pd.read_csv(csv_path, header=None)
        dates = pd.date_range(start="2024-01-01", periods=len(df_raw), freq="B")
        df = df_raw.copy()
        df.insert(0, "Date", dates)
        df["Month"] = df["Date"].dt.month
        df["Daily_Mean"] = df_raw.mean(axis=1)

        # Tính toán giá trung bình theo tháng
        monthly_stats = df.groupby("Month")["Daily_Mean"].agg(
            Gia_Trung_Binh="mean", Do_Lech_Chuan="std"
        ).round(2)

        # --- BIỂU ĐỒ 1: Biểu đồ cột giá trung bình mỗi tháng ---
        plt.figure(figsize=(7, 4))
        monthly_stats["Gia_Trung_Binh"].plot(kind="bar", color="#0ea5e9", edgecolor="black", alpha=0.85)
        plt.title("Gia trung binh cac thang trong nam", fontsize=11, fontweight="bold")
        plt.xlabel("Thang", fontsize=10)
        plt.ylabel("Gia trung binh (VND)", fontsize=10)
        plt.grid(True, linestyle="--", alpha=0.5, axis="y")
        plt.xticks(rotation=0)
        plt.tight_layout()
        plt.savefig("static/chart_monthly_mean.png", dpi=150)
        plt.close()

        # --- BIỂU ĐỒ 2: Biểu đồ hộp (Boxplot) theo tháng ---
        plt.figure(figsize=(8, 4))
        df_melted = df_raw.copy()
        df_melted["Month"] = dates.month
        df_long = df_melted.melt(id_vars=["Month"], value_vars=df_raw.columns, var_name="Price_Point", value_name="Price")
        
        sns.boxplot(x="Month", y="Price", data=df_long, palette="Set2", showmeans=True)
        plt.title("Boxplot phan phoi gia theo tung thang", fontsize=11, fontweight="bold")
        plt.xlabel("Thang", fontsize=10)
        plt.ylabel("Muc gia (VND)", fontsize=10)
        plt.grid(True, linestyle="--", alpha=0.5)
        plt.tight_layout()
        plt.savefig("static/chart_monthly_boxplot.png", dpi=150)
        plt.close()

    except Exception as e:
        print(f"Lỗi xử lý biểu đồ Câu 1: {e}")

# Định tuyến trang chủ hiển thị Video + 2 biểu đồ Câu 1 kèm nhận xét
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request, 
        "index.html", 
        {
            "comments": comments
        }
    )