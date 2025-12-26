# ui/visuals.py
import streamlit as st
import plotly.graph_objects as go
import numpy as np
import math

def draw_request_queue(queue, current_idx):
    """Vẽ hàng đợi request nằm ngang"""
    st.markdown("##### 📥 Request Queue (CPU)")
    
    st.markdown("""
    <style>
    .req-box {
        display: inline-block;
        width: 30px; height: 30px;
        line-height: 30px; text-align: center;
        margin: 2px;
        border-radius: 4px; font-weight: bold; font-size: 14px;
        border: 1px solid #ddd;
    }
    .req-active {
        background-color: #FF4B4B; color: white;
        border: 2px solid #333; transform: scale(1.15);
        box-shadow: 0px 2px 5px rgba(0,0,0,0.2);
    }
    .req-waiting { background-color: #f0f2f6; color: #31333F; }
    .req-done { background-color: #e0e0e0; color: #a0a0a0; text-decoration: line-through; }
    </style>
    """, unsafe_allow_html=True)

    html_str = "<div>"
    for i, num in enumerate(queue):
        if i < current_idx: cls = "req-done"
        elif i == current_idx: cls = "req-active"
        else: cls = "req-waiting"
        html_str += f'<div class="req-box {cls}">{num}</div>'
    html_str += "</div>"
    st.markdown(html_str, unsafe_allow_html=True)


def draw_metrics(hits, misses):
    """Hiển thị số đếm Hit/Miss và Tỉ lệ Miss - Đã sửa lỗi hiển thị code"""
    total = hits + misses
    miss_rate = (misses / total * 100) if total > 0 else 0.0
    
    # Lưu chuỗi HTML vào biến và viết sát lề để tránh lỗi Markdown code-block
    html_content = f"""
    <div style="display: flex; gap: 20px; margin-top: 15px; padding: 15px; background-color: #f1f3f6; border-radius: 8px; border: 1px solid #e0e0e0; justify-content: space-around; font-family: sans-serif;">
        <div style="text-align: center;">
            <div style="font-size: 14px; color: #555;">Hit Count</div>
            <div style="font-size: 24px; font-weight: bold; color: #28a745;">{hits}</div>
        </div>
        <div style="border-left: 1px solid #ccc;"></div>
        <div style="text-align: center;">
            <div style="font-size: 14px; color: #555;">Miss Count</div>
            <div style="font-size: 24px; font-weight: bold; color: #dc3545;">{misses}</div>
        </div>
        <div style="border-left: 1px solid #ccc;"></div>
        <div style="text-align: center;">
            <div style="font-size: 14px; color: #555;">Miss Rate</div>
            <div style="font-size: 24px; font-weight: bold; color: #FF4B4B;">{miss_rate:.1f}%</div>
        </div>
    </div>
    """
    st.markdown(html_content, unsafe_allow_html=True)


def draw_linear_cache_with_evicted(data, evicted_val, algo_name, capacity, description):
    """Vẽ cache tuyến tính + Mô tả"""
    st.markdown(f"##### 🗃️ Cache State ({algo_name})")
    st.markdown(f"*{description}*") # Dùng markdown in nghiêng cho mô tả

    col_cache, col_trash = st.columns([3, 1])

    with col_cache:
        cols = st.columns(capacity)
        for i in range(capacity):
            with cols[i]:
                if i < len(data):
                    item = data[i]
                    if isinstance(item, dict) and 'freq' in item:
                        txt = f"**{item['val']}**\n\n*(f:{item['freq']})*"
                    else:
                        txt = f"**{item}**"
                    st.info(txt)
                else:
                    st.markdown("""<div style="height: 60px; border: 2px dashed #ccc; border-radius: 5px; display: flex; align-items: center; justify-content: center; color: #ccc;">Empty</div>""", unsafe_allow_html=True)

    with col_trash:
        if evicted_val is not None:
            box_html = f"""
            <div style="display: flex; flex-direction: column; align-items: center;">
                <div style="
                    width: 60px; height: 60px; 
                    border: 3px solid #FF4B4B; 
                    background-color: #ffe6e6;
                    border-radius: 8px; 
                    display: flex; align-items: center; justify-content: center; 
                    font-weight: bold; font-size: 20px; color: #FF4B4B;
                    margin-bottom: 5px;">
                    {evicted_val}
                </div>
                <div style="font-size: 14px; color: #FF4B4B; font-weight: bold;">🗑️ Evicted</div>
            </div>
            """
        else:
            box_html = """
            <div style="display: flex; flex-direction: column; align-items: center;">
                <div style="width: 60px; height: 60px; border: 1px dashed #ccc; border-radius: 8px; margin-bottom: 5px;"></div>
                <div style="font-size: 14px; color: #ccc;">🗑️ Evicted</div>
            </div>
            """
        st.markdown(box_html, unsafe_allow_html=True)

def draw_clock_plotly(cache_items, hand_idx, capacity, evicted_val, description):
    """
    Vẽ đồng hồ phong cách Modern UI (Clean, Flat design)
    - Font: Sans-serif (giống Metrics)
    - Box: Nền #f1f3f6, Viền đen
    - Text: Xanh (b=1) / Đỏ (b=0)
    """
    
    # 1. Header & Description
    st.markdown(f"##### 🗃️ Cache State (CLOCK)")
    st.markdown(f"*{description}*")
    
    # Tính góc chia đều
    angles = np.linspace(0, 360, capacity, endpoint=False)
    
    # --- Cấu hình Màu sắc Modern ---
    BG_METRIC_COLOR = "#f1f3f6" # Màu nền giống thanh Metrics
    SKY_BLUE        = "#0099FF" # Màu xanh da trời cho bit 1
    RED_HIGHLIGHT   = "#FF4B4B" # Màu đỏ cho bit 0
    BORDER_COLOR    = "#333333" # Màu viền đen (không quá đậm để tinh tế hơn)
    
    # --- Chuẩn bị dữ liệu ---
    r_values = []      
    theta_values = []  
    text_labels = []   
    marker_colors = [] 
    
    for i in range(capacity):
        item = cache_items[i]
        
        # Đẩy ô ra xa tâm một chút cho thoáng (0.8)
        r_values.append(0.8) 
        theta_values.append(angles[i])
        
        if item['val'] is None:
            # Ô trống: Màu trắng hoặc trong suốt
            marker_colors.append("white")
            text_labels.append("")
        else:
            val = item['val']
            bit = item['bit']
            
            # 2. Ô có dữ liệu: Nền xám nhạt (#f1f3f6)
            marker_colors.append(BG_METRIC_COLOR)
            
            # 3. Logic màu chữ: Xanh nếu b=1, Đỏ nếu b=0
            # Dùng font-family: sans-serif để giống thanh metrics
            txt_color = SKY_BLUE if bit == 1 else RED_HIGHLIGHT
            
            label_html = (
                f"<span style='font-family: sans-serif; color: {txt_color}'>"
                f"<b style='font-size: 18px'>{val}</b><br>"
                f"<span style='font-size: 12px'>b={bit}</span>"
                f"</span>"
            )
            text_labels.append(label_html)

    fig = go.Figure()

    # --- Lớp 1: Vẽ Kim (Hand) ---
    if len(cache_items) > 0:
        current_angle = angles[hand_idx]
        
        # Vẽ kim chỉ
        fig.add_trace(go.Scatterpolar(
            r=[0, 0.7], # Kim dài vừa phải chạm mép ô
            theta=[current_angle, current_angle],
            mode='lines',
            line=dict(color=BORDER_COLOR, width=4), # Kim màu đen, mỏng hơn chút cho hiện đại
            hoverinfo='skip'
        ))
        
        # Vẽ tâm đồng hồ
        fig.add_trace(go.Scatterpolar(
            r=[0], theta=[0], mode='markers',
            marker=dict(color=BORDER_COLOR, size=8),
            hoverinfo='skip'
        ))

    # --- Lớp 2: Các ô chứa số (Modern Box) ---
    fig.add_trace(go.Scatterpolar(
        r=r_values,
        theta=theta_values,
        mode='markers+text',
        text=text_labels,
        marker=dict(
            symbol='square',         # Hình vuông
            size=55,                 # Kích thước to hơn để chứa số thoáng
            color=marker_colors,     # Màu nền #f1f3f6
            line=dict(color='black', width=1.5) # Viền đen
            # Lưu ý: Plotly markers chưa hỗ trợ border-radius (bo góc)
        ),
        hoverinfo='skip'
    ))

    # --- Cấu hình Layout ---
    fig.update_layout(
        template=None,
        paper_bgcolor='white',
        polar = dict(
            radialaxis = dict(visible=False, range=[0, 1]),
            angularaxis = dict(
                direction = "clockwise", 
                rotation = 90,           
                showticklabels = False,  
                showgrid = False,        
                showline = False         
            ),
            bgcolor = 'white'
        ),
        margin=dict(l=20, r=20, t=20, b=20),
        height=350,
        showlegend=False
    )

    col1, col2 = st.columns([2, 1])
    with col1:
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False, 'staticPlot': True})
    with col2:
        # Cập nhật Box Evicted cho cùng style (Nền xám, Chữ đỏ, Viền đen)
        if evicted_val is not None:
             box_html = f"""
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%;">
                <div style="
                    width: 60px; height: 60px; 
                    border: 2px solid #333; 
                    background-color: #f1f3f6; /* Nền giống metrics */
                    border-radius: 10px;       /* Bo góc được vì đây là HTML */
                    display: flex; align-items: center; justify-content: center; 
                    font-family: sans-serif;
                    font-weight: bold; font-size: 20px; color: #FF4B4B; /* Chữ đỏ */
                    margin-bottom: 5px;">
                    {evicted_val}
                </div>
                <div style="font-size: 14px; color: #FF4B4B; font-weight: bold; font-family: sans-serif;">🗑️ Evicted</div>
            </div>
            """
        else:
            box_html = """
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%;">
                <div style="width: 60px; height: 60px; border: 1px dashed #ccc; border-radius: 10px; margin-bottom: 5px;"></div>
                <div style="font-size: 14px; color: #ccc; font-family: sans-serif;">🗑️ Evicted</div>
            </div>
            """
        st.markdown(box_html, unsafe_allow_html=True)

def draw_clock_svg(cache_items, hand_idx, capacity, evicted_val, description):
    """
    Vẽ đồng hồ bằng SVG.
    FIX: Xóa bỏ indentation (thụt đầu dòng) trong chuỗi HTML để tránh lỗi Markdown hiển thị code text.
    """
    # Hiển thị tiêu đề
    st.markdown(f"##### 🗃️ Cache State (CLOCK)")
    st.markdown(f"*{description}*")
    
    # Cấu hình kích thước canvas SVG
    width, height = 400, 320
    cx, cy = width / 2, height / 2  # Tâm đồng hồ
    radius = 110                    # Bán kính vòng tròn
    box_size = 60                   # Kích thước ô vuông
    
    # Cấu hình màu sắc
    COLOR_BOX_BG = "#f1f3f6"      
    COLOR_BOX_BORDER = "#333333" 
    COLOR_TEXT_BLUE = "#0099FF"   
    COLOR_TEXT_RED = "#FF4B4B"    
    COLOR_HAND = "#333333"        
    
    svg_content = ""
    
    # 1. Vẽ các ô nhớ (Rounded Rectangles)
    angle_step = 360 / capacity
    
    for i in range(capacity):
        angle_deg = i * angle_step
        angle_rad = math.radians(angle_deg)
        
        # Tọa độ tâm ô vuông
        x = cx + radius * math.sin(angle_rad)
        y = cy - radius * math.cos(angle_rad)
        
        item = cache_items[i]
        
        if item['val'] is None:
            # Ô trống
            svg_content += f'<rect x="{x - box_size/2}" y="{y - box_size/2}" width="{box_size}" height="{box_size}" rx="10" ry="10" fill="white" stroke="#e0e0e0" stroke-width="2" />'
        else:
            # Ô có dữ liệu
            val = item['val']
            bit = item['bit']
            text_fill = COLOR_TEXT_BLUE if bit == 1 else COLOR_TEXT_RED
            
            # Vẽ Box và Text (viết liền 1 dòng để tránh lỗi hiển thị)
            svg_content += f'<rect x="{x - box_size/2}" y="{y - box_size/2}" width="{box_size}" height="{box_size}" rx="10" ry="10" fill="{COLOR_BOX_BG}" stroke="{COLOR_BOX_BORDER}" stroke-width="2" />'
            svg_content += f'<text x="{x}" y="{y}" fill="{text_fill}" font-family="sans-serif" text-anchor="middle" dominant-baseline="middle">'
            svg_content += f'<tspan x="{x}" dy="-5" font-weight="bold" font-size="20">{val}</tspan>'
            svg_content += f'<tspan x="{x}" dy="20" font-size="12">b={bit}</tspan></text>'

    # 2. Vẽ Kim đồng hồ (Arrow)
    if len(cache_items) > 0:
        hand_angle_deg = hand_idx * angle_step
        hand_rad = math.radians(hand_angle_deg)
        
        # 1. Tính tọa độ ĐỈNH NHỌN của mũi tên (giữ nguyên)
        hand_len = radius - 42 
        tip_x = cx + hand_len * math.sin(hand_rad)
        tip_y = cy - hand_len * math.cos(hand_rad)
        
        # 2. Tính tọa độ điểm kết thúc của THÂN KIM (ngắn hơn đỉnh 10px)
        # Để thân kim chui vào trong tam giác chứ không lòi ra ngoài đỉnh
        stick_len = hand_len - 10 
        stick_end_x = cx + stick_len * math.sin(hand_rad)
        stick_end_y = cy - stick_len * math.cos(hand_rad)
        
        # 3. Tính toán 2 cánh của mũi tên (dựa trên đỉnh tip_x, tip_y)
        arrow_size = 12
        p1_x = tip_x - arrow_size * math.sin(hand_rad - math.pi/6)
        p1_y = tip_y + arrow_size * math.cos(hand_rad - math.pi/6)
        p2_x = tip_x - arrow_size * math.sin(hand_rad + math.pi/6)
        p2_y = tip_y + arrow_size * math.cos(hand_rad + math.pi/6)
        
        # VẼ:
        # - Line: vẽ từ tâm đến stick_end (điểm ngắn hơn)
        # - Polygon: vẫn vẽ tại tip (đỉnh nhọn)
        svg_content += f'<line x1="{cx}" y1="{cy}" x2="{stick_end_x}" y2="{stick_end_y}" stroke="{COLOR_HAND}" stroke-width="4" stroke-linecap="round" />'
        svg_content += f'<polygon points="{tip_x},{tip_y} {p1_x},{p1_y} {p2_x},{p2_y}" fill="{COLOR_HAND}" />'
        svg_content += f'<circle cx="{cx}" cy="{cy}" r="6" fill="{COLOR_HAND}" />'

    # Tạo chuỗi HTML cuối cùng (Lưu ý: Không xuống dòng, không thụt lề)
    full_html = f'<div style="display: flex; justify-content: center; background-color: white; border-radius: 10px; padding: 10px; border: 1px solid #ddd;"><svg width="{width}" height="{height}" viewBox="0 0 {width} {height}">{svg_content}</svg></div>'

    # --- Render ---
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(full_html, unsafe_allow_html=True)
        
    with col2:
        # Phần Evicted Box (cũng viết gọn lại)
        if evicted_val is not None:
             box_html = f'<div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%;"><div style="width: 60px; height: 60px; border: 2px solid #333; background-color: #f1f3f6; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-family: sans-serif; font-weight: bold; font-size: 20px; color: #FF4B4B; margin-bottom: 5px;">{evicted_val}</div><div style="font-size: 14px; color: #FF4B4B; font-weight: bold; font-family: sans-serif;">🗑️ Evicted</div></div>'
        else:
            box_html = '<div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%;"><div style="width: 60px; height: 60px; border: 1px dashed #ccc; border-radius: 12px; margin-bottom: 5px;"></div><div style="font-size: 14px; color: #ccc; font-family: sans-serif;">🗑️ Evicted</div></div>'
        
        st.markdown(box_html, unsafe_allow_html=True)