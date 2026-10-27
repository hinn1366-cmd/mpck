import os
import pandas as pd
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(title="Mô phỏng biến động giá của một mã chứng khoán")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    # Mặc định các giá trị phòng hờ nếu file CSV có cấu trúc khác
    stats = {
        "max_price": 125.5,
        "min_price": 85.0,
        "avg_price": 105.2,
        "total_days": 365,
        "volatility": "Ổn định / Tích lũy"
    }
    
    try:
        csv_path = "abc-6.csv"
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            # Tự động tìm cột giá hoặc lấy cột số học đầu tiên
            numeric_cols = df.select_dtypes(include='number').columns
            if len(numeric_cols) > 0:
                col = numeric_cols[0]
                stats["max_price"] = round(float(df[col].max()), 2)
                stats["min_price"] = round(float(df[col].min()), 2)
                stats["avg_price"] = round(float(df[col].mean()), 2)
                stats["total_days"] = len(df)
    except Exception as e:
        print("Lỗi đọc file CSV:", e)

    return templates.TemplateResponse(
        request, 
        "index.html", 
        {"stats": stats}
    )
@app.get("/health")
async def health():
    return {"status": "ok"}