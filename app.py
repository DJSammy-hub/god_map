import streamlit as st
from datetime import datetime, time
import time as time_module
from lunar_python import Lunar, Solar

# --- 1. 頁面設定 ---
st.set_page_config(
    page_title="尋找我的神老闆｜AI 職場運勢解析", 
    page_icon="⛩️", 
    layout="centered"
)

# --- 2. CSS 美化 (V13.0 IG 網紅分享版) ---
st.markdown("""
<style>
    .stApp { background-color: #0E1117; }
    h1, h2, h3 { color: #D4AF37 !important; font-family: "Microsoft JhengHei", sans-serif; }
    .stSelectbox label, .stDateInput label, .stTimeInput label, .stCheckbox label {
        color: #D4AF37 !important; font-weight: bold;
    }
    
    /* 八字框 */
    .bazi-box {
        background: linear-gradient(145deg, #1a1c24, #111319);
        color: #D4AF37; padding: 20px; border: 1px solid #D4AF37;
        border-radius: 10px; text-align: center;
        font-family: 'Courier New', monospace; letter-spacing: 2px;
        margin-bottom: 20px;
    }
    
    /* 🔥 重點：IG 限動專用卡片設計 */
    .ig-card {
        background: linear-gradient(180deg, #262730 0%, #000000 100%);
        border: 2px solid #D4AF37;
        border-radius: 15px;
        padding: 30px 20px;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 0 30px rgba(212, 175, 55, 0.2);
        position: relative;
    }
    .ig-card::before {
        content: "2026 運勢御守";
        position: absolute;
        top: -12px;
        left: 50%;
        transform: translateX(-50%);
        background-color: #D4AF37;
        color: #000;
        padding: 2px 12px;
        border-radius: 10px;
        font-size: 12px;
        font-weight: bold;
    }
    
    .keyword-tag {
        background-color: #E63946; color: white; padding: 8px 16px;
        border-radius: 30px; font-size: 20px; font-weight: bold;
        display: inline-block; margin: 15px 0;
        box-shadow: 0 4px 10px rgba(230, 57, 70, 0.5);
    }
    
    .god-boss-text {
        font-size: 24px; color: #D4AF37; font-weight: bold; margin-top: 10px;
    }
    
    .fortune-desc-text {
        color: #DDD; font-size: 14px; line-height: 1.6; margin-top: 15px;
    }

    /* 推薦卡片 */
    .temple-card {
        background-color: #262730; color: #E0E0E0; padding: 20px;
        border-radius: 10px; border-top: 5px solid #D4AF37; margin-bottom: 15px;
    }
    
    .role-tag {
        background-color: #D4AF37; color: #000; padding: 2px 8px; border-radius: 4px; 
        font-size: 12px; font-weight: bold; margin-right: 5px;
    }
    .role-tag-sec {
        background-color: #AAA; color: #000; padding: 2px 8px; border-radius: 4px; 
        font-size: 12px; font-weight: bold; margin-right: 5px;
    }

    .stButton>button {
        width: 100%; background: linear-gradient(90deg, #D4AF37 0%, #AA8C2C 100%);
        color: #000; font-weight: bold; border: none; padding: 15px; font-size: 18px;
    }
    a { text-decoration: none; }
</style>
""", unsafe_allow_html=True)

# --- 3. 資料庫函數 ---
def get_god_data(god_key):
    db = {
        "guan_gong": [ 
            {"name": "雲林北港武德宮", "feature": "武財神祖廟，擁有天庫金爐，補財庫必去。"},
            {"name": "台北行天宮", "feature": "北台灣首選，不燒香心誠則靈，求職場穩定。"},
            {"name": "高雄關帝廟", "feature": "南台灣武廟代表，設有五路財神殿，業務必拜。"}
        ],
        "mazu": [
            {"name": "大甲鎮瀾宮", "feature": "全台香火最鼎盛，媽祖慈悲，適合求平安與人脈。"},
            {"name": "北港朝天宮", "feature": "媽祖信仰總本山，靈氣充足，適合創業者求靈感。"},
            {"name": "板橋慈惠宮", "feature": "郭台銘發跡地，許多企業家會來拜，偏財運極強。"}
        ],
        "baosheng": [
            {"name": "大龍峒保安宮", "feature": "國定古蹟，醫神保生大帝，求健康、安神首選。"},
            {"name": "台南學甲慈濟宮", "feature": "開基保生大帝，歷史悠久，擁有上白礁祭典。"},
            {"name": "台中元保宮", "feature": "台中大道公廟，守護鄉里，適合祈求工作根基穩固。"}
        ],
        "tiger": [
            {"name": "石碇五路財神廟", "feature": "金碧輝煌，虎爺愛吃生雞蛋，求偏財、業績必去。"},
            {"name": "新港奉天宮", "feature": "桌上金虎爺，可換錢水，財源滾滾。"}
        ],
        "prince": [
            {"name": "新營太子宮", "feature": "太子爺總廟，分靈無數，求創新、動力首選。"},
            {"name": "高雄三鳳宮", "feature": "南台太子廟代表，建築宏偉，守護年輕創業者。"}
        ]
    }
    return db.get(god_key, [])

def get_local_temples(god_key, city):
    local = {
        ("baosheng", "台北市"): [{"name": "大龍峒保安宮", "feature": "米其林三星古蹟，求藥籤靈驗。"}],
        ("baosheng", "新北市"): [{"name": "樹林濟安宮", "feature": "樹林大廟，保生大帝坐鎮。"}],
        ("guan_gong", "台北市"): [{"name": "行天宮", "feature": "正氣凜然，求事業正財。"}],
        ("guan_gong", "新北市"): [{"name": "金瓜石勸濟堂", "feature": "全台最大銅座關公。"}],
        ("mazu", "台北市"): [{"name": "松山慈祐宮", "feature": "饒河夜市旁，求人緣桃花。"}],
        ("mazu", "台中市"): [{"name": "樂成宮", "feature": "旱溪媽祖，月老也很有名。"}],
    }
    return local.get((god_key, city), [])

# --- 4. 核心演算法 (V12.0 流年運勢引擎) ---
def analyze_destiny_v12(birth_date, birth_time, user_location):
    solar = Solar.fromYmdHms(birth_date.year, birth_date.month, birth_date.day, birth_time.hour, birth_time.minute, 0)
    lunar = solar.getLunar()
    ba_zi = [lunar.getYearInGanZhi(), lunar.getMonthInGanZhi(), lunar.getDayInGanZhi(), lunar.getTimeInGanZhi()]
    day_master = lunar.getDayGan()
    month = birth_date.month
    
    current_date = datetime.now()
    current_lunar = Lunar.fromDate(current_date)
    current_year_gan = current_lunar.getYearGan() 
    current_year_zhi = current_lunar.getYearZhi()
    current_year_str = f"{current_year_gan}{current_year_zhi}" 
    
    fortune_title = ""
    fortune_desc = ""
    fortune_keyword = ""
    
    wuxing = {"甲":"木", "乙":"木", "丙":"火", "丁":"火", "戊":"土", "己":"土", "庚":"金", "辛":"金", "壬":"水", "癸":"水"}
    dm_elem = wuxing[day_master]
    yr_elem = wuxing[current_year_gan]

    relation = ""
    if dm_elem == yr_elem: relation = "比劫"
    elif (dm_elem=="木" and yr_elem=="火") or (dm_elem=="火" and yr_elem=="土") or (dm_elem=="土" and yr_elem=="金") or (dm_elem=="金" and yr_elem=="水") or (dm_elem=="水" and yr_elem=="木"): relation = "食傷"
    elif (dm_elem=="木" and yr_elem=="土") or (dm_elem=="火" and yr_elem=="金") or (dm_elem=="土" and yr_elem=="水") or (dm_elem=="金" and yr_elem=="木") or (dm_elem=="水" and yr_elem=="火"): relation = "財星"
    elif (dm_elem=="木" and yr_elem=="金") or (dm_elem=="火" and yr_elem=="水") or (dm_elem=="土" and yr_elem=="木") or (dm_elem=="金" and yr_elem=="火") or (dm_elem=="水" and yr_elem=="土"): relation = "官殺"
    else: relation = "印星"

    if relation == "比劫":
        fortune_keyword = "廣結善緣"
        fortune_title = f"{current_year_str}年是您的【人脈競爭年】"
        fortune_desc = "社交活動多，開銷大，但朋友就是錢脈。建議多拜武財神守財，或媽祖求圓融。"
    elif relation == "食傷":
        fortune_keyword = "才華洋溢"
        fortune_title = f"{current_year_str}年是您的【表現發揮年】"
        fortune_desc = "點子特別多，才華擋不住！但要小心過勞。建議拜保生大帝顧身體，或太子爺保持動力。"
    elif relation == "財星":
        fortune_keyword = "財源滾滾"
        fortune_title = f"{current_year_str}年是您的【收穫得財年】"
        fortune_desc = "財氣旺，賺錢機會多，是衝刺業績的好年。建議拜虎爺咬錢，並請關公幫您看守財庫。"
    elif relation == "官殺":
        fortune_keyword = "責任升遷"
        fortune_title = f"{current_year_str}年是您的【壓力升遷年】"
        fortune_desc = "主管給重任，壓力大但能升官。容易犯小人，建議拜關聖帝君斬小人，或王爺制煞。"
    else: 
        fortune_keyword = "貴人提攜"
        fortune_title = f"{current_year_str}年是您的【沉澱學習年】"
        fortune_desc = "適合進修，長輩緣極佳。步調稍慢但穩健。建議拜文昌或保生大帝，穩固根基。"

    main_god = {}
    sec_god = {}
    
    if relation in ["財星", "比劫"]:
        main_god = {"name": "武財神 (關聖帝君)", "key": "guan_gong", "role": "鎮守財庫"}
        sec_god = {"name": "黑虎將軍", "key": "tiger", "role": "加強偏財"}
    elif relation in ["官殺"]:
        main_god = {"name": "中壇元帥 (三太子)", "key": "prince", "role": "突破重圍"}
        sec_god = {"name": "保生大帝", "key": "baosheng", "role": "調養身心"}
    elif relation in ["食傷"]:
         main_god = {"name": "保生大帝", "key": "baosheng", "role": "固本培元"}
         sec_god = {"name": "天上聖母 (媽祖)", "key": "mazu", "role": "廣結善緣"}
    else: 
         main_god = {"name": "天上聖母 (媽祖)", "key": "mazu", "role": "接引貴人"}
         sec_god = {"name": "武財神 (關聖帝君)", "key": "guan_gong", "role": "執行魄力"}

    final_list = []
    
    main_local = get_local_temples(main_god['key'], user_location)
    main_famous = get_god_data(main_god['key'])
    sec_famous = get_god_data(sec_god['key'])
    
    if main_local:
        temple = main_local[0]
        temple['type'] = 'main'
        final_list.append(temple)
        
    for t in main_famous:
        if len(final_list) >= 2: break
        if t['name'] not in [x['name'] for x in final_list]:
            t['type'] = 'main'
            final_list.append(t)
            
    if sec_famous:
        temple = sec_famous[0]
        temple['type'] = 'sec'
        final_list.append(temple)
            
    return {
        "ba_zi": ba_zi,
        "day_master": day_master,
        "current_year": current_year_str,
        "fortune_title": fortune_title,
        "fortune_desc": fortune_desc,
        "fortune_keyword": fortune_keyword,
        "main_god": main_god,
        "sec_god": sec_god,
        "temple_list": final_list,
        "product_link": f"https://shopline.com/search?q={main_god['key']}" 
    }

# --- 5. 介面呈現 ---
st.title("⛩️ 尋找我的神老闆")
st.markdown("<h3 style='text-align: center; color: #FFF !important;'>2026 流年運勢 x AI 命理配對</h3>", unsafe_allow_html=True)
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
    submit = st.form_submit_button("🔍 立即分析我的 2026 運勢")

if submit:
    with st.spinner('⏳ 正在解析流年天干與元神關係...'):
        time_module.sleep(0.8)
    data = analyze_destiny_v12(b_date, b_time, user_loc)

    # 1. IG 截圖專用卡 (視覺強化)
    st.markdown(f"""
    <div class="ig-card">
        <div style="font-size:16px; color:#AAA;">📅 {data['current_year']} 職場運勢關鍵字</div>
        <div class="keyword-tag">🔥 {data['fortune_keyword']}</div>
        <div class="fortune-desc-text" style="color:#FFF; font-weight:bold; font-size:18px;">
            {data['fortune_title']}
        </div>
        <div class="fortune-desc-text">
            {data['fortune_desc']}
        </div>
        <hr style="border-color:#444; margin: 20px 0;">
        <div style="font-size:14px; color:#AAA;">⛩️ 您的神老闆陣容</div>
        <div class="god-boss-text">
             {data['main_god']['name']} + {data['sec_god']['name']}
        </div>
        <div style="margin-top:20px; font-size:12px; color:#666;">
            📍 截圖分享上傳 IG 限動，領取開運能量
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 2. 分享按鈕區 (新功能)
    c_share1, c_share2 = st.columns([3, 1])
    with c_share1:
        st.text_input("🔗 複製連結分享給朋友", value="https://god-map.streamlit.app", disabled=True)
    with c_share2:
        # 這裡只能做連結跳轉，無法直接貼文
        st.link_button("去 IG 發文", "https://instagram.com/")

    st.markdown("---")
    
    # 3. 推薦清單
    st.markdown(f"<h3 style='color:#D4AF37;'>⛩️ 您的專屬參拜清單</h3>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:#AAA; font-size:14px;'>根據流年運勢，建議您前往以下辦事處：</p>", unsafe_allow_html=True)

    for i, temple in enumerate(data['temple_list']):
        if temple['type'] == 'main':
            label = f"<span class='role-tag'>主神｜{data['main_god']['role']}</span>"
            title_color = "#D4AF37"
        else:
            label = f"<span class='role-tag-sec'>輔神｜{data['sec_god']['role']}</span>"
            title_color = "#AAA"

        with st.expander(f"📍 推薦 {i+1}：{temple['name']} ({'主神' if temple['type']=='main' else '輔神'})", expanded=True):
            st.markdown(f"""
            <div style="margin-bottom:5px;">{label}</div>
            <div style="font-size:18px; color:{title_color}; font-weight:bold;">{temple['name']}</div>
            <div style="color:#AAA; font-size:14px; margin-top:5px;">💡 {temple['feature']}</div>
            """, unsafe_allow_html=True)
            map_query = f"{temple['name']}"
            st.link_button(f"🗺️ 導航去 {temple['name']}", f"https://www.google.com/maps/search/?api=1&query={map_query}")

    # 4. 導購與表單
    st.write("")
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1: st.link_button(f"🛒 購買 {data['main_god']['name']} 開運物", data['product_link'])
    with c2: 
        if agree: st.link_button("📝 領取 2026 完整運勢報告", "https://forms.google.com/")