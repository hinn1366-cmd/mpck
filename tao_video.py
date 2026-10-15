import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


# 1. ĐỌC DỮ LIỆU
df = pd.read_csv("abc-6.csv", header=None)
gia = df.to_numpy(dtype=float)

so_ngay = gia.shape[0]  # 365 ngày
so_gia = gia.shape[1]   # 7 mức giá trong ngày

print("Kích thước dữ liệu:", gia.shape)


# 2. TÍNH GIÁ THAM CHIẾU
gia_tham_chieu = np.zeros(so_ngay)
gia_tham_chieu[0] = 10000  # Giá tham chiếu mốc khởi đầu ngày đầu tiên
gia_tham_chieu[1:] = gia[:-1, -1]  # Từ ngày thứ 2: lấy giá đóng cửa ngày liền trước


# 3. TÍNH GIÁ SÀN VÀ GIÁ TRẦN
gia_san = 0.90 * gia_tham_chieu     # Sàn -10%
gia_tran = 1.10 * gia_tham_chieu    # Trần +10%


# 4. HÀM XÁC ĐỊNH MÀU THEO ĐỀ BÀI
def xac_dinh_mau(p, tham_chieu, san, tran):
    if np.isclose(p, san):
        return "deepskyblue"  # Sàn: xanh dương
    elif np.isclose(p, tran):
        return "purple"       # Trần: tím
    elif np.isclose(p, tham_chieu):
        return "yellow"       # Tham chiếu: vàng
    elif p < tham_chieu:
        return "red"          # Nhỏ hơn tham chiếu: đỏ
    else:
        return "lime"         # Lớn hơn tham chiếu: xanh lá


# 5. TẠO BỐ CỤC BIỂU ĐỒ
plt.style.use("dark_background")

fig, (ax1, ax2) = plt.subplots(
    2, 1, figsize=(10, 6), sharex=True
)

fig.subplots_adjust(hspace=0.12)

gia_min = np.min(gia_san) * 0.95
gia_max = np.max(gia_tran) * 1.05

for ax in (ax1, ax2):
    ax.set_xlim(0.5, so_ngay + 5)
    ax.set_ylim(gia_min, gia_max)
    ax.grid(True, alpha=0.25)

ax2.set_xlabel("Date")
for ax in (ax1, ax2):
    ax.set_ylabel("VND")


# 6. BIỂU ĐỒ TRÊN: THANH NẾN GIAO DỊCH TRONG NGÀY
ax1.tick_params(axis="x", bottom=False, labelbottom=False)
ax1.set_title("Mô phỏng 7 mức giá giao dịch trong ngày")


# 7. BIỂU ĐỒ DƯỚI: GIÁ ĐÓNG CỬA VÀ KHUNG GIÁ (NÉT LIỀN ĐẬM RÕ NÉT NHƯ MẪU THẦY)
ax2.set_xticks(np.arange(0, so_ngay + 1, 30))
ax2.set_title("Giá đóng cửa và khung giá")

line_close, = ax2.plot(
    [], [], color="#a8b832",
    linewidth=2.5, label="Giá đóng cửa"
)

line_ref, = ax2.plot(
    [], [], color="yellow",
    linewidth=2.0, alpha=1.0, linestyle="-", label="Giá tham chiếu"  # Đổi sang nét liền, đậm rõ
)

line_floor, = ax2.plot(
    [], [], color="deepskyblue",
    linewidth=2.0, alpha=1.0, linestyle="-", label="Giá sàn"  # Đổi sang nét liền, sáng rõ trên nền tối
)

line_ceiling, = ax2.plot(
    [], [], color="purple",
    linewidth=2.0, alpha=1.0, linestyle="-", label="Giá trần"  # Đổi sang nét liền, màu tím nổi bật
)

ax2.legend(loc="upper right", fontsize=8)
text_val = ax2.text(0, 0, "", fontsize=9, va="center")


# 8. HÀM CẬP NHẬT TỪNG NGÀY (VẼ NẾN TÍCH LŨY)
def animate(i):
    ref = gia_tham_chieu[i]
    san = gia_san[i]
    tran = gia_tran[i]

    # Lấy 7 giá của ngày thứ i
    ngay_gia = gia[i, :]
    mo_cua = ngay_gia[0]
    dong_cua = ngay_gia[-1]
    thap_nhat = np.min(ngay_gia)
    cao_nhat = np.max(ngay_gia)

    # Xác định màu nến dựa trên giá đóng cửa so với tham chiếu/sàn/trần
    mau_nen = xac_dinh_mau(dong_cua, ref, san, tran)

    # Vẽ thanh nến (High-Low range) cho ngày i + 1
    x_ngay = i + 1
    ax1.vlines(x=x_ngay, ymin=thap_nhat, ymax=cao_nhat, color=mau_nen, linewidth=2, alpha=0.85)
    
    # Vẽ vạch ngang thể hiện giá mở cửa và đóng cửa
    ax1.hlines(y=mo_cua, xmin=x_ngay - 0.15, xmax=x_ngay, color=mau_nen, linewidth=1.5)
    ax1.hlines(y=dong_cua, xmin=x_ngay, xmax=x_ngay + 0.15, color=mau_nen, linewidth=1.5)

    # Cập nhật lịch sử biểu đồ dưới từ ngày đầu đến ngày hiện tại i
    x_lich_su = np.arange(1, i + 2)
    y_close = gia[:i + 1, -1]

    line_close.set_data(x_lich_su, y_close)
    line_ref.set_data(x_lich_su, gia_tham_chieu[:i + 1])
    line_floor.set_data(x_lich_su, gia_san[:i + 1])
    line_ceiling.set_data(x_lich_su, gia_tran[:i + 1])

    # Cập nhật con số giá trị chạy theo đường giá ở cuối
    current_price = y_close[-1]
    if np.isclose(current_price, ref):
        text_color = "yellow"
    elif current_price > ref:
        text_color = "lime"
    else:
        text_color= "red"
        
    text_val.set_text(f"  {current_price:,.0f}")
    text_val.set_position((x_ngay, current_price))
    text_val.set_color(text_color)

    return (
        line_close, line_ref, line_floor, line_ceiling, text_val
    )


# 9. TẠO ANIMATION
ani = FuncAnimation(
    fig,
    animate,
    frames=so_ngay,
    interval=30,
    blit=False,
    repeat=False
)


# 10. XUẤT VIDEO MP4
print("Đang xuất video ...")

ani.save(
    "mo_phong_chung_khoan.mp4",
    writer="ffmpeg",
    fps=2
)

print("Đã xuất video thành công: mo_phong_chung_khoan.mp4")