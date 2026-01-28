import streamlit as st
from datetime import datetime, time
import time as time_module
from lunar_python import Lunar, Solar
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# --- 1. 頁面設定 (更新標題) ---
st.set_page_config(
    page_title="找到我的神老闆｜全台廟宇地圖", 
    page_icon="⛩️", 
    layout="centered"
)

# --- 2. 核心資料庫 (神老闆名單) ---
TEMPLE_DB = {
    "武財神 (關聖帝君)": {
        "key": "guan_gong",
        "台北市": "台北行天宮",
        "新北市": "金瓜石勸濟堂",
        "基隆市": "基隆聖安宮",
        "桃園市": "大溪普濟堂",
        "新竹縣": "普元宮",
        "新竹市": "古奇峰普天宮",
        "苗栗縣": "玉清宮",
        "台中市": "台中南天宮",
        "彰化縣": "彰化關帝廟",
        "南投縣": "日月潭文武廟",
        "雲林縣": "四湖參天宮",
        "嘉義縣": "嘉義南天門太子行宮",
        "嘉義市": "嘉義文財殿",
        "台南市": "台灣祀典武廟",
        "高雄市": "高雄關帝廟 (武廟)",
        "屏東縣": "車城統埔鎮安宮",
        "宜蘭縣": "礁溪協天廟",
        "花蓮縣": "花蓮聖天宮",
        "台東縣": "台東關帝廟",
        "澎湖縣": "澎湖文澳城隍廟",
        "金門縣": "金門關帝廟",
        "連江縣": "馬祖南竿牛峰境",
        "default": "雲林北港武德宮 (財神開基祖廟)"
    },
    "天上聖母 (媽祖)": {
        "key": "mazu",
        "台北市": "松山慈祐宮 / 關渡宮",
        "新北市": "板橋慈惠宮",
        "基隆市": "慶安宮",
        "桃園市": "中壢仁海宮",
        "新竹縣": "竹北天后宮",
        "新竹市": "新竹長和宮",
        "苗栗縣": "白沙屯拱天宮",
        "台中市": "大甲鎮瀾宮 / 旱溪樂成宮",
        "彰化縣": "鹿港天后宮",
        "南投縣": "集集廣盛宮",
        "雲林縣": "北港朝天宮",
        "嘉義縣": "新港奉天宮",
        "嘉義市": "嘉義朝天宮",
        "台南市": "大天后宮 / 正統鹿耳門聖母廟",
        "高雄市": "旗津天后宮",
        "屏東縣": "屏東慈鳳宮",
        "宜蘭縣": "南方澳南天宮",
        "花蓮縣": "花蓮港天宮",
        "台東縣": "台東天后宮",
        "澎湖縣": "澎湖天后宮",
        "金門縣": "金門天后宮",
        "連江縣": "馬祖南竿天后宮",
        "default": "雲林北港朝天宮"
    },
    "黑虎將軍/武財神": {
        "key": "tiger",
        "台北市": "北投關渡宮 (財神洞)",
        "新北市": "石碇五路財神廟",
        "桃園市": "南崁五福宮",
        "台中市": "台中廣天宮",
        "雲林縣": "北港武德宮 (五路財神祖廟)",
        "台南市": "南鯤鯓代天府",
        "高雄市": "旗山八路財神廟",
        "屏東縣": "枋山五路財神廟",
        "default": "北港武德宮 (虎爺大本營)"
    },
    "中壇元帥 (三太子)": {
        "key": "prince",
        "台北市": "社子島坤天亭",
        "新北市": "新莊保元宮",
        "桃園市": "桃園護國宮 (太子廟)",
        "新竹市": "指澤宮",
        "台中市": "三陽玉府天宮",
        "台南市": "新營太子宮 (全台總廟)",
        "高雄市": "高雄三鳳宮",
        "default": "台南新營太子宮 (全台總廟)"
    }
}

# --- 3. CSS 美化 (黑金風格) ---
st.markdown("""
<style>
    .stApp { background-color: #0E1117; }
    h1, h2, h3 { color: #D4AF37 !important; font-family: "Microsoft JhengHei", sans-serif; }
    
    /* 輸入框優化 */
    .stSelectbox label, .stDateInput label, .stTimeInput label {
        color: #D4AF37 !important;
        font-weight: bold;
    }

    .bazi-box {
        background: linear-gradient(145deg, #1a1c24, #111319);
        color: #D4AF37; padding: 25px; border: 1px solid #D4AF37;
        border-radius: 10px; text-align: center;
        font-family: 'Courier New', monospace; letter-spacing: 2px;
        margin-bottom: 20px;
    }
    
    .result-card {
        background-color: #262730; color: #E0E0E0; padding: 25px;
        border-radius: 10px; border-left: 5px solid #D4AF37; margin-top: 15px;
    }
    
    .temple-highlight {
        background-color: #D4AF37; color: #000; padding: 8px 20px;
        border-radius: 20px; font-weight: bold; display: inline-block; margin-top: 10px;
        box-shadow: 0 0 10px rgba(212, 175, 55, 0.4);
    }

    .stButton>button {
        width: 100%; background: linear-gradient(90deg, #D4AF37 0%, #AA8C2C 100%);
        color: #000; font-weight: bold; border: none; padding: 15px; font-size: 18px;
    }
    a { text-decoration: none; }
</style>
""", unsafe_allow_html=True)

# --- 4. 命理與配對邏輯 ---
def analyze_destiny_v2(birth_date, birth_time, user_location):
    # A. 命盤計算
    solar = Solar.fromYmdHms(birth_date.year, birth_date.month, birth_date.day, birth_time.hour, birth_time.minute, 0)
    lunar = solar.getLunar()
    ba_zi = [lunar.getYearInGanZhi(), lunar.getMonthInGanZhi(), lunar.getDayInGanZhi(), lunar.getTimeInGanZhi()]
    month = birth_date.month
    
    # B. 判斷神老闆 (五行調候)
    if 2 <= month <= 4: # 春 (木旺缺金)
        god_name = "武財神 (關聖帝君)"
        reason = "春木過旺，需金修剪。您的神老闆是【關聖帝君】，祂能斬斷職場小人，助您決策果斷，正財穩固。"
        lacking = "金 (決斷力)"
    elif 5 <= month <= 7: # 夏 (火旺缺水)
        god_name = "天上聖母 (媽祖)"
        reason = "夏火過炎，需水調候。您的神老闆是【天上聖母】，祂能賜您圓融智慧，廣結善緣，化解火爆脾氣。"
        lacking = "水 (智慧)"
    elif 8 <= month <= 10: # 秋 (金旺缺木)
        god_name = "黑虎將軍/武財神"
        reason = "秋金肅殺，需木生發。您的神老闆是【黑虎將軍】，祂的爆發力能為您咬錢帶財，在僵局中殺出一條血路。"
        lacking = "木 (生機)"
    else: # 冬 (水旺缺火)
        god_name = "中壇元帥 (三太子)"
        reason = "冬水寒冷，需火暖局。您的神老闆是【中壇元帥】，祂的赤子之心與行動力，能為您驅除懶散，動力全開。"
        lacking = "火 (動力)"

    # C. LBS 地理配對
    temple_dict = TEMPLE_DB.get(god_name, {})
    local_temple = temple_dict.get(user_location, temple_dict.get("default"))
    key = temple_dict.get("key", "")
    
    return {
        "ba_zi": ba_zi,
        "lacking": lacking,
        "god": god_name,
        "temple": local_temple,
        "reason": reason,
        "product_link": f"https://shopline.com/search?q={key}" 
    }

# --- 5. 介面呈現 ---
st.title("⛩️ 找到我的神老闆")
st.markdown("<h3 style='text-align: center; color: #FFF !important;'>全台廟宇地圖 x AI 命理檢測</h3>", unsafe_allow_html=True)
st.write("")

with st.form("main_form"):
    c1, c2 = st.columns(2)
    with c1: 
        b_date = st.date_input("📅 出生日期", value=datetime(1995, 1, 1), min_value=datetime(1950, 1, 1))
    with c2: 
        b_time = st.time_input("⏰ 出生時間", value=time(12, 0))
    
    taiwan_locations = [
        "台北市", "新北市", "基隆市", "桃園市", "新竹縣", "新竹市", "苗栗縣", 
        "台中市", "彰化縣", "南投縣", "雲林縣", "嘉義縣", "嘉義市", 
        "台南市", "高雄市", "屏東縣", "宜蘭縣", "花蓮縣", "台東縣", 
        "澎湖縣", "金門縣", "連江縣"
    ]
    user_loc = st.selectbox("🏠 居住縣市 (為您尋找最近的據點)", taiwan_locations)
    
    agree = st.checkbox("我同意將匿名數據提供給「神職應援團」做統計分析")
    
    submit = st.form_submit_button("🔍 尋找我的神老闆")

if submit:
    # 執行運算
    with st.spinner('⏳ 正在連線天干地支資料庫...'):
        time_module.sleep(0.8)
    data = analyze_destiny_v2(b_date, b_time, user_loc)

    # 寫入 Google Sheets (包在 try-except 避免沒設定 Secrets 時報錯)
    if agree:
        try:
            conn = st.connection("gsheets", type=GSheetsConnection)
            existing_data = conn.read(worksheet="Sheet1", usecols=list(range(6)), ttl=5)
            new_row = pd.DataFrame([{
                "填寫時間": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "居住縣市": user_loc,
                "出生年生": b_date.year,
                "缺五行": data['lacking'],
                "推薦神明": data['god'],
                "推薦原因": data['reason']
            }])
            updated_df = pd.concat([existing_data, new_row], ignore_index=True)
            conn.update(worksheet="Sheet1", data=updated_df)
        except Exception as e:
            pass # 靜默處理錯誤

    # 1. 八字區
    st.markdown(f"""
    <div class="bazi-box">
        <div style="font-size:14px; color:#888;">您的職場本命盤</div>
        <div style="font-size:24px; margin-top:10px;">
            {data['ba_zi'][0]}   {data['ba_zi'][1]}   <span style="color:#FFF;">{data['ba_zi'][2]}</span>   {data['ba_zi'][3]}
        </div>
        <div style="font-size:12px; color:#666; margin-top:5px;">年柱     月柱     元神     時柱</div>
    </div>
    """, unsafe_allow_html=True)

    # 2. 結果區
    st.markdown(f"""
    <div class="result-card">
        <h3 style="color:#D4AF37;">命局診斷</h3>
        <p>依據八字調候，您目前最欠缺 <span style="color:#E63946; font-weight:bold;">【{data['lacking']}】</span> 能量。</p>
        <p>{data['reason']}</p>
    </div>
    
    <div class="result-card" style="border-left: 5px solid #E63946;">
        <h3 style="color:#E63946; text-align:center;">⛩️ 您的神老闆是 ⛩️</h3>
        <h1 style="text-align:center; color:#FFF;">{data['god']}</h1>
        <div style="text-align:center;">
            <span class="temple-highlight">📍 {user_loc}｜{data['temple']}</span>
        </div>
        <p style="text-align:center; margin-top:15px; color:#AAA;">這位神老闆離您最近，且磁場最合，建議盡快前往「面試」(參拜)。</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 3. 導購區
    st.write("")
    col_a, col_b = st.columns(2)
    with col_a:
        st.link_button(f"🛒 購買 {data['god']} 聯名戰袍", data['product_link'])
    with col_b:
        map_query = f"{data['temple']}"
        st.link_button("🗺️ 開啟導航去拜碼頭", f"https://www.google.com/maps/search/?api=1&query={map_query}")