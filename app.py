"""
三人即時聊天室 - Phase 1
支援 Firebase Realtime Database + 本地模擬模式

模式切換：
- 本地模式：使用 localStorage 模擬（離線測試）
- Firebase 模式：需要正確設定 secrets.toml

成員：
- 少爺（藍色）
- 龍龍（綠色）
- 蝦米（紅色）
"""

import streamlit as st
import time
from datetime import datetime
import json
import os

# 頁面設定
st.set_page_config(
    page_title="三人聊天室",
    page_icon="💬",
    layout="wide"
)

# 成員設定
MEMBERS = {
    "少爺": {"color": "#1E88E5", "emoji": "👑"},  # 藍色
    "龍龍": {"color": "#43A047", "emoji": "🐉"},  # 綠色
    "蝦米": {"color": "#E53935", "emoji": "🦐"},  # 紅色
}

# 模式設定
# Firebase 設定（從 secrets.toml 讀取）
def get_firebase_config():
    """從 secrets.toml 讀取 Firebase 設定"""
    try:
        if hasattr(st, 'secrets') and "firebase" in st.secrets:
            return st.secrets["firebase"]["database_url"]
    except Exception:
        pass
    return None

FIREBASE_DATABASE_URL = get_firebase_config()
USE_LOCAL_MODE = FIREBASE_DATABASE_URL is None  # 沒有 Firebase URL 時使用本地模式

# 初始化 session state
if "current_user" not in st.session_state:
    st.session_state.current_user = "少爺"
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_fetch_time" not in st.session_state:
    st.session_state.last_fetch_time = 0
if "local_messages" not in st.session_state:
    st.session_state.local_messages = []


def init_firebase_settings():
    """嘗試初始化 Firebase 設定"""
    try:
        if hasattr(st, 'secrets') and "firebase" in st.secrets:
            return {
                "database_url": st.secrets["firebase"]["database_url"],
                "use_firebase": True,
            }
    except Exception:
        pass
    return {"use_firebase": False}


def fetch_messages_firebase():
    """從 Firebase 取得訊息"""
    try:
        import requests
        url = f"{FIREBASE_DATABASE_URL}/messages.json"
        params = {"orderBy": "\"$key\"", "limitToLast": "50"}
        response = requests.get(url, params=params, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data:
                messages = []
                for key, msg in data.items():
                    msg['id'] = key
                    messages.append(msg)
                messages.sort(key=lambda x: x.get('timestamp', 0))
                return messages
        return []
    except Exception as e:
        return []


def send_message_firebase(sender, text):
    """傳送訊息到 Firebase"""
    try:
        import requests
        timestamp = int(time.time() * 1000)
        message = {
            "sender": sender,
            "text": text,
            "timestamp": timestamp,
            "display_time": datetime.now().strftime("%H:%M:%S")
        }
        url = f"{FIREBASE_DATABASE_URL}/messages.json"
        response = requests.post(url, json=message, timeout=5)
        return response.status_code == 200
    except:
        return False


def fetch_messages_local():
    """本地模式：取得訊息"""
    return st.session_state.local_messages


def send_message_local(sender, text):
    """本地模式：發送訊息"""
    message = {
        "id": f"local_{int(time.time() * 1000)}",
        "sender": sender,
        "text": text,
        "timestamp": int(time.time() * 1000),
        "display_time": datetime.now().strftime("%H:%M:%S")
    }
    st.session_state.local_messages.append(message)
    return True


def fetch_messages():
    """統一取得訊息介面"""
    if USE_LOCAL_MODE:
        return fetch_messages_local()
    else:
        return fetch_messages_firebase()


def send_message(sender, text):
    """統一發送訊息介面"""
    if USE_LOCAL_MODE:
        return send_message_local(sender, text)
    else:
        return send_message_firebase(sender, text)


def render_message(msg, current_user):
    """渲染單條訊息"""
    sender = msg.get("sender", "未知")
    text = msg.get("text", "")
    display_time = msg.get("display_time", "")
    member_info = MEMBERS.get(sender, {"color": "#888888", "emoji": "❓"})
    color = member_info["color"]
    emoji = member_info["emoji"]
    
    # 判斷是否是自己發的
    is_me = sender == current_user
    
    # 樣式設定
    bg_color = "#E3F2FD" if is_me else "#FFFFFF"
    align = "flex-end" if is_me else "flex-start"
    border_color = color
    
    html = f"""
    <div style="display: flex; justify-content: {align}; margin: 8px 0;">
        <div style="
            max-width: 70%;
            background: {bg_color};
            border-left: 4px solid {border_color};
            border-radius: 12px;
            padding: 12px 16px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        ">
            <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 6px;">
                <span style="font-size: 16px;">{emoji}</span>
                <span style="font-weight: bold; color: {color}; font-size: 15px;">{sender}</span>
                <span style="color: #999; font-size: 12px; margin-left: 10px;">{display_time}</span>
            </div>
            <div style="color: #333; font-size: 15px; line-height: 1.5; word-wrap: break-word;">{text}</div>
        </div>
    </div>
    """
    return html


def main():
    """主程式"""
    # 初始化 Firebase 設定
    fb_settings = init_firebase_settings()
    
    # 側邊欄 - 成員選擇
    with st.sidebar:
        st.markdown("## 👥 成員切換")
        st.markdown("---")
        
        # 成員選擇
        selected_user = st.radio(
            "選擇身份",
            options=list(MEMBERS.keys()),
            index=list(MEMBERS.keys()).index(st.session_state.current_user),
            format_func=lambda x: f"{MEMBERS[x]['emoji']} {x}",
            label_visibility="collapsed"
        )
        
        if selected_user != st.session_state.current_user:
            st.session_state.current_user = selected_user
            st.rerun()
        
        st.markdown("---")
        st.markdown("### 🎨 成員顏色")
        for name, info in MEMBERS.items():
            st.markdown(
                f"<span style='color: {info['color']}; font-weight: bold; font-size: 18px;'>"
                f"{info['emoji']} {name}</span>",
                unsafe_allow_html=True
            )
        
        st.markdown("---")
        st.markdown("### 連線狀態")
        if fb_settings.get("use_firebase", False):
            st.success("🟢 Firebase 已連線")
        else:
            st.warning("🟡 本地模式（測試用）")
        
        st.markdown("---")
        
        # 清除訊息按鈕（本地模式）
        if st.button("🗑️ 清除訊息", use_container_width=True):
            st.session_state.local_messages = []
            st.rerun()
        
        # 重新整理按鈕
        if st.button("🔄 重新整理", use_container_width=True):
            st.rerun()
    
    # 主視窗標題
    st.markdown("""
    <div style="text-align: center; padding: 15px 0; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); border-radius: 10px; margin-bottom: 20px;">
        <h1 style="color: white; margin: 0;">💬 三人聊天室</h1>
        <p style="color: rgba(255,255,255,0.8); margin: 5px 0 0 0;">
            即時訊息 · Firebase Realtime Database
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # 自動輪詢更新
    current_time = time.time()
    should_refresh = (current_time - st.session_state.last_fetch_time) > 2
    
    if should_refresh or len(st.session_state.messages) == 0:
        messages = fetch_messages()
        if messages:
            st.session_state.messages = messages
            st.session_state.last_fetch_time = current_time
    
    # 訊息顯示區域
    st.markdown("### 📝 訊息記錄")
    
    message_container = st.container()
    
    with message_container:
        if st.session_state.messages:
            for msg in st.session_state.messages[-50:]:
                st.markdown(
                    render_message(msg, st.session_state.current_user),
                    unsafe_allow_html=True
                )
        else:
            st.info("📭 還沒有訊息，成為第一個發言的人吧！")
    
    st.markdown("---")
    
    # 輸入區域
    member_info = MEMBERS[st.session_state.current_user]
    
    col1, col2 = st.columns([6, 1])
    
    with col1:
        message_text = st.text_input(
            "輸入訊息",
            placeholder="輸入訊息後點擊發送...",
            label_visibility="collapsed",
            key="message_input"
        )
    
    with col2:
        send_label = f"{member_info['emoji']} 發送"
        
        if st.button(send_label, use_container_width=True, type="primary"):
            if message_text.strip():
                success = send_message(st.session_state.current_user, message_text.strip())
                if success:
                    # 立即刷新
                    messages = fetch_messages()
                    st.session_state.messages = messages
                    st.session_state.message_input = ""
                    st.rerun()
                else:
                    st.error("傳送失敗！")
    
    # 底部狀態列
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(
            f"<div style='text-align: center;'>"
            f"目前身份：<span style='color: {member_info['color']}; font-weight: bold;'>"
            f"{member_info['emoji']} {st.session_state.current_user}</span></div>",
            unsafe_allow_html=True
        )
    
    with col2:
        if st.session_state.messages:
            count = len(st.session_state.messages)
            st.markdown(f"<div style='text-align: center;'>📊 訊息總數：{count}</div>", unsafe_allow_html=True)
    
    with col3:
        mode_text = "Firebase 模式" if fb_settings.get("use_firebase") else "本地測試模式"
        st.markdown(f"<div style='text-align: center;'>🔧 {mode_text}</div>", unsafe_allow_html=True)
    
    # 自動更新提示
    st.markdown(
        "<div style='text-align: center; color: #aaa; font-size: 12px; margin-top: 10px;'>"
        "✨ 每 2 秒自動更新訊息</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
