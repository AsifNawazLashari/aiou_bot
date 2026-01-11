import streamlit as st
import os
import time
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType

# ==============================================================================
#  UI CONFIGURATION
# ==============================================================================
st.set_page_config(page_title="AI 1.0 Ultimate", layout="centered", page_icon="🚀")

st.markdown("""
    <style>
    .stApp { background: #0f1116; color: white; }
    h1 { color: #00d4ff; text-align: center; font-family: 'Helvetica'; }
    .stButton>button {
        background: linear-gradient(90deg, #00d2ff 0%, #3a7bd5 100%);
        color: white; border: none; padding: 12px; border-radius: 8px; font-weight: bold; width: 100%;
    }
    .status-box { background: #1a1c24; padding: 15px; border-radius: 10px; border: 1px solid #333; font-family: monospace; height: 300px; overflow-y: scroll; }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
#  AUTOMATION ENGINE
# ==============================================================================
def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    
    # Cloud-Specific Installer
    return webdriver.Chrome(
        service=Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()),
        options=options
    )

def run_automation(uid, pwd, uploaded_files):
    log_container = st.empty()
    logs = []

    def log(msg, color="white"):
        logs.append(f"<div style='color:{color}'>[{time.strftime('%H:%M:%S')}] {msg}</div>")
        log_container.markdown(f"<div class='status-box'>{''.join(logs)}</div>", unsafe_allow_html=True)

    def force_click(driver, element):
        driver.execute_script("arguments[0].scrollIntoView(true);arguments[0].click();", element)

    # 1. Save Files Temporarily
    temp_dir = "temp_assignments"
    if os.path.exists(temp_dir): shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)
    
    for f in uploaded_files:
        with open(os.path.join(temp_dir, f.name), "wb") as w:
            w.write(f.getbuffer())

    try:
        log(">>> STARTING CLOUD ENGINE...", "#00d4ff")
        driver = get_driver()
        wait = WebDriverWait(driver, 30)
        
        log(">>> CONNECTING TO AIOU...", "yellow")
        driver.get("https://lms3.aiou.edu.pk/my/courses.php")
        
        # Login
        if "microsoftonline" in driver.current_url:
            log(">>> AUTHENTICATING...", "orange")
            wait.until(EC.visibility_of_element_located((By.NAME, "loginfmt"))).send_keys(uid)
            wait.until(EC.element_to_be_clickable((By.ID, "idSIButton9"))).click(); time.sleep(2)
            pf = wait.until(EC.visibility_of_element_located((By.NAME, "passwd")))
            pf.click(); pf.send_keys(pwd)
            wait.until(EC.element_to_be_clickable((By.ID, "idSIButton9"))).click(); time.sleep(2)
            try: wait.until(EC.element_to_be_clickable((By.ID, "idSIButton9"))).click()
            except: pass

        log(">>> ACCESS GRANTED", "#00ff9d")
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "coursename")))

        # Mapping
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

        log(f">>> {len(tasks)} COURSES DETECTED", "#00d4ff")

        for code, url in tasks:
            log(f"--- CHECKING {code} ---")
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
                
                if not os.path.exists(fpath):
                    log(f"Skipping {fname} (Not uploaded)", "grey")
                    continue
                
                driver.get(aurl)
                if "Submitted for grading" in driver.find_element(By.TAG_NAME, "body").text:
                    log(f"{fname}: Already Done", "#00ff9d")
                    continue

                try:
                    log(f"Uploading {fname}...", "yellow")
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

                    log(f"SUCCESS: {fname}", "#00ff9d")
                except Exception as e: log(f"Err: {e}", "red")

    except Exception as e: log(f"System Error: {e}", "red")
    finally:
        if 'driver' in locals(): driver.quit()
        # Cleanup files
        shutil.rmtree(temp_dir)
        log("JOB COMPLETE", "white")

# ==============================================================================
#  MAIN APP
# ==============================================================================
st.markdown("<h1>AI 1.0 ULTIMATE</h1>", unsafe_allow_html=True)

if "auth" not in st.session_state: st.session_state["auth"] = False

if not st.session_state["auth"]:
    code = st.text_input("Enter Access Code", type="password")
    if st.button("UNLOCK"):
        if code == "Aksji2014": st.session_state["auth"] = True; st.rerun()
        else: st.error("Access Denied")
else:
    # 1. Credentials
    c1, c2 = st.columns(2)
    with c1: uid = st.text_input("User ID")
    with c2: pwd = st.text_input("Password", type="password")

    # 2. File Uploader
    st.info("Select your PDF assignments. They will be uploaded securely.")
    files = st.file_uploader("Upload PDFs", type="pdf", accept_multiple_files=True)

    # 3. Start
    if st.button("START AUTO-UPLOAD"):
        if uid and pwd and files:
            run_automation(uid, pwd, files)
        else:
            st.error("Please provide Credentials and Files.")

st.markdown("<div class='footer'>Cloud Software by Asif Lashari | 2026</div>", unsafe_allow_html=True)
