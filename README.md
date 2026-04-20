# 三人即時聊天室 - Phase 1

## 專案概述
- 三人即時聊天室，使用 Firebase Realtime Database
- 成員：少爺（藍色）、龍龍（綠色）、蝦米（紅色）

## Firebase 設定指引

### 1. 建立 Firebase 專案
1. 前往 [Firebase Console](https://console.firebase.google.com/)
2. 使用 luluopenclaw0110@gmail.com 登入
3. 點擊「新增專案」
4. 專案名稱：`ai-chatroom`
5. 停用 Google Analytics（可選）
6. 點擊「建立專案」

### 2. 啟用 Realtime Database
1. 在左側選單點擊「Realtime Database」
2. 點擊「建立資料庫」
3. 選擇地區（建議：asia-east1 或 us-central）
4. 選擇「以測試模式啟動」
5. 點擊「啟用」

### 3. 設定資料庫規則（測試用）
在「規則」標籤中設定：
```json
{
  "rules": {
    ".read": true,
    ".write": true
  }
}
```

### 4. 取得 Firebase 設定檔
1. 點擊齒輪圖示 → 「專案設定」
2. 向下滾動到「您的應用程式」
3. 點擊 web icon（</>）新增網頁應用
4. 註冊應用程式
5. 複製 firebaseConfig 物件內容

### 5. 設定 secrets.toml
將 Firebase 設定寫入 `.streamlit/secrets.toml`：

```toml
[firebase]
type = "your-type"
project_id = "ai-chatroom"
private_key_id = "your-private-key-id"
private_key = "your-private-key"
client_email = "your-client-email"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "your-cert-url"
```

### 6. 產生服務帳號金鑰（用於 Firebase Admin SDK）
1. 在「專案設定」→「服務帳號」
2. 點擊「產生新的私密金鑰」
3. 下載 JSON 檔案
4. 將 JSON 內容填入 `secrets.toml`

## 本地執行

```bash
cd ~/ai-chatroom
pip3 install -r requirements.txt
streamlit run app.py --server.port 8504
```

## 功能
- ✅ 三個成員身份切換（少爺/龍龍/蝦米）
- ✅ 即時訊息顯示
- ✅ 自動輪詢更新（每 2 秒）
- ✅ 訊息時間戳
- ✅ 成員名稱不同顏色顯示
