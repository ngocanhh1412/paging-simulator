# core/algorithms.py
import collections

class PagingAlgorithm:
    def __init__(self, capacity):
        self.capacity = capacity
        self.hits = 0
        self.misses = 0
        # Snapshot lưu lại kết quả của bước vừa chạy
        self.last_evicted = None 
        self.last_status = None

    def access(self, page):
        """Trả về (status, evicted)"""
        pass

    def get_cache_state(self):
        pass

# --- FIFO, LIFO, LRU, LFU (Giữ nguyên logic cũ, chỉ clean code) ---
class FIFO(PagingAlgorithm):
    def __init__(self, capacity):
        super().__init__(capacity)
        self.cache = collections.deque()

    def access(self, page):
        if page in self.cache:
            self.hits += 1
            return "HIT", None
        
        self.misses += 1
        evicted = None
        if len(self.cache) >= self.capacity:
            evicted = self.cache.popleft()
        
        self.cache.append(page)
        return "MISS", evicted

    def get_cache_state(self):
        return list(self.cache)

class LIFO(PagingAlgorithm):
    def __init__(self, capacity):
        super().__init__(capacity)
        self.cache = []

    def access(self, page):
        if page in self.cache:
            self.hits += 1
            return "HIT", None
        
        self.misses += 1
        evicted = None
        if len(self.cache) >= self.capacity:
            evicted = self.cache.pop()
        
        self.cache.append(page)
        return "MISS", evicted

    def get_cache_state(self):
        return self.cache

class LRU(PagingAlgorithm):
    def __init__(self, capacity):
        super().__init__(capacity)
        self.cache = collections.OrderedDict()

    def access(self, page):
        if page in self.cache:
            self.hits += 1
            self.cache.move_to_end(page)
            return "HIT", None
        
        self.misses += 1
        evicted = None
        if len(self.cache) >= self.capacity:
            evicted, _ = self.cache.popitem(last=False)
        
        self.cache[page] = True
        return "MISS", evicted

    def get_cache_state(self):
        return list(self.cache.keys())

class LFU(PagingAlgorithm):
    def __init__(self, capacity):
        super().__init__(capacity)
        self.cache = {} 
        self.time = {}
        self.timer = 0

    def access(self, page):
        self.timer += 1
        if page in self.cache:
            self.hits += 1
            self.cache[page] += 1
            return "HIT", None
        
        self.misses += 1
        evicted = None
        if len(self.cache) >= self.capacity:
            evicted = min(self.cache, key=lambda k: (self.cache[k], self.time[k]))
            del self.cache[evicted]
            del self.time[evicted]
        
        self.cache[page] = 1
        self.time[page] = self.timer
        return "MISS", evicted

    def get_cache_state(self):
        # Sắp xếp theo thứ tự thêm vào (dựa trên time) để hiển thị ổn định
        sorted_keys = sorted(self.cache.keys(), key=lambda k: self.time[k])
        return [{'val': k, 'freq': self.cache[k]} for k in sorted_keys]

# # --- CLOCK (Logic chuẩn vòng tròn) ---
# class CLOCK(PagingAlgorithm):
#     def __init__(self, capacity):
#         super().__init__(capacity)
#         # Khởi tạo sẵn các slot trống để vẽ vòng tròn cho đẹp ngay từ đầu
#         # frames là list các dict hoặc None
#         self.frames = [{'val': None, 'bit': 0} for _ in range(capacity)]
#         self.hand = 0
#         self.valid_count = 0 # Đếm số phần tử thực sự có giá trị

#     def access(self, page):
#         # 1. Check HIT
#         for i in range(self.capacity):
#             if self.frames[i]['val'] == page:
#                 self.hits += 1
#                 self.frames[i]['bit'] = 1
#                 return "HIT", None
        
#         # 2. MISS
#         self.misses += 1
#         evicted = None
        
#         while True:
#             current = self.frames[self.hand]
            
#             # Nếu slot trống (chưa có giá trị) -> Điền vào luôn
#             if current['val'] is None:
#                 current['val'] = page
#                 current['bit'] = 1
#                 self.hand = (self.hand + 1) % self.capacity
#                 self.valid_count += 1
#                 return "MISS", None
            
#             # Nếu có giá trị, kiểm tra bit
#             if current['bit'] == 1:
#                 current['bit'] = 0 # Give second chance
#                 self.hand = (self.hand + 1) % self.capacity
#             else:
#                 # Bit == 0 -> Replace
#                 evicted = current['val']
#                 current['val'] = page
#                 current['bit'] = 1
#                 self.hand = (self.hand + 1) % self.capacity
#                 return "MISS", evicted

#     def get_cache_state(self):
#         return self.frames

class CLOCK(PagingAlgorithm):
    def __init__(self, capacity):
        super().__init__(capacity)
        self.frames = [{'val': None, 'bit': 0} for _ in range(capacity)]
        self.hand = 0

    def access(self, page):
        # 1. Check HIT
        for i in range(self.capacity):
            if self.frames[i]['val'] == page:
                self.hits += 1
                self.frames[i]['bit'] = 1
                return "HIT", None

        # 2. MISS
        # Lưu ý: Không cộng misses ngay tại đây vì có thể tốn nhiều bước quét
        # Chúng ta sẽ kiểm tra xem vị trí hiện tại có xử lý được luôn không
        
        current = self.frames[self.hand]
        
        # Trường hợp 1: Slot trống -> Điền vào (Xong luôn)
        if current['val'] is None:
            self.misses += 1
            current['val'] = page
            current['bit'] = 1
            self.hand = (self.hand + 1) % self.capacity
            return "MISS", None

        # Trường hợp 2: Có bit 1 -> Hạ xuống 0 và dịch kim (Trả về STEP)
        if current['bit'] == 1:
            current['bit'] = 0 
            self.hand = (self.hand + 1) % self.capacity
            return "STEP", None # Trạng thái trung gian

        # Trường hợp 3: Bit == 0 -> Thay thế (Xong luôn)
        self.misses += 1
        evicted = current['val']
        current['val'] = page
        current['bit'] = 1
        self.hand = (self.hand + 1) % self.capacity
        return "MISS", evicted

    def get_cache_state(self):
        return self.frames