import streamlit as st
from datetime import datetime, time
import time as time_module
from lunar_python import Lunar, Solar
import random  # 新增：隨機模組

# --- 1. 頁面設定 ---
st.set_page_config(
    page_title="尋找我的神老闆｜AI 職場運勢解析", 
    page_icon="⛩️", 
    layout="centered"
)

# --- 2. CSS 美化 (V15.0 純淨排版版) ---
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
    
    /* IG 限動卡片 */
    .ig-card {
        background: linear-gradient(180deg, #1A1C24 0%, #000000 100%);
        border: 2px solid #D4AF37;
        border-radius: 20px;
        padding: 30px 20px;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 0 40px rgba(212, 175, 55, 0.15);
        position: relative;
    }
    
    .keyword-tag {
        background-color: #E63946; color: white; padding: 6px 16px;
        border-radius: 30px; font-size: 18px; font-weight: bold;
        display: inline-block; margin-bottom: 10px;
        box-shadow: 0 4px 10px rgba(230, 57, 70, 0.4);
    }
    
    .god-boss-text {
        font-size: 22px; color: #D4AF37; font-weight: bold; margin-top: 10px;
        text-shadow: 0 2px 4px rgba(0,0,0,0.8);
    }
    
    .fortune-desc-text {
        color: #CCC; font-size: 14px; line-height: 1.5; margin-top: 10px;
    }
    
    /* 標籤樣式 */
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

# --- 3. 巨量資料庫 (V15.0 全台擴充版) ---
# 這裡包含了 7 大神明 x 全台主要縣市的資料
# 為了避免重複，系統會從這裡面隨機抓取

def get_god_temple_list(god_key):
    # 這是一個包含全台各地廟宇的超大字典
    # 格式： {"縣市": [廟宇列表]}
    
    db = {
        # === 1. 武財神 (關公/正財/事業) ===
        "guan_gong": {
            "all": [ # 全台通用 (若在地找不到時用)
                {"name": "雲林北港武德宮", "feature": "全台財神開基祖廟，巨大天庫金爐。"},
                {"name": "南投竹山紫南宮", "feature": "雖主祀土地公，但為全台最強求財聖地。"}, 
                {"name": "台北行天宮", "feature": "恩主公信仰，正氣凜然，求事業穩定。"},
                {"name": "高雄關帝廟", "feature": "南部武廟代表，設有五路財神殿。"}
            ],
            "台北市": [{"name": "台北行天宮", "feature": "不燒香心誠則靈，收驚安神。"}, {"name": "北投關渡宮", "feature": "財神洞非常有感，亦供奉關帝。"}],
            "新北市": [{"name": "金瓜石勸濟堂", "feature": "全台最大銅座關公，磁場強大。"}, {"name": "新莊武聖廟", "feature": "北部歷史悠久武廟，古蹟靈氣重。"}],
            "桃園市": [{"name": "大溪普濟堂", "feature": "關聖帝君聖誕慶典非常盛大。"}, {"name": "桃園明倫三聖宮", "feature": "虎頭山上的關帝廟，視野開闊。"}],
            "新竹市": [{"name": "古奇峰普天宮", "feature": "超大關公神像，新竹地標。"}, {"name": "新竹關帝廟", "feature": "都城隍廟旁，生意人必拜。"}],
            "台中市": [{"name": "台中南天宮", "feature": "巨大關公地標，補財庫首選。"}, {"name": "醒修宮", "feature": "台中老牌關帝廟，正氣十足。"}],
            "彰化縣": [{"name": "彰化關帝廟", "feature": "縣定古蹟，武聖靈驗。"}],
            "南投縣": [{"name": "日月潭文武廟", "feature": "風景秀麗，文武雙全。"}],
            "台南市": [{"name": "台灣祀典武廟", "feature": "官方祭祀武廟，地位崇高。"}, {"name": "龍崎文衡殿", "feature": "有鋼鐵人護駕的關帝廟，非常特別。"}],
            "高雄市": [{"name": "高雄關帝廟", "feature": "技擊館旁，求財求平安。"}, {"name": "鹽埕文武聖殿", "feature": "澎湖移民信仰中心，香火旺。"}],
            "宜蘭縣": [{"name": "礁溪協天廟", "feature": "北台灣重要關帝廟，蠶絲關公。"}],
            "花蓮縣": [{"name": "花蓮聖天宮", "feature": "花蓮在地知名關帝廟。"}],
            "台東縣": [{"name": "台東關帝廟", "feature": "後山武神，守護台東。"}],
        },

        # === 2. 媽祖 (人脈/貴人/平安) ===
        "mazu": {
             "all": [
                {"name": "大甲鎮瀾宮", "feature": "全台香火最鼎盛，媽祖慈悲。"},
                {"name": "白沙屯拱天宮", "feature": "粉紅超跑，進香活動最熱血。"},
                {"name": "北港朝天宮", "feature": "媽祖總本山，靈氣充足。"}
            ],
            "台北市": [{"name": "松山慈祐宮", "feature": "饒河夜市旁，香火極旺。"}, {"name": "關渡宮", "feature": "北台最老媽祖廟，財神洞必走。"}, {"name": "台北天后宮", "feature": "西門町守護神，鬧中取靜。"}],
            "新北市": [{"name": "板橋慈惠宮", "feature": "郭台銘發跡地，偏財運強。"}, {"name": "新莊慈祐宮", "feature": "新莊老街信仰中心。"}],
            "桃園市": [{"name": "中壢仁海宮", "feature": "中壢媽，在地信仰重鎮。"}, {"name": "桃園慈護宮", "feature": "桃園媽，守護北桃園。"}],
            "台中市": [{"name": "大甲鎮瀾宮", "feature": "國際宗教盛事，有求必應。"}, {"name": "旱溪樂成宮", "feature": "除了媽祖靈，月老也超有名。"}, {"name": "萬和宮", "feature": "南屯老街三百餘年古廟。"}],
            "彰化縣": [{"name": "鹿港天后宮", "feature": "開台湄洲媽祖，古色古香。"}],
            "雲林縣": [{"name": "北港朝天宮", "feature": "世界三大媽祖廟之一。"}],
            "嘉義縣": [{"name": "新港奉天宮", "feature": "開臺媽祖，虎爺也很有名。"}],
            "台南市": [{"name": "大天后宮", "feature": "官方祭祀天后宮。"}, {"name": "鹿耳門聖母廟", "feature": "建築宏偉，像紫禁城一樣。"}, {"name": "安平開台天后宮", "feature": "安平古堡旁，靈氣十足。"}],
            "高雄市": [{"name": "旗津天后宮", "feature": "高雄最古老媽祖廟。"}, {"name": "鳳山雙慈亭", "feature": "鳳山在地信仰。"}],
            "屏東縣": [{"name": "屏東慈鳳宮", "feature": "阿猴媽祖，屏東市中心。"}],
            "宜蘭縣": [{"name": "南方澳南天宮", "feature": "金媽祖與玉媽祖聞名。"}],
        },

        # === 3. 保生大帝 (健康/固本/抗壓) ===
        "baosheng": {
            "all": [
                {"name": "大龍峒保安宮", "feature": "米其林三星推薦，醫神保生大帝。"},
                {"name": "台南學甲慈濟宮", "feature": "上白礁祭典，開基保生大帝。"}
            ],
            "台北市": [{"name": "大龍峒保安宮", "feature": "國定古蹟，求藥籤非常靈驗。"}],
            "新北市": [{"name": "樹林濟安宮", "feature": "樹林大廟，守護鄉里。"}, {"name": "永和保福宮", "feature": "建築雕刻精美，永和信仰中心。"}],
            "桃園市": [{"name": "新屋永安宮", "feature": "在地歷史悠久。"}],
            "台中市": [{"name": "台中元保宮", "feature": "大道公廟，香火鼎盛。"}],
            "嘉義市": [{"name": "嘉義仁武宮", "feature": "市定古蹟，環境清幽。"}],
            "台南市": [{"name": "祀典興濟宮", "feature": "可以向虎爺「換錢水」。"}, {"name": "學甲慈濟宮", "feature": "開基祖廟，神威顯赫。"}],
            "高雄市": [{"name": "鼓山亭", "feature": "苓雅寮大廟，保生大帝靈驗。"}, {"name": "大社保元宮", "feature": "歷史悠久，擁有特別的「搶孤」活動。"}],
        },
        
        # === 4. 虎爺/偏財 (現金流/業績) ===
        "tiger": {
            "all": [
                {"name": "南投竹山紫南宮", "feature": "求發財金首選，土地公與金雞母。"},
                {"name": "中和烘爐地", "feature": "24小時開放，換錢母，看夜景。"},
                {"name": "北港武德宮", "feature": "五路財神與黑虎將軍。"}
            ],
            "台北市": [{"name": "松山慈祐宮", "feature": "虎爺在正殿，業務員愛來拜。"}, {"name": "北投關渡宮", "feature": "綿延的財神洞，補財庫必走。"}],
            "新北市": [{"name": "石碇五路財神廟", "feature": "虎爺愛吃香腸雞蛋，求偏財。"}, {"name": "中和烘爐地", "feature": "爬樓梯換財氣，土地公超靈。"}, {"name": "板橋慈惠宮", "feature": "發財金很有名。"}],
            "桃園市": [{"name": "南崁五福宮", "feature": "天官武財神，鎮廟之寶「天爐」。"}],
            "台中市": [{"name": "台中廣天宮", "feature": "財神開基祖廟，位階很高。"}],
            "嘉義縣": [{"name": "新港奉天宮", "feature": "桌上金虎爺，換錢水財源滾滾。"}],
            "屏東縣": [{"name": "車城福安宮", "feature": "全台最大土地公廟，自動點鈔機金爐。"}],
        },

        # === 5. 三太子 (創新/動力/突破) ===
        "prince": {
            "all": [
                {"name": "新營太子宮", "feature": "太子爺總廟，分靈無數。"},
                {"name": "高雄三鳳宮", "feature": "南台太子廟代表。"}
            ],
            "台北市": [{"name": "社子島坤天亭", "feature": "在地知名太子廟。"}],
            "桃園市": [{"name": "桃園護國宮", "feature": "獨腳太子，辦事非常靈驗。"}],
            "新竹市": [{"name": "指澤宮", "feature": "廣澤尊王與太子爺。"}],
            "高雄市": [{"name": "三鳳宮", "feature": "建築宏偉，年輕人創業必拜。"}],
            "台南市": [{"name": "沙淘宮", "feature": "府城頂太子，歷史悠久。"}, {"name": "昆沙宮", "feature": "府城下太子，神像精美。"}],
        },

        # === 6. 月老 (人緣/桃花) ===
        "yuelao": {
            "all": [{"name": "台北霞海城隍廟", "feature": "全台最強月老之一，效率極高。"}],
            "台北市": [{"name": "霞海城隍廟", "feature": "大稻埕求姻緣聖地。"}, {"name": "艋舺龍山寺", "feature": "月老靈驗，紅線很搶手。"}],
            "台中市": [{"name": "慈德慈惠堂", "feature": "專斬爛桃花，職場防小三。"}, {"name": "樂成宮", "feature": "求復合、求正緣非常有名。"}],
            "台南市": [{"name": "大天后宮", "feature": "緣粉有名，求貴人牽線。"}, {"name": "祀典武廟", "feature": "月老專打爛桃花，求正緣。"}, {"name": "重慶寺", "feature": "醋矸攪動，挽回感情。"}],
            "高雄市": [{"name": "關帝廟", "feature": "月老殿貼滿姻緣簿。"}],
        },

        # === 7. 文昌 (升遷/考試) ===
        "wenchang": {
            "all": [{"name": "台北文昌宮", "feature": "求升遷考試首選。"}],
            "台北市": [{"name": "台北文昌宮", "feature": "雙連捷運旁，香火鼎盛。"}, {"name": "關渡宮", "feature": "文昌帝君靈驗。"}],
            "新北市": [{"name": "新莊文昌祠", "feature": "大台北歷史悠久文昌廟。"}],
            "台南市": [{"name": "赤崁樓文昌閣", "feature": "魁星爺點名，榜上有名。"}],
            "高雄市": [{"name": "文武聖殿", "feature": "文昌與關帝同祀，文武雙全。"}],
        }
    }
    
    return db.get(god_key, {})

# --- 4. 核心演算法 (V15.0 隨機洗牌版) ---
def analyze_destiny_v15(birth_date, birth_time, user_location):
    # A. 基礎排盤
    solar = Solar.fromYmdHms(birth_date.year, birth_date.month, birth_date.day, birth_time.hour, birth_time.minute, 0)
    lunar = solar.getLunar()
    ba_zi = [lunar.getYearInGanZhi(), lunar.getMonthInGanZhi(), lunar.getDayInGanZhi(), lunar.getTimeInGanZhi()]
    day_master = lunar.getDayGan()
    month = birth_date.month
    
    # B. 流年分析
    current_date = datetime.now()
    current_lunar = Lunar.fromDate(current_date)
    current_year_gan = current_lunar.getYearGan() 
    current_year_str = f"{current_year_gan}{current_lunar.getYearZhi()}" 
    
    wuxing = {"甲":"木", "乙":"木", "丙":"火", "丁":"火", "戊":"土", "己":"土", "庚":"金", "辛":"金", "壬":"水", "癸":"水"}
    dm_elem = wuxing[day_master]
    yr_elem = wuxing[current_year_gan]

    relation = ""
    if dm_elem == yr_elem: relation = "比劫"
    elif (dm_elem=="木" and yr_elem=="火") or (dm_elem=="火" and yr_elem=="土") or (dm_elem=="土" and yr_elem=="金") or (dm_elem=="金" and yr_elem=="水") or (dm_elem=="水" and yr_elem=="木"): relation = "食傷"
    elif (dm_elem=="木" and yr_elem=="土") or (dm_elem=="火" and yr_elem=="金") or (dm_elem=="土" and yr_elem=="水") or (dm_elem=="金" and yr_elem=="木") or (dm_elem=="水" and yr_elem=="火"): relation = "財星"
    elif (dm_elem=="木" and yr_elem=="金") or (dm_elem=="火" and yr_elem=="水") or (dm_elem=="土" and yr_elem=="木") or (dm_elem=="金" and yr_elem=="火") or (dm_elem=="水" and yr_elem=="土"): relation = "官殺"
    else: relation = "印星"

    fortune_title = ""
    fortune_desc = ""
    fortune_keyword = ""

    # C. 神老闆配對邏輯 (加入新神明)
    main_god = {}
    sec_god = {}
    
    if relation == "比劫":
        fortune_keyword = "廣結善緣"
        fortune_title = f"{current_year_str}年是您的【人脈競爭年】"
        fortune_desc = "競爭大，朋友多。建議拜**月老**求好人緣，或**武財神**守財。"
        main_god = {"name": "月下老人", "key": "yuelao", "role": "職場人緣"}
        sec_god = {"name": "武財神", "key": "guan_gong", "role": "防範小人"}
        
    elif relation == "食傷":
        fortune_keyword = "才華洋溢"
        fortune_title = f"{current_year_str}年是您的【表現發揮年】"
        fortune_desc = "才華擋不住，但易過勞。建議拜**文昌**理清思緒，或**保生大帝**顧身。"
        main_god = {"name": "文昌帝君", "key": "wenchang", "role": "思緒清晰"}
        sec_god = {"name": "保生大帝", "key": "baosheng", "role": "避免過勞"}
        
    elif relation == "財星":
        fortune_keyword = "財源滾滾"
        fortune_title = f"{current_year_str}年是您的【收穫得財年】"
        fortune_desc = "財氣旺，是衝刺業績的好年。建議拜**虎爺**咬錢，**關公**守庫。"
        main_god = {"name": "武財神", "key": "guan_gong", "role": "鎮守財庫"}
        sec_god = {"name": "黑虎將軍", "key": "tiger", "role": "加強偏財"}
        
    elif relation == "官殺":
        fortune_keyword = "責任升遷"
        fortune_title = f"{current_year_str}年是您的【壓力升遷年】"
        fortune_desc = "壓力大但能升官。建議拜**太子爺**突破，或**文昌**助考核。"
        main_god = {"name": "三太子", "key": "prince", "role": "抗壓突破"}
        sec_god = {"name": "文昌帝君", "key": "wenchang", "role": "升官考核"}
        
    else: # 印星
        fortune_keyword = "貴人提攜"
        fortune_title = f"{current_year_str}年是您的【沉澱學習年】"
        fortune_desc = "適合進修，長輩緣佳。建議拜**媽祖**接貴人，或**文昌**進修。"
        main_god = {"name": "天上聖母", "key": "mazu", "role": "接引貴人"}
        sec_god = {"name": "文昌帝君", "key": "wenchang", "role": "進修學習"}

    # D. 候選人名單產生 (智慧隨機洗牌)
    final_list = []
    
    # 1. 取得主神的所有資料 (全台+在地)
    main_db = get_god_temple_list(main_god['key'])
    sec_db = get_god_temple_list(sec_god['key'])
    
    # 2. 挑選主神 (在地優先，隨機排序)
    main_local_candidates = main_db.get(user_location, [])
    main_all_candidates = main_db.get("all", [])
    
    # 洗牌！讓每次結果可能不同
    random.shuffle(main_local_candidates) 
    random.shuffle(main_all_candidates)
    
    # 先加在地的
    for t in main_local_candidates:
        if len(final_list) >= 1: break # 主神在地至少取 1 間
        t['type'] = 'main'
        final_list.append(t)
        
    # 如果在地不夠，或者需要補滿 2 間主神，從全台清單抓
    for t in main_all_candidates:
        if len(final_list) >= 2: break # 主神總共取 2 間
        if t['name'] not in [x['name'] for x in final_list]:
            t['type'] = 'main'
            final_list.append(t)
            
    # 3. 挑選輔神 (取 1 間)
    sec_local_candidates = sec_db.get(user_location, [])
    sec_all_candidates = sec_db.get("all", [])
    
    random.shuffle(sec_local_candidates)
    random.shuffle(sec_all_candidates)
    
    # 優先找在地輔神
    sec_found = False
    for t in sec_local_candidates:
        if t['name'] not in [x['name'] for x in final_list]:
            t['type'] = 'sec'
            final_list.append(t)
            sec_found = True
            break
            
    # 沒有在地輔神，就找全台輔神
    if not sec_found:
        for t in sec_all_candidates:
            if t['name'] not in [x['name'] for x in final_list]:
                t['type'] = 'sec'
                final_list.append(t)
                break
            
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
    data = analyze_destiny_v15(b_date, b_time, user_loc)

    # 1. IG 截圖專用卡 (純文字版)
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
    
    # 2. 分享區
    c_share1, c_share2 = st.columns([3, 1])
    with c_share1: st.text_input("🔗 複製連結", value="https://god-map.streamlit.app", disabled=True)
    with c_share2: st.link_button("IG 發文", "https://instagram.com/")
    st.markdown("---")
    
    # 3. 推薦清單 (隨機排序後結果)
    st.markdown(f"<h3 style='color:#D4AF37;'>⛩️ 您的專屬參拜清單</h3>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:#AAA; font-size:14px;'>根據流年與地緣關係，系統為您隨機精選 3 間廟宇：</p>", unsafe_allow_html=True)

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

    # 4. 底部
    st.write("")
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1: st.link_button(f"🛒 購買 {data['main_god']['name']} 開運物", data['product_link'])
    with c2: 
        if agree: st.link_button("📝 領取 2026 完整運勢報告", "https://forms.google.com/")