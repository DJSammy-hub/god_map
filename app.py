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

# --- 2. CSS 美化 (黑金風格 - 針對三欄卡片優化) ---
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
    
    /* 推薦廟宇卡片 */
    .temple-card {
        background-color: #262730; 
        color: #E0E0E0; 
        padding: 20px;
        border-radius: 10px; 
        border-top: 5px solid #D4AF37; 
        margin-bottom: 15px;
        transition: transform 0.2s;
    }
    .temple-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 5px 15px rgba(212, 175, 55, 0.3);
    }
    
    .feature-tag {
        background-color: #333; color: #AAA; 
        padding: 5px 10px; border-radius: 5px; 
        font-size: 13px; margin-top: 8px; display: block;
    }

    .stButton>button {
        width: 100%; background: linear-gradient(90deg, #D4AF37 0%, #AA8C2C 100%);
        color: #000; font-weight: bold; border: none; padding: 15px; font-size: 18px;
    }
    a { text-decoration: none; }
</style>
""", unsafe_allow_html=True)

# --- 3. 核心資料庫 (神老闆名單 - 擴充版) ---
# 為了避免語法錯誤，我們使用函數來產生資料
def get_god_data(god_key):
    # 定義全台通用的「總廟/大廟」，當在地廟宇不足3間時，用這些來補
    famous_backups = {
        "guan_gong": [
            {"name": "雲林北港武德宮", "feature": "全台武財神開基祖廟，擁有巨大天庫金爐，求財氣必去。"},
            {"name": "台北行天宮", "feature": "北台灣香火最鼎盛，不燒金紙，收驚靈驗，適合求事業穩定。"},
            {"name": "高雄關帝廟", "feature": "南台灣著名武廟，設有財神殿，許多業務與生意人必拜。"}
        ],
        "mazu": [
            {"name": "台中大甲鎮瀾宮", "feature": "全台最知名的媽祖廟之一，香火極旺，適合求平安與開運。"},
            {"name": "雲林北港朝天宮", "feature": "國定古蹟，媽祖信仰的總本山，靈氣充足，有求必應。"},
            {"name": "板橋慈惠宮", "feature": "郭台銘發跡廟，適合求創業順利、貴人相助。"}
        ],
        "tiger": [
            {"name": "石碇五路財神廟", "feature": "求偏財首選，虎爺愛吃生雞蛋與香腸，適合業務與投資者。"},
            {"name": "嘉義新港奉天宮", "feature": "少數供奉在桌上的「金虎爺」，可換錢水，財氣滿滿。"},
            {"name": "北港武德宮", "feature": "黑虎將軍的大本營，咬錢速度快，適合急需周轉者。"}
        ],
        "prince": [
            {"name": "台南新營太子宮", "feature": "全台太子爺總廟，神像數以萬計，能量場強大，求動力首選。"},
            {"name": "高雄三鳳宮", "feature": "南台灣著名太子廟，建築壯觀，適合求創新靈感與突破。"},
            {"name": "桃園護國宮", "feature": "北台灣知名太子廟，獨特的「獨腳太子」，辦事靈驗。"}
        ]
    }
    return famous_backups.get(god_key, [])

def get_local_temples(god_key, city):
    # 這裡定義各縣市的「在地精選」
    # 格式：(城市, 神明key): [廟1, 廟2...]
    # 為了簡潔，這裡列舉主要城市，其他城市會自動使用「全台推薦」來補足
    
    local_db = {
        # --- 關公 (武財神) ---
        ("guan_gong", "台北市"): [
            {"name": "台北行天宮", "feature": "恩主公信仰中心，正氣凜然，適合求正財、職場升遷。"},
            {"name": "北投關渡宮", "feature": "雖主祀媽祖，但其財神洞非常有名，亦供奉關帝。"}
        ],
        ("guan_gong", "新北市"): [
            {"name": "金瓜石勸濟堂", "feature": "擁全台最大純銅關公像，坐山望海，磁場宏大。"},
            {"name": "新莊武聖廟", "feature": "北部歷史悠久的武廟，古蹟靈氣重，適合求穩健發展。"}
        ],
        ("guan_gong", "台中市"): [
            {"name": "台中南天宮", "feature": "巨大的關公地標，求財非常靈驗，補財庫首選。"},
            {"name": "旱溪樂成宮", "feature": "雖然是媽祖廟，但配祀的財神與關帝也香火鼎盛。"}
        ],
        ("guan_gong", "高雄市"): [
            {"name": "高雄關帝廟", "feature": "技擊館旁，設有五路財神殿，貼金牛活動非常受歡迎。"},
            {"name": "鳳山文衡殿", "feature": "在地歷史悠久，香火鼎盛，許多政治人物與商人都來拜。"}
        ],

        # --- 媽祖 ---
        ("mazu", "台北市"): [
            {"name": "松山慈祐宮", "feature": "饒河夜市旁，交通便利，適合求人緣、健康與平安。"},
            {"name": "關渡宮", "feature": "北台灣最古老媽祖廟之一，財神洞是最大特色。"}
        ],
        ("mazu", "新北市"): [
            {"name": "板橋慈惠宮", "feature": "許多企業家的發跡地，偏財運與貴人運特別強。"},
            {"name": "新莊慈祐宮", "feature": "新莊老街信仰中心，歷史悠久，守護在地繁榮。"}
        ],
        ("mazu", "台中市"): [
            {"name": "大甲鎮瀾宮", "feature": "國際級的宗教聖地，人潮眾多，陽氣最旺。"},
            {"name": "旱溪樂成宮", "feature": "以月老聞名，但媽祖正殿能量溫和，適合求人際和諧。"}
        ],

        # --- 虎爺/財神 ---
        ("tiger", "台北市"): [
            {"name": "松山慈祐宮", "feature": "虎爺供奉於正殿，許多業務會專程帶生雞蛋來拜。"},
            {"name": "北投關渡宮", "feature": "財神洞內的虎爺，咬錢能力一流。"}
        ],
        ("tiger", "新北市"): [
            {"name": "石碇五路財神廟", "feature": "金碧輝煌的財神廟，虎爺是這裡的超級明星。"},
            {"name": "中和烘爐地", "feature": "雖然主祀土地公，但其財神殿與虎爺求偏財非常靈驗。"}
        ],

        # --- 三太子 ---
        ("prince", "台北市"): [
            {"name": "社子島坤天亭", "feature": "在地知名的太子廟，適合求行車平安與工作動力。"},
        ],
        ("prince", "高雄市"): [
            {"name": "高雄三鳳宮", "feature": "全台最大太子廟之一，建築宏偉，適合年輕創業者。"}
        ],
        ("prince", "台南市"): [
            {"name": "新營太子宮", "feature": "太子爺的總本山，分靈無數，必朝聖之地。"},
            {"name": "沙淘宮", "feature": "府城歷史悠久的太子廟，見證台南發展。"}
        ]
    }
    
    return local_db.get((god_key, city), [])

# --- 4. 命理與配對邏輯 (智慧推薦版) ---
def analyze_destiny_v4(birth_date, birth_time, user_location):
    # A. 命盤計算
    solar = Solar.fromYmdHms(birth_date.year, birth_date.month, birth_date.day, birth_time.hour, birth_time.minute, 0)
    lunar = solar.getLunar()
    ba_zi = [lunar.getYearInGanZhi(), lunar.getMonthInGanZhi(), lunar.getDayInGanZhi(), lunar.getTimeInGanZhi()]
    month = birth_date.month
    
    # B. 判斷神老闆 (五行調候)
    if 2 <= month <= 4: # 春 (木旺缺金)
        god_name = "武財神 (關聖帝君)"
        god_key = "guan_gong"
        reason = "春木過旺，需金修剪。建議找【關聖帝君】當靠山，祂能斬斷職場爛桃花與小人，助您決策果斷。"
        lacking = "金 (決斷力)"
    elif 5 <= month <= 7: # 夏 (火旺缺水)
        god_name = "天上聖母 (媽祖)"
        god_key = "mazu"
        reason = "夏火過炎，需水調候。建議找【天上聖母】當靠山，祂能賜您圓融智慧，化解火爆脾氣，帶來好人緣。"
        lacking = "水 (智慧)"
    elif 8 <= month <= 10: # 秋 (金旺缺木)
        god_name = "黑虎將軍/武財神"
        god_key = "tiger"
        reason = "秋金肅殺，需木生發。建議找【黑虎將軍】當靠山，祂的爆發力能為您咬錢帶財，在僵局中殺出一條血路。"
        lacking = "木 (生機)"
    else: # 冬 (水旺缺火)
        god_name = "中壇元帥 (三太子)"
        god_key = "prince"
        reason = "冬水寒冷，需火暖局。建議找【中壇元帥】當靠山，祂的赤子之心與行動力，能為您驅除懶散，動力全開。"
        lacking = "火 (動力)"

    # C. 智慧配對 (湊滿 3 間)
    # 1. 先抓在地
    recommendations = get_local_temples(god_key, user_location)
    
    # 2. 抓全台知名 (備用)
    backups = get_god_data(god_key)
    
    # 3. 合併並去重 (如果在地不夠3間，就從備用清單補)
    final_list = recommendations[:] # 複製一份
    existing_names = [r["name"] for r in final_list]
    
    for backup in backups:
        if len(final_list) >= 3:
            break
        if backup["name"] not in existing_names:
            final_list.append(backup)
            
    return {
        "ba_zi": ba_zi,
        "lacking": lacking,
        "god": god_name,
        "temple_list": final_list, # 這裡現在是一個 list
        "reason": reason,
        "product_link": f"https://shopline.com/search?q={god_key}" 
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
    user_loc = st.selectbox("🏠 居住縣市 (為您推薦在地 + 知名大廟)", taiwan_locations)
    
    agree = st.checkbox("我同意將匿名數據提供給「神職應援團」做統計分析")
    
    submit = st.form_submit_button("🔍 尋找我的神老闆")

if submit:
    with st.spinner('⏳ 正在連線天干地支資料庫...'):
        time_module.sleep(0.8)
    data = analyze_destiny_v4(b_date, b_time, user_loc)

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

    # 2. 命格診斷
    st.markdown(f"""
    <div class="result-card" style="border-left: 5px solid #E63946;">
        <h3 style="color:#D4AF37;">🔮 命局診斷</h3>
        <p>依據八字調候，您目前命局最欠缺 <span style="color:#E63946; font-weight:bold;">【{data['lacking']}】</span> 能量。</p>
        <p>{data['reason']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 3. 推薦神老闆 (三張卡片)
    st.markdown(f"<h3 style='color:#D4AF37; margin-top:30px;'>⛩️ 推薦您參拜 {data['god']}</h3>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:#AAA; font-size:14px;'>以下為您精選 3 間最適合的辦事處：</p>", unsafe_allow_html=True)

    # 使用迴圈顯示 3 間廟
    for i, temple in enumerate(data['temple_list']):
        with st.expander(f"📍 推薦 {i+1}：{temple['name']}", expanded=True):
            st.markdown(f"""
            <div style="margin-bottom:10px;">
                <b>{temple['name']}</b>
                <span class="feature-tag">💡 {temple['feature']}</span>
            </div>
            """, unsafe_allow_html=True)
            
            # 按鈕連結
            map_query = f"{temple['name']}"
            st.link_button(f"🗺️ 導航去 {temple['name']}", f"https://www.google.com/maps/search/?api=1&query={map_query}")

    # 4. 導購與表單
    st.write("")
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
         st.link_button(f"🛒 購買 {data['god']} 聯名戰袍", data['product_link'])
    with c2:
        if agree:
             st.link_button("📝 免費領取 2026 流年運勢", "https://forms.google.com/")