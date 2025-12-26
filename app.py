# # app.py
# import streamlit as st
# import random
# from core.algorithms import FIFO, LIFO, LRU, LFU, CLOCK
# # Import hàm metrics
# from ui.visuals import draw_request_queue, draw_linear_cache_with_evicted, draw_clock_plotly, draw_metrics, draw_clock_svg

# # --- Cấu hình ---
# st.set_page_config(page_title="Paging Algorithm", layout="centered") 
# st.title("💾 Paging Algorithm Simulator")

# # --- 4. TỪ ĐIỂN MÔ TẢ THUẬT TOÁN ---
# ALGO_DESCRIPTIONS = {
#     "FIFO": "Page vào cache sớm nhất → bị xóa",
#     "LIFO": "Page vào sau cùng → bị xóa",
#     "LRU": "Page lâu nhất chưa được dùng → bị xóa",
#     "LFU": "Page nào được dùng ít lần nhất → bị xóa",
#     "CLOCK": 'Cải tiến của LRU - Bit = 0 → bị xóa, Bit = 1 → 0, cho page một "cơ hội thứ hai"'
# }

# # --- 1. Sidebar ---
# with st.sidebar:
#     st.header("Cài đặt")
#     new_algo = st.selectbox("Thuật toán", list(ALGO_DESCRIPTIONS.keys()))
#     new_capacity = st.slider("Kích thước Cache", 3, 6, 3) 

# # State Management
# if 'config' not in st.session_state:
#     st.session_state.config = {'algo': new_algo, 'cap': new_capacity}
#     # Sinh 15 request
#     st.session_state.requests = [random.randint(1, 10) for _ in range(15)] 
#     st.session_state.step = 0 

# # Detect Change -> Auto Reset
# if (st.session_state.config['algo'] != new_algo) or (st.session_state.config['cap'] != new_capacity):
#     st.session_state.config = {'algo': new_algo, 'cap': new_capacity}
#     st.session_state.step = 0
#     st.rerun()

# # --- Helper ---
# def simulate_up_to_step(algo_name, capacity, requests, target_step):
#     if algo_name == "FIFO": algo = FIFO(capacity)
#     elif algo_name == "LIFO": algo = LIFO(capacity)
#     elif algo_name == "LRU": algo = LRU(capacity)
#     elif algo_name == "LFU": algo = LFU(capacity)
#     elif algo_name == "CLOCK": algo = CLOCK(capacity)
    
#     last_status = None
#     last_evicted = None
    
#     for i in range(target_step):
#         page = requests[i]
#         last_status, last_evicted = algo.access(page)
        
#     return algo, last_status, last_evicted

# # --- 2. Giao diện chính ---

# requests = st.session_state.requests
# current_step = st.session_state.step
# # Vẽ queue
# draw_request_queue(requests, current_step - 1 if current_step > 0 else -1)

# # --- Helper: Khởi tạo hoặc lấy lại Algorithm Instance ---
# def get_algo_instance(algo_name, capacity):
#     # Nếu chưa có hoặc đổi cài đặt thì tạo mới
#     if 'algo_instance' not in st.session_state or \
#        st.session_state.config['algo'] != algo_name or \
#        st.session_state.config['cap'] != capacity:
        
#         if algo_name == "FIFO": instance = FIFO(capacity)
#         elif algo_name == "LIFO": instance = LIFO(capacity)
#         elif algo_name == "LRU": instance = LRU(capacity)
#         elif algo_name == "LFU": instance = LFU(capacity)
#         elif algo_name == "CLOCK": instance = CLOCK(capacity)
        
#         st.session_state.algo_instance = instance
#         st.session_state.last_status = (None, None)
#     return st.session_state.algo_instance

# # --- Xử lý Logic ---
# algo_instance = get_algo_instance(new_algo, new_capacity)
# requests = st.session_state.requests
# current_step = st.session_state.step

# st.write("---")

# # B. Controls
# col_ctrl1, col_ctrl2, col_ctrl3 = st.columns(3)

# # with col_ctrl1:
# #     if st.button("🔄 Random", use_container_width=True):
# #         st.session_state.step = 0
# #         # CẬP NHẬT: Reset cũng sinh lại 15 request
# #         st.session_state.requests = [random.randint(1, 10) for _ in range(15)]
# #         st.rerun()

# with col_ctrl1:
#     if st.button("🔄 Random", use_container_width=True):
#         st.session_state.step = 0
#         st.session_state.requests = [random.randint(1, 10) for _ in range(15)]
#         # Xóa instance cũ để tạo mới
#         if 'algo_instance' in st.session_state: del st.session_state.algo_instance
#         st.rerun()

# with col_ctrl2:
#     if st.button("⬅️ Prev", disabled=(current_step == 0), use_container_width=True):
#         st.session_state.step -= 1
#         st.rerun()

# # with col_ctrl3:
# #     # Disable khi >= 15
# #     if st.button("Next ➡️", disabled=(current_step >= 15), use_container_width=True, type="primary"):
# #         st.session_state.step += 1
# #         st.rerun()

# with col_ctrl3:
#     # Nút Next xử lý logic "từng bước"
#     if st.button("Next ➡️", disabled=(current_step >= 15), use_container_width=True, type="primary"):
#         if current_step < 15:
#             page = requests[current_step]
#             status, evicted = algo_instance.access(page)
#             st.session_state.last_status = (status, evicted)
            
#             # NẾU KHÔNG PHẢI LÀ BƯỚC QUÉT TRUNG GIAN CỦA CLOCK THÌ MỚI TĂNG STEP
#             if status != "STEP":
#                 st.session_state.step += 1
#             st.rerun()

# # C. Xử lý Logic & Hiển thị kết quả
# # Lấy mô tả thuật toán
# current_desc = ALGO_DESCRIPTIONS[new_algo]

# if current_step > 0:
#     algo_instance, status, evicted = simulate_up_to_step(
#         new_algo, new_capacity, requests, current_step
#     )
    
#     current_page = requests[current_step - 1]
    
#     # Thông báo trạng thái
#     st.markdown(f"**Step {current_step}:** CPU request **{current_page}**")
#     if status == "HIT":
#         st.success(f"HIT! Trang {current_page} đã có trong Cache.", icon="✅")
#     else:
#         msg = f"MISS! Đưa {current_page} vào Cache."
#         if evicted is not None:
#             msg += f" Cache đầy -> Loại bỏ **{evicted}**."
#         st.error(msg, icon="❌")

#     # Visualization
#     cache_data = algo_instance.get_cache_state()
    
#     if new_algo == "CLOCK":
#         # 3. & 4. Truyền description vào Clock
#         draw_clock_svg(cache_data, algo_instance.hand, new_capacity, evicted, current_desc)
#     else:
#         # 4. Truyền description vào Linear Cache
#         draw_linear_cache_with_evicted(cache_data, evicted, new_algo, new_capacity, current_desc)
    
#     # 2. Hiển thị Metrics (Hit, Miss, Miss Rate)
#     draw_metrics(algo_instance.hits, algo_instance.misses)
        
# else:
#     st.info("Nhấn 'Next' để bắt đầu mô phỏng.")
#     if new_algo == "CLOCK":
#         dummy_algo = CLOCK(new_capacity)
#         draw_clock_svg(dummy_algo.frames, 0, new_capacity, None, current_desc)
#     else:
#         draw_linear_cache_with_evicted([], None, new_algo, new_capacity, current_desc)
        
#     draw_metrics(0, 0)

# # Chú thích cuối trang
# st.write("")
# st.caption(f"Algorithm: {new_algo} | Cache Size: {new_capacity}")

import streamlit as st
import random
import copy # Cần để copy trạng thái object
from core.algorithms import FIFO, LIFO, LRU, LFU, CLOCK
from ui.visuals import draw_request_queue, draw_linear_cache_with_evicted, draw_metrics, draw_clock_svg

st.set_page_config(page_title="Paging Algorithm", layout="centered") 
st.title("💾 Paging Algorithm Simulator")

ALGO_DESCRIPTIONS = {
    "FIFO": "Page vào cache sớm nhất → bị xóa",
    "LIFO": "Page vào sau cùng → bị xóa",
    "LRU": "Page lâu nhất chưa được dùng → bị xóa",
    "LFU": "Page nào được dùng ít lần nhất → bị xóa",
    "CLOCK": 'Cải tiến của LRU: Bit = 1 → hạ xuống 0 (Cơ hội thứ hai), Bit = 0 → Thay thế.'
}

# --- 1. Sidebar ---
with st.sidebar:
    st.header("Cài đặt")
    new_algo = st.selectbox("Thuật toán", list(ALGO_DESCRIPTIONS.keys()))
    new_capacity = st.slider("Kích thước Cache", 3, 6, 3) 

# --- 2. Khởi tạo / Reset State ---
if 'config' not in st.session_state or \
   st.session_state.config['algo'] != new_algo or \
   st.session_state.config['cap'] != new_capacity:
    
    st.session_state.config = {'algo': new_algo, 'cap': new_capacity}
    st.session_state.requests = [random.randint(1, 10) for _ in range(15)] 
    st.session_state.step = 0
    
    # Khởi tạo instance
    if new_algo == "FIFO": instance = FIFO(new_capacity)
    elif new_algo == "LIFO": instance = LIFO(new_capacity)
    elif new_algo == "LRU": instance = LRU(new_capacity)
    elif new_algo == "LFU": instance = LFU(new_capacity)
    elif new_algo == "CLOCK": instance = CLOCK(new_capacity)
    
    st.session_state.algo_instance = instance
    st.session_state.last_status = (None, None)
    # QUAN TRỌNG: Lưu lịch sử trạng thái
    st.session_state.history = [] 
    st.rerun()

# --- 3. Giao diện chính ---
requests = st.session_state.requests
current_step = st.session_state.step
algo_instance = st.session_state.algo_instance
status, evicted = st.session_state.last_status

draw_request_queue(requests, current_step)
st.write("---")

# B. Controls
col_ctrl1, col_ctrl2, col_ctrl3 = st.columns(3)

with col_ctrl1:
    if st.button("🔄 Random", use_container_width=True):
        del st.session_state.config
        st.rerun()

with col_ctrl2:
    # --- LOGIC NÚT PREV ---
    if st.button("⬅️ Prev", disabled=(not st.session_state.history), use_container_width=True):
        # Lấy trạng thái cũ nhất từ history
        prev_state = st.session_state.history.pop()
        
        st.session_state.algo_instance = prev_state['instance']
        st.session_state.step = prev_state['step']
        st.session_state.last_status = prev_state['last_status']
        st.rerun()

with col_ctrl3:
    # --- LOGIC NÚT NEXT ---
    if st.button("Next ➡️", disabled=(current_step >= 15), use_container_width=True, type="primary"):
        # Lưu lại trạng thái HIỆN TẠI vào history trước khi thực hiện bước mới
        current_snapshot = {
            'instance': copy.deepcopy(algo_instance),
            'step': st.session_state.step,
            'last_status': st.session_state.last_status
        }
        st.session_state.history.append(current_snapshot)
        
        # Thực hiện bước tiếp theo
        page = requests[current_step]
        res_status, res_evicted = algo_instance.access(page)
        st.session_state.last_status = (res_status, res_evicted)
        
        if res_status != "STEP":
            st.session_state.step += 1
        st.rerun()

# C. Hiển thị kết quả (Giữ nguyên logic cũ)
current_desc = ALGO_DESCRIPTIONS[new_algo]
if status is not None:
    current_page = requests[current_step if status == "STEP" else current_step - 1]
    if status == "STEP":
        st.warning(f"**CLOCK Scanning:** Đang hạ bit trang tại kim chỉ. CPU đợi **{current_page}**", icon="🔄")
    elif status == "HIT":
        st.success(f"**Step {current_step}:** HIT trang **{current_page}**", icon="✅")
    else:
        msg = f"**Step {current_step}:** MISS trang **{current_page}**."
        if evicted: msg += f" Loại bỏ **{evicted}**."
        st.error(msg, icon="❌")

# Visualization
cache_data = algo_instance.get_cache_state()
if new_algo == "CLOCK":
    draw_clock_svg(cache_data, algo_instance.hand, new_capacity, evicted, current_desc)
else:
    draw_linear_cache_with_evicted(cache_data, evicted, new_algo, new_capacity, current_desc)

draw_metrics(algo_instance.hits, algo_instance.misses)