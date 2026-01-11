import streamlit as st
import os
import time
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ==============================================================================
#  1. MOBILE-FIRST UI DESIGN
# ==============================================================================
st.set_page_config(page_title="AI 1.0", layout="centered", page_icon="📱")

# CSS: AMOLED Dark Mode, Big Buttons, Modern Inputs
st.markdown("""
    <style>
    /* Main Background - Deep Black for OLED */
    .stApp { background-color: #000000; color: white; }
    
    /* Hide Header/Footer */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Modern Title */
    h1 {
        background: -webkit-linear-gradient(45deg, #00d4ff, #005bea);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        font-weight: 800;
        font-family: 'Helvetica Neue', sans-serif;
        margin-bottom: 30px;
    }

    /* Input Fields styling */
    div[data-baseweb="input"] {
        background-color: #1a1a1a !important;
        border: 1px solid #333 !important;
        border-radius: 12px !important;
        color: white !important;
    }
    
    /* The Big Action Button */
    div.stButton > button {
        background: linear-gradient(90deg, #00d4ff 0%, #005bea 100%);
        color: white;
        border: none;
        padding: 15px 0;
        border-radius: 50px;
        font-size: 18px;
        font-weight: bold;
        width: 100%;
        box-shadow: 0 4px 15px rgba(0, 212, 255, 0.4);
        transition: transform 0.2s;
    }
    div.stButton > button:active { transform: scale(0.96); }

    /* Glass Logs Container */
    .log-container {
        margin-top: 20px;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 15px;
        height: 250px;
        overflow-y: scroll;
        font-family: 'Courier New', monospace;
        font-size: 12px;
    }

    /* File Uploader styling */
    div[data-testid="stFileUploader"] {
        background-color: #111;
        border-radius: 15px;
        padding: 10px;
        border: 1px dashed #444;
    }
    
    .status-line { margin-bottom: 5px; border-bottom: 1px solid #222; padding-bottom: 2px; }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
#  2. ROBUST CLOUD ENGINE
# ==============================================================================
def get_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    
    # CRITICAL FIX FOR ERROR 127 ON CLOUD
    # We point directly to the installed system chromium
    options.binary_location = "/usr/bin/chromium"
    
    service = Service("/usr/bin/chromedriver")
    return webdriver.Chrome(service=service, options=options)

def run_automation(uid, pwd, uploaded_files):
    log_ph = st.empty()
    logs = []

    def log(msg, color="#ffffff"):
        ts = time.strftime('%H:%M:%S')
        logs.insert(0, f"<div class='status-line' style='color:{color}'><b>[{ts}]</b> {msg}</div>")
        log_ph.markdown(f"<div class='log-container'>{''.join(logs)}</div>", unsafe_allow_html=True)

    def force_click(driver, element):
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", element)

    # 1. Handle Files
    temp_dir = "temp_data"
    if os.path.exists(temp_dir): shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)
    
    for f in uploaded_files:
        with open(os.path.join(temp_dir, f.name), "wb") as w: w.write(f.getbuffer())

    driver = None
    try:
        log("🚀 INITIALIZING CLOUD ENGINE...", "#00d4ff")
        driver = get_driver()
        wait = WebDriverWait(driver, 30)
        
        log("🌐 CONNECTING TO LMS...", "#aaaaaa")
        driver.get("https://lms3.aiou.edu.pk/my/courses.php")
        
        # LOGIN
        if "microsoftonline" in driver.current_url:
            log("🔐 AUTHENTICATING...", "#ffcc00")
            wait.until(EC.visibility_of_element_located((By.NAME, "loginfmt"))).send_keys(uid)
            wait.until(EC.element_to_be_clickable((By.ID, "idSIButton9"))).click(); time.sleep(2)
            pf = wait.until(EC.visibility_of_element_located((By.NAME, "passwd")))
            pf.click(); pf.send_keys(pwd)
            wait.until(EC.element_to_be_clickable((By.ID, "idSIButton9"))).click(); time.sleep(2)
            try: wait.until(EC.element_to_be_clickable((By.ID, "idSIButton9"))).click()
            except: pass

        log("✅ ACCESS GRANTED", "#00ff9d")
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "coursename")))

        # MAPPING
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

        log(f"📋 {len(tasks)} COURSES DETECTED", "#00d4ff")

        # PROCESSING
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
                fpath = os.path.join(temp_dir, fname)
                
                if not os.path.exists(fpath): continue
                
                driver.get(aurl)
                if "Submitted for grading" in driver.find_element(By.TAG_NAME, "body").text:
                    log(f"✔ {fname} Already Done", "#555")
                    continue
                
                try:
                    log(f"📤 Uploading {fname}...", "#ffcc00")
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
                    force_click(driver, sb)
                    time.sleep(4)
                    
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
                except Exception as e: log(f"❌ Error: {e}", "#ff4b4b")

    except Exception as e: log(f"CRITICAL: {e}", "red")
    finally:
        if driver: driver.quit()
        if os.path.exists(temp_dir): shutil.rmtree(temp_dir)
        log("🏁 PROCESS FINISHED", "white")

# ==============================================================================
#  3. MAIN APP FLOW
# ==============================================================================
st.markdown("<h1>AI 1.0 ULTIMATE</h1>", unsafe_allow_html=True)

if "auth" not in st.session_state: st.session_state["auth"] = False

if not st.session_state["auth"]:
    st.markdown("<br>", unsafe_allow_html=True)
    code = st.text_input("ACCESS CODE", type="password", label_visibility="collapsed", placeholder="Enter Code")
    if st.button("UNLOCK SYSTEM"):
        if code == "Aksji2014": st.session_state["auth"] = True; st.rerun()
        else: st.error("ACCESS DENIED")
else:
    uid = st.text_input("User ID", placeholder="User ID")
    pwd = st.text_input("Password", type="password", placeholder="Password")
    
    st.markdown("<br><b>Select Assignment PDFs</b>", unsafe_allow_html=True)
    files = st.file_uploader("Drop files here", type="pdf", accept_multiple_files=True, label_visibility="collapsed")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("START AUTOMATION"):
        if uid and pwd and files:
            run_automation(uid, pwd, files)
        else:
            st.warning("Please provide Credentials and Files")

    st.markdown("<br><div style='text-align:center; color:#333; font-size:10px;'>Asif Lashari | 2026</div>", unsafe_allow_html=True)
