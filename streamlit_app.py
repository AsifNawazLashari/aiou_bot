import streamlit as st
import os
import time
import shutil
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ==============================================================================
#  1. OCEAN UI DESIGN (NATIVE ANDROID FEEL)
# ==============================================================================
st.set_page_config(page_title="AI 1.0 Ocean", layout="centered", page_icon="🌊", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    /* 1. MAIN BACKGROUND (Deep Ocean Gradient) */
    .stApp {
        background: linear-gradient(180deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
        color: white;
        font-family: 'Roboto', sans-serif;
    }

    /* 2. REMOVE WEB ELEMENTS (Native App Feel) */
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* 3. GLASSMORPHISM PANELS (Water Effect) */
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }

    /* 4. BEAUTIFUL BUTTONS (Ocean Cyan) */
    div.stButton > button {
        background: linear-gradient(90deg, #00c6ff 0%, #0072ff 100%);
        color: white;
        border: none;
        padding: 15px;
        border-radius: 50px; /* Pill shape */
        font-size: 16px;
        font-weight: 700;
        letter-spacing: 1px;
        width: 100%;
        box-shadow: 0 4px 15px rgba(0, 198, 255, 0.4);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    div.stButton > button:active {
        transform: scale(0.96);
        box-shadow: 0 2px 10px rgba(0, 198, 255, 0.2);
    }

    /* 5. INPUT FIELDS (Transparent) */
    div[data-baseweb="input"] {
        background-color: rgba(0, 0, 0, 0.3) !important;
        border: 1px solid rgba(0, 255, 255, 0.3) !important;
        border-radius: 12px !important;
        color: white !important;
    }
    
    /* 6. HEADERS */
    h1, h2, h3 {
        color: #00d2ff !important;
        text-shadow: 0 0 10px rgba(0, 210, 255, 0.5);
        text-align: center;
    }
    
    /* 7. FOOTER CREDIT */
    .credits {
        position: fixed;
        left: 0; bottom: 0; width: 100%;
        background: rgba(15, 32, 39, 0.95);
        color: #00d2ff;
        text-align: center;
        padding: 10px;
        font-size: 11px;
        border-top: 1px solid #00d2ff;
        z-index: 999;
    }

    /* 8. LOGS */
    .log-text {
        font-family: 'Courier New', monospace;
        font-size: 12px;
        margin-bottom: 4px;
        border-bottom: 1px solid rgba(255,255,255,0.05);
        padding-bottom: 2px;
    }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
#  2. PROFILE MANAGER (SAVE ACCOUNTS)
# ==============================================================================
PROFILE_FILE = "ocean_profiles.json"

def load_profiles():
    if os.path.exists(PROFILE_FILE):
        with open(PROFILE_FILE, "r") as f: return json.load(f)
    return {}

def save_profile_to_disk(name, u, p):
    data = load_profiles()
    data[name] = {"u": u, "p": p}
    with open(PROFILE_FILE, "w") as f: json.dump(data, f)

# ==============================================================================
#  3. CLOUD AUTOMATION ENGINE
# ==============================================================================
def get_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    # CLOUD BINARY PATHS
    options.binary_location = "/usr/bin/chromium"
    service = Service("/usr/bin/chromedriver")
    return webdriver.Chrome(service=service, options=options)

def run_automation(uid, pwd, files):
    log_ph = st.empty()
    logs = []
    
    def log(m, c="#fff"):
        t = time.strftime('%H:%M')
        logs.insert(0, f"<div class='log-text' style='color:{c}'><b>{t}</b> | {m}</div>")
        log_ph.markdown(f"<div class='glass-card' style='height:250px; overflow-y:scroll;'>{''.join(logs)}</div>", unsafe_allow_html=True)

    def force_click(driver, elem):
        driver.execute_script("arguments[0].scrollIntoView(true);arguments[0].click();", elem)

    # File Handling
    temp = "ocean_temp"
    if os.path.exists(temp): shutil.rmtree(temp)
    os.makedirs(temp)
    for f in files:
        with open(os.path.join(temp, f.name), "wb") as w: w.write(f.getbuffer())

    driver = None
    try:
        log("🌊 INITIALIZING ENGINE...", "#00d2ff")
        driver = get_driver()
        wait = WebDriverWait(driver, 40)
        
        log("🌐 CONNECTING TO SERVER...", "#fff")
        driver.get("https://lms3.aiou.edu.pk/my/courses.php")
        
        if "microsoftonline" in driver.current_url:
            log("🔐 AUTHENTICATING...", "#ffaa00")
            wait.until(EC.visibility_of_element_located((By.NAME, "loginfmt"))).send_keys(uid)
            wait.until(EC.element_to_be_clickable((By.ID, "idSIButton9"))).click(); time.sleep(2)
            pf = wait.until(EC.visibility_of_element_located((By.NAME, "passwd")))
            pf.click(); pf.send_keys(pwd)
            wait.until(EC.element_to_be_clickable((By.ID, "idSIButton9"))).click(); time.sleep(2)
            try: wait.until(EC.element_to_be_clickable((By.ID, "idSIButton9"))).click()
            except: pass

        log("✅ DASHBOARD ACCESSED", "#00ff9d")
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "coursename")))

        links = driver.find_elements(By.CSS_SELECTOR, "a.aalink.coursename")
        amap = {}; tasks = []
        for l in links:
            t = l.get_attribute('innerText').strip()
            if "|" in t: 
                p = t.split("|")
                if len(p)>=3: amap[''.join(e for e in p[2].upper() if e.isalnum())] = p[0].strip().split()[-1]
        
        for l in links:
            t = l.get_attribute('innerText').strip()
            url = l.get_attribute("href")
            if "|" not in t and len(t)>3:
                ct = ''.join(e for e in t.upper() if e.isalnum())
                mc = amap.get(ct)
                if not mc:
                    for k,v in amap.items():
                        if ct in k: mc=v; break
                if mc: tasks.append((mc, url))

        log(f"📋 {len(tasks)} COURSES FOUND", "#00d2ff")

        for code, url in tasks:
            driver.get(url)
            alist = []
            fl = driver.find_elements(By.PARTIAL_LINK_TEXT, "ASSIGNMENT")
            if not fl: fl = driver.find_elements(By.XPATH, "//a[contains(translate(., 'a-z', 'A-Z'), 'ASSIGNMENT')]")
            for x in fl:
                try: alist.append(("2" if "2" in x.text else "1", x.get_attribute("href")))
                except: pass
            
            for num, aurl in list(set(alist)):
                fname = f"{code}_{num}.pdf"
                fpath = os.path.join(temp, fname)
                
                if not os.path.exists(fpath): continue
                
                driver.get(aurl)
                if "Submitted for grading" in driver.find_element(By.TAG_NAME, "body").text:
                    log(f"✔ {fname} Already Done", "#888")
                    continue
                
                try:
                    log(f"🚀 Uploading {fname}...", "#ffcc00")
                    try:
                        btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Add submission') or contains(text(), 'Edit submission')]")))
                        force_click(driver, btn)
                    except: continue

                    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".fp-btn-add"))).click()
                    try: wait.until(EC.visibility_of_element_located((By.XPATH, "//span[contains(text(), 'Upload a file')]"))).click()
                    except: pass
                    
                    fi = wait.until(EC.presence_of_element_located((By.NAME, "repo_upload_file")))
                    fi.send_keys(fpath)
                    driver.find_element(By.NAME, "title").send_keys(f"{code}_{num}")
                    driver.find_element(By.CLASS_NAME, "fp-upload-btn").click()
                    time.sleep(8)
                    
                    sb = driver.find_element(By.NAME, "submitbutton")
                    force_click(driver, sb); time.sleep(5)
                    
                    try:
                        sbtn = driver.find_elements(By.XPATH, "//button[contains(text(), 'Submit assignment')]")
                        if sbtn:
                            force_click(driver, sbtn[0]); time.sleep(3)
                            force_click(driver, wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[value='Continue']"))))
                    except: pass
                    
                    try:
                        cl = driver.find_elements(By.LINK_TEXT, "Continue")
                        if cl: force_click(driver, cl[0])
                    except: pass

                    log(f"✨ SUCCESS: {fname}", "#00ff9d")
                except Exception as e: log(f"❌ Err: {e}", "#ff4444")

    except Exception as e: log(f"CRITICAL: {e}", "red")
    finally:
        if driver: driver.quit()
        if os.path.exists(temp): shutil.rmtree(temp)
        log("🏁 PROCESS COMPLETED", "#fff")

# ==============================================================================
#  4. MAIN UI LAYOUT
# ==============================================================================
if "auth" not in st.session_state: st.session_state["auth"] = False

if not st.session_state["auth"]:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("<h1>AI 1.0 SECURE</h1>", unsafe_allow_html=True)
    code = st.text_input("ACCESS CODE", type="password", placeholder="Enter Code")
    if st.button("UNLOCK SYSTEM"):
        if code == "Aksji2014": st.session_state["auth"] = True; st.rerun()
        else: st.error("INVALID CODE")
    st.markdown("</div>", unsafe_allow_html=True)
else:
    # HEADER
    st.markdown("<h1>AI 1.0 OCEAN</h1>", unsafe_allow_html=True)
    
    # --- ACCOUNT CARD ---
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("<h3>👤 Accounts</h3>", unsafe_allow_html=True)
    
    profiles = load_profiles()
    p_names = ["Select Saved Account"] + list(profiles.keys())
    selected = st.selectbox("Load Profile", p_names, label_visibility="collapsed")
    
    u_val, p_val = "", ""
    if selected != "Select Saved Account":
        u_val, p_val = profiles[selected]["u"], profiles[selected]["p"]

    c1, c2 = st.columns(2)
    with c1: uid = st.text_input("User ID", value=u_val)
    with c2: pwd = st.text_input("Password", value=p_val, type="password")
    
    with st.expander("Save New Account"):
        new_name = st.text_input("Profile Name (e.g. My ID)")
        if st.button("Save Account"):
            save_profile_to_disk(new_name, uid, pwd)
            st.success("Saved!")
            time.sleep(0.5)
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    # --- UPLOAD CARD ---
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("<h3>📂 Assignments</h3>", unsafe_allow_html=True)
    files = st.file_uploader("Select PDFs", type="pdf", accept_multiple_files=True, label_visibility="collapsed")
    st.markdown("</div>", unsafe_allow_html=True)

    # --- START BUTTON ---
    if st.button("🚀 INITIATE UPLOAD"):
        if uid and pwd and files:
            run_automation(uid, pwd, files)
        else:
            st.warning("Please provide Credentials and Files")

    st.markdown("<div class='credits'>Software Developed by <b>Asif Lashari</b> | 2026</div>", unsafe_allow_html=True)
