import streamlit as st
from datetime import datetime, time
import time as time_module
from lunar_python import Lunar, Solar

# --- 1. 頁面設定 ---
st.set_page_config(
    page_title="找到我的神老闆｜全台廟宇地圖", 
    page_icon="⛩️", 
    layout="centered"
)

# --- 2. CSS 美化 (維持 V9.0 的三欄設計) ---
st.markdown("""
<style>
    .stApp { background-color: #0E1117; }
    h1, h2, h3 { color: #D4AF37 !important; font-family: "Microsoft JhengHei", sans-serif; }
    .stSelectbox label, .stDateInput label, .stTimeInput label, .stCheckbox label {
        color: #D4AF37 !important; font-weight: bold;
    }
    .bazi-box {
        background: linear-gradient(145deg, #1a1c24, #111319);
        color: #D4AF37; padding: 20px; border: 1px solid #D4AF37;
        border-radius: 10px; text-align: center;
        font-family: 'Courier New', monospace; letter-spacing: 2px;
        margin-bottom: 20px;
    }
    .temple-card {
        background-color: #262730; color: #E0E0E0; padding: 20px;
        border-radius: 10px; border-top: 5px solid #D4AF37; margin-bottom: 15px;
    }
    .feature-tag {
        background-color: #333; color: #AAA; padding: 5px 10px; border-radius: 5px; 
        font-size: 13px; margin-top: 8px; display: block;
    }
    .stButton>button {
        width: 100%; background: linear-gradient(90deg, #D4AF37 0%, #AA8C2C 100%);
        color: #000; font-weight: bold; border: none; padding: 15px; font-size: 18px;
    }
    a { text-decoration: none; }
</style>
""", unsafe_allow_html=True)

# --- 3. 核心資料庫 (新增保生大帝) ---
def get_god_data(god_key):
    famous_backups = {
        "guan_gong": [ # 武財神
            {"name": "雲林北港武德宮", "feature": "全台武財神祖廟，巨大天庫金爐，求正財與事業運。"},
            {"name": "台北行天宮", "feature": "恩主公信仰，正氣凜然，收驚靈驗，適合求事業穩定。"},
            {"name": "高雄關帝廟", "feature": "南台灣著名武廟，設有五路財神殿，業務必拜。"}
        ],
        "mazu": [ # 媽祖
            {"name": "台中大甲鎮瀾宮", "feature": "全台香火最旺之一，大甲媽慈悲，適合求平安與人脈。"},
            {"name": "板橋慈惠宮", "feature": "郭台銘發跡廟，媽祖賜福，適合求貴人與偏財。"},
            {"name": "北港朝天宮", "feature": "媽祖總本山，靈氣充足，有求必應。"}
        ],
        "baosheng": [ # 新增：保生大帝 (健康/固本)
            {"name": "台北大龍峒保安宮", "feature": "國定古蹟，保生大帝醫術高明，求健康、安神、固本首選。"},
            {"name": "台南學甲慈濟宮", "feature": "開基保生大帝，歷史悠久，擁有全台僅有的上白礁祭典。"},
            {"name": "台中元保宮", "feature": "台中市區的大道公廟，香火鼎盛，守護地方安寧。"}
        ],
        "tiger": [ # 虎爺
            {"name": "石碇五路財神廟", "feature": "求偏財首選，虎爺愛吃生雞蛋，業務投資必拜。"},
            {"name": "嘉義新港奉天宮", "feature": "桌上金虎爺，可換錢水，財氣滿滿。"},
            {"name": "北港武德宮", "feature": "黑虎將軍大本營，咬錢速度快，適合急需周轉。"}
        ],
        "prince": [ # 三太子
            {"name": "台南新營太子宮", "feature": "全台太子爺總廟，求動力、創新、突破首選。"},
            {"name": "高雄三鳳宮", "feature": "建築宏偉，年輕創業者的守護神。"},
            {"name": "桃園護國宮", "feature": "獨腳太子辦事靈驗，適合求行車平安。"}
        ]
    }
    return famous_backups.get(god_key, [])

def get_local_temples(god_key, city):
    # 在地資料庫擴充 (加入保生大帝)
    local_db = {
        # ... (保留原本的關公、媽祖、虎爺、太子，為了篇幅我這裡只列新增的) ...
        # 如果您原本的資料庫完整，請把原本的貼回來，這裡我示範新增保生大帝
        
        ("baosheng", "台北市"): [{"name": "大龍峒保安宮", "feature": "米其林三星景點，求藥籤非常靈驗。"}],
        ("baosheng", "新北市"): [{"name": "樹林濟安宮", "feature": "樹林大廟，保生大帝坐鎮，守護健康。"}],
        ("baosheng", "台中市"): [{"name": "台中元保宮", "feature": "大道公廟，歷史悠久，香火鼎盛。"}],
        ("baosheng", "台南市"): [{"name": "學甲慈濟宮", "feature": "開基祖廟，上白礁謁祖祭典非常盛大。"}],
        ("baosheng", "高雄市"): [{"name": "高雄鼓山亭", "feature": "在地信仰中心，保生大帝靈驗。"}],
        
        # 關公 (範例)
        ("guan_gong", "台北市"): [{"name": "行天宮", "feature": "不燒香的環保廟宇，心誠則靈。"}],
        ("guan_gong", "新北市"): [{"name": "金瓜石勸濟堂", "feature": "全台最大銅座關公。"}],
        # ... (請自行補全其他縣市的舊有資料)
    }
    # 為了防止找不到資料報錯，這裡做一個簡單的 fallback
    return local_db.get((god_key, city), [])

# --- 4. 命理與配對邏輯 (V10.0 專家演算法) ---
def analyze_destiny_v10(birth_date, birth_time, user_location):
    # A. 排盤
    solar = Solar.fromYmdHms(birth_date.year, birth_date.month, birth_date.day, birth_time.hour, birth_time.minute, 0)
    lunar = solar.getLunar()
    ba_zi = [lunar.getYearInGanZhi(), lunar.getMonthInGanZhi(), lunar.getDayInGanZhi(), lunar.getTimeInGanZhi()]
    day_master = lunar.getDayGan() # 取得日主 (例如：甲、乙、丙...)
    month = birth_date.month
    
    # B. 判斷邏輯 (結合元神 + 季節)
    # 這裡模擬老師的邏輯：
    # 1. 如果日主是土/金/水，且生在消耗的季節 -> 身弱 -> 建議保生大帝 (固本/健康)
    # 2. 如果日主是木/火，且生在旺季 -> 身強 -> 建議關公 (修剪/事業)
    
    god_name = ""
    god_key = ""
    reason = ""
    lacking = ""

    # 簡易判斷 (可依需求調整)
    if day_master in ["甲", "乙", "丙", "丁"]:
        # 木火日主
        if 5 <= month <= 7: # 生於夏天 (火旺) -> 洩氣太過 or 火太旺
            # 這裡就是 AI 與老師的黃金交叉點
            # AI 原本會推媽祖(調候)，但如果考慮事業，關公(金)可以修剪木、或者生水
            god_name = "武財神 (關聖帝君)" 
            god_key = "guan_gong"
            lacking = "金 (決斷力/事業運)"
            reason = f"您的元神為【{day_master}】，生於夏季。火氣雖旺但需金來雕琢成材。武財神關公能助您在事業上大刀闊斧，斬斷猶豫。"
        else:
            # 其他季節 -> 走原本的調候邏輯
             god_name = "天上聖母 (媽祖)"
             god_key = "mazu"
             lacking = "水 (圓融智慧)"
             reason = f"您的元神為【{day_master}】，需要水的滋潤來平衡。媽祖能賜您貴人運與智慧。"
             
    elif day_master in ["戊", "己", "庚", "辛", "壬", "癸"]:
        # 土金水日主
        if day_master in ["戊", "己"] and (10 <= month <= 12 or month == 1):
             # 土生冬天 -> 凍土 -> 需要火/燥土
             god_name = "中壇元帥 (三太子)"
             god_key = "prince"
             lacking = "火 (動力/行動)"
             reason = f"您的元神為【{day_master}】，生於冬日，土氣凍結。三太子能賜您熱情與行動力，破冰前行。"
        else:
             # 其他情況，假設身弱需要固本 (模擬老師建議保生大帝的情境)
             god_name = "保生大帝 (大道公)"
             god_key = "baosheng"
             lacking = "土/木 (健康/根基)"
             reason = f"您的元神為【{day_master}】，目前運勢需要「固本培元」。保生大帝不僅護佑健康，更能幫您穩固職場根基，讓您無後顧之憂。"

    # C. 智慧配對 (湊滿 3 間)
    recommendations = get_local_temples(god_key, user_location)
    backups = get_god_data(god_key)
    final_list = recommendations[:]
    existing_names = [r["name"] for r in final_list]
    for backup in backups:
        if len(final_list) >= 3: break
        if backup["name"] not in existing_names: final_list.append(backup)
            
    return {
        "ba_zi": ba_zi,
        "day_master": day_master,
        "lacking": lacking,
        "god": god_name,
        "temple_list": final_list,
        "reason": reason,
        "product_link": f"https://shopline.com/search?q={god_key}" 
    }

# --- 5. 介面呈現 ---
st.title("⛩️ 找到我的神老闆")
st.markdown("<h3 style='text-align: center; color: #FFF !important;'>全台廟宇地圖 x AI 命理檢測</h3>", unsafe_allow_html=True)
st.write("")

with st.form("main_form"):
    c1, c2 = st.columns(2)
    with c1: b_date = st.date_input("📅 出生日期", value=datetime(1995, 1, 1), min_value=datetime(1950, 1, 1))
    with c2: b_time = st.time_input("⏰ 出生時間", value=time(12, 0))
    
    taiwan_locations = [
        "台北市", "新北市", "基隆市", "桃園市", "新竹縣", "新竹市", "苗栗縣", 
        "台中市", "彰化縣", "南投縣", "雲林縣", "嘉義縣", "嘉義市", 
        "台南市", "高雄市", "屏東縣", "宜蘭縣", "花蓮縣", "台東縣", 
        "澎湖縣", "金門縣", "連江縣"
    ]
    user_loc = st.selectbox("🏠 居住縣市", taiwan_locations)
    agree = st.checkbox("我同意將匿名數據提供給「神職應援團」做統計分析")
    submit = st.form_submit_button("🔍 尋找我的神老闆")

if submit:
    with st.spinner('⏳ 正在解析元神強弱...'):
        time_module.sleep(0.8)
    data = analyze_destiny_v10(b_date, b_time, user_loc)

    # 1. 八字區
    st.markdown(f"""
    <div class="bazi-box">
        <div style="font-size:14px; color:#888;">您的職場本命盤</div>
        <div style="font-size:24px; margin-top:10px;">
            {data['ba_zi'][0]}   {data['ba_zi'][1]}   <span style="color:#FFF; border-bottom:2px solid #D4AF37;">{data['ba_zi'][2]}</span>   {data['ba_zi'][3]}
        </div>
        <div style="font-size:12px; color:#666; margin-top:5px;">年柱     月柱     <b style="color:#D4AF37">元神({data['day_master']})</b>     時柱</div>
    </div>
    """, unsafe_allow_html=True)

    # 2. 命格診斷
    st.markdown(f"""
    <div class="result-card" style="border-left: 5px solid #E63946;">
        <h3 style="color:#D4AF37;">🔮 專家命盤解析</h3>
        <p>依據您的元神【{data['day_master']}】與流年運勢，您最需要補強 <span style="color:#E63946; font-weight:bold;">【{data['lacking']}】</span>。</p>
        <p>{data['reason']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 3. 推薦神老闆
    st.markdown(f"<h3 style='color:#D4AF37; margin-top:30px;'>⛩️ 推薦神老闆：{data['god']}</h3>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:#AAA; font-size:14px;'>以下為您精選 3 間最適合的辦事處：</p>", unsafe_allow_html=True)

    for i, temple in enumerate(data['temple_list']):
        with st.expander(f"📍 推薦 {i+1}：{temple['name']}", expanded=True):
            st.markdown(f"<b>{temple['name']}</b><br><span class='feature-tag'>💡 {temple['feature']}</span>", unsafe_allow_html=True)
            map_query = f"{temple['name']}"
            st.link_button(f"🗺️ 導航去 {temple['name']}", f"https://www.google.com/maps/search/?api=1&query={map_query}")

    # 4. 導購與表單
    st.write("")
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1: st.link_button(f"🛒 購買 {data['god']} 聯名戰袍", data['product_link'])
    with c2: 
        if agree: st.link_button("📝 領取流年運勢報告", "https://forms.google.com/")