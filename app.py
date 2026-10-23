import streamlit as st
import datetime
import random
import string
import urllib.parse
from streamlit_autorun import autorun

st.set_page_config(page_title="Wi-Fi Quick Chat", page_icon="💬", layout="centered")

# Tự động refresh giao diện mỗi 2000ms (2 giây) để cập nhật tin nhắn mới
autorun(interval=2000, key="chat_auto_refresh")

# 1. Khởi tạo kho lưu trữ tin nhắn trong bộ nhớ tạm (In-memory storage)
if "rooms" not in st.session_state:
    st.session_state.rooms = {}

# 2. Xử lý Room ID từ URL query parameter (?room=xxxx)
query_params = st.query_params
room_id = query_params.get("room", None)

is_sender = False
if not room_id:
    # Nếu chưa có room ID -> Tạo room ID ngẫu nhiên cho người khởi tạo (Bạn)
    room_id = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
    st.query_params["room"] = room_id
    is_sender = True

# Đảm bảo phòng chat tồn tại trong kho dữ liệu
if room_id not in st.session_state.rooms:
    st.session_state.rooms[room_id] = []

st.title("💬 Wi-Fi Quick Chat")

# 3. Khung gửi SMS dành cho người khởi tạo
if is_sender:
    with st.expander("📱 Gửi link mời qua SMS cho số điện thoại", expanded=True):
        phone_number = st.text_input("Nhập số điện thoại người nhận:", placeholder="Ví dụ: 0987654321")
        
        # Link hiện tại của ứng dụng Streamlit
        current_url = f"http://localhost:8501/?room={room_id}" # Thay localhost bằng IP LAN hoặc domain khi public
        sms_text = f"Chào bạn, bấm vào link này để chat trực tiếp qua Wi-Fi nhé: {current_url}"
        encoded_text = urllib.parse.quote(sms_text)
        
        # Cú pháp link SMS hỗ trợ cả Android & iOS
        sms_link = f"sms:{phone_number}?body={encoded_text}"
        
        if phone_number:
            st.markdown(f'''
                <a href="{sms_link}" target="_blank" style="display: inline-block; padding: 10px 20px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 6px; font-weight: bold;">
                    🚀 Mở ứng dụng SMS để gửi link
                </a>
            ''', unsafe_allow_dict=True)

st.divider()

# 4. Hiển thị lịch sử tin nhắn
st.subheader("Trò chuyện")
chat_container = st.container(height=350)

messages = st.session_state.rooms[room_id]

with chat_container:
    if not messages:
        st.info("Chưa có tin nhắn nào. Hãy gửi tin nhắn đầu tiên!")
    for msg in messages:
        sender_label = "Bạn" if msg["sender"] == ("User" if is_sender else "Guest") else "Đối phương"
        avatar = "🧑‍💻" if msg["sender"] == ("User" if is_sender else "Guest") else "👤"
        
        with st.chat_message(sender_label, avatar=avatar):
            st.write(msg["text"])
            st.caption(f"{msg['time']}")

# 5. Khung nhập và gửi tin nhắn mới
user_role = "User" if is_sender else "Guest"
if prompt := st.chat_input("Nhập tin nhắn..."):
    now_str = datetime.datetime.now().strftime("%H:%M:%S")
    st.session_state.rooms[room_id].append({
        "sender": user_role,
        "text": prompt,
        "time": now_str
    })
    st.rerun()
