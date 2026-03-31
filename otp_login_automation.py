
import uuid
import re
import time
import requests
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout




MAILSLURP_URL   = "https://playground.mailslurp.com/"
MAILTM_EMAIL    = "test11223344@sharebot.net"  # pnew email should be created for each test at Mailslurp
MAILTM_PASSWORD = "test@123"
ACCOUNT_PASSWORD = "test@123"   # password to use when creating mailslurp account
OTP_DIGITS      = 6
EMAIL_WAIT_TIMEOUT = 120        # seconds to wait for OTP email



#  STEP 0 — LOGIN TO mail.tm TO GET AUTH TOKEN
MAILSLURP_URL    = "https://playground.mailslurp.com/"
MAILTM_PASSWORD  = "test@123"
ACCOUNT_PASSWORD = "test@123"   # password to use when creating mailslurp account
OTP_DIGITS       = 6
EMAIL_WAIT_TIMEOUT = 120        # seconds to wait for OTP email

# Global variables that will be populated dynamically
MAILTM_EMAIL = ""

#  STEP -1 — DYNAMICALLY CREATE mail.tm ACCOUNT

def create_mailtm_account():
    global MAILTM_EMAIL
    print("\n" + "=" * 55)
    print("  STEP -1: Creating fresh mail.tm account")
    print("=" * 55)
    
    try:
        # 1. Get available domain
        dom_res = requests.get("https://api.mail.tm/domains").json()
        domain = dom_res["hydra:member"][0]["domain"]
        
        # 2. Generate random email address
        MAILTM_EMAIL = f"test_{uuid.uuid4().hex[:8]}@{domain}"
        
        # 3. Create the account
        requests.post("https://api.mail.tm/accounts", json={
            "address": MAILTM_EMAIL,
            "password": MAILTM_PASSWORD
        }).raise_for_status()
        
        # 4. Get the auth token
        token_res = requests.post("https://api.mail.tm/token", json={
            "address": MAILTM_EMAIL,
            "password": MAILTM_PASSWORD
        })
        token_res.raise_for_status()
        token = token_res.json()["token"]
        
        print(f"  Generated Email: {MAILTM_EMAIL} ✓")
        return token
    except Exception as e:
        raise Exception(f"Failed to create mail.tm account: {e}")

# def login_to_mailtm():
#     print("\n" + "=" * 55)
#     print("  STEP 0: Logging into mail.tm inbox")
#     print("=" * 55)
#     print(f"  Email : {MAILTM_EMAIL}")

#     try:
#         response = requests.post(
#             "https://api.mail.tm/token",
#             json={"address": MAILTM_EMAIL, "password": MAILTM_PASSWORD},
#             timeout=10
#         )
#         response.raise_for_status()
#         token = response.json()["token"]
#         print(f"  mail.tm login : Success ✓")
#         return token

#     except Exception as e:
#         raise Exception(f"Could not log into mail.tm: {e}")



#  STEP 1 — OPEN MAILSLURP AND CREATE ACCOUNT


def step1_create_account(page):
    print("\n" + "=" * 55)
    print("  STEP 1: Opening MailSlurp Playground")
    print("=" * 55)

    # Open the mailslurp playground
    page.goto(MAILSLURP_URL)
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(2000)
    print(f"  Page loaded : {page.url} ✓")

    # ── Click Sign Up button ──
    print("  Looking for Sign Up button...")
    signup_selectors = [
        "a:has-text('Sign up')",
        "a:has-text('Sign Up')",
        "button:has-text('Sign up')",
        "button:has-text('Sign Up')",
        "a:has-text('Register')",
        "a:has-text('Create account')",
        "a:has-text('Create Account')",
        "[href*='signup']",
        "[href*='register']",
    ]

    clicked = False
    for selector in signup_selectors:
        try:
            btn = page.locator(selector).first
            if btn.is_visible():
                btn.click()
                page.wait_for_load_state("networkidle")
                page.wait_for_timeout(1500)
                print(f"  Clicked signup : {selector} ✓")
                clicked = True
                break
        except Exception:
            continue

    if not clicked:
        print("  No signup button found — may already be on signup form, continuing...")

    # ── Fill in Email ──
    print(f"  Filling email : {MAILTM_EMAIL}")
    email_selectors = [
        "input[type='email']",
        "input[name='email']",
        "input[id='email']",
        "input[placeholder*='email' i]",
        "input[name='username']",
        "input[id='username']",
    ]

    email_filled = False
    for selector in email_selectors:
        try:
            field = page.locator(selector).first
            if field.is_visible():
                field.click()
                field.fill(MAILTM_EMAIL)
                email_filled = True
                print(f"  Email entered : {selector} ✓")
                break
        except Exception:
            continue

    if not email_filled:
        raise Exception(
            "Could not find the email input field on MailSlurp.\n"
            "The page layout may have changed. Take a screenshot and share it."
        )

    # ── Fill in Password ──
    print(f"  Filling password...")
    password_selectors = [
        "input[type='password']",
        "input[name='password']",
        "input[id='password']",
        "input[placeholder*='password' i]",
    ]

    password_filled = False
    for selector in password_selectors:
        try:
            field = page.locator(selector).first
            if field.is_visible():
                field.fill(ACCOUNT_PASSWORD)
                password_filled = True
                print(f"  Password entered : {selector} ✓")
                break
        except Exception:
            continue

    if not password_filled:
        print("  No password field found — site may only ask for email. Continuing...")

    # ── Click Create / Register / Submit button ──
    print("  Clicking Create Account button...")
    create_selectors = [
        "button:has-text('Create account')",
        "button:has-text('Create Account')",
        "button:has-text('Sign up')",
        "button:has-text('Sign Up')",
        "button:has-text('Register')",
        "button:has-text('Submit')",
        "button:has-text('Continue')",
        "input[type='submit']",
        "button[type='submit']",
    ]

    create_clicked = False
    for selector in create_selectors:
        try:
            btn = page.locator(selector).first
            if btn.is_visible():
                btn.click()
                create_clicked = True
                print(f"  Clicked : {selector} ✓")
                break
        except Exception:
            continue

    if not create_clicked:
        raise Exception(
            "Could not find the Create Account / Submit button.\n"
            "Share a screenshot of the page and I will fix the selector."
        )

    # ── Wait for OTP input to appear ──
    print("  Waiting for OTP input field to appear on screen...")
    page.wait_for_timeout(3000)

    otp_selectors = [
        "input[name='code']",
        "input[name='otp']",
        "input[id='code']",
        "input[id='otp']",
        "input[placeholder*='code' i]",
        "input[placeholder*='OTP' i]",
        "input[placeholder*='verification' i]",
        "input[maxlength='6']",
        "input[maxlength='4']",
        "input[type='number']",
    ]

    otp_appeared = False
    for selector in otp_selectors:
        try:
            page.wait_for_selector(selector, timeout=20000)
            otp_appeared = True
            print(f"  OTP input appeared : {selector} ✓")
            break
        except PlaywrightTimeout:
            continue

    if not otp_appeared:
        raise Exception(
            "OTP input field did not appear after creating the account.\n"
            "The email may not have been sent, or the OTP field uses a different selector.\n"
            "Share a screenshot of the current page."
        )



#  STEP 2 — WAIT FOR OTP EMAIL IN mail.tm


def step2_get_otp(token):
    print("\n" + "=" * 55)
    print(f"  STEP 2: Waiting for OTP email in mail.tm inbox")
    print("=" * 55)

    headers  = {"Authorization": f"Bearer {token}"}
    # Increased timeout to 5 minutes for slow networks
    EMAIL_WAIT_TIMEOUT = 300 
    deadline = time.time() + EMAIL_WAIT_TIMEOUT
    attempt  = 1

    while time.time() < deadline:
        print(f"  Check #{attempt} — polling inbox (Time left: {int(deadline - time.time())}s)...")
        try:
            # Increased timeout to 30s for slow connection
            inbox = requests.get("https://api.mail.tm/messages", headers=headers, timeout=30)
            inbox.raise_for_status()
            all_msgs = inbox.json().get("hydra:member", [])

            if not all_msgs:
                print("  [...] Inbox still empty. Waiting...")
            else:
                print(f"  {len(all_msgs)} email(s) found! Checking content...")
                msg_id = all_msgs[0]["id"]
                
                full = requests.get(f"https://api.mail.tm/messages/{msg_id}", headers=headers, timeout=30)
                data = full.json()
                
                # Get body and clean it
                text_body = data.get("text", "")
                html_body = data.get("html", [""])[0] if data.get("html") else ""
                raw_content = text_body if text_body.strip() else html_body
                
                clean = re.sub(r"<[^>]+>", " ", raw_content)
                print(f"  Email Subject: {data.get('subject')}")

                # Look for any 6-digit number
                match = re.search(r"(\d{6})", clean)
                if match:
                    otp = match.group(1)
                    print(f"  ✅ OTP extracted: {otp}")
                    return otp
                else:
                    print("  [!] Email arrived, but no 6-digit OTP found in text.")

        except Exception as e:
            print(f"  [!] Network/API error: {e}")

        attempt += 1
        time.sleep(8) # Wait 8 seconds between retries to give the network a break

    raise TimeoutError(f"OTP did not arrive within {EMAIL_WAIT_TIMEOUT} seconds.")


#  STEP 3 — TYPE OTP INTO MAILSLURP AND SUBMIT


def step3_submit_otp(page, otp):
    print("\n" + "=" * 55)
    print(f"  STEP 3: Entering OTP into MailSlurp")
    print("=" * 55)
    print(f"  OTP : {otp}")

    otp_selectors = [
        "input[name='code']",
        "input[name='otp']",
        "input[id='code']",
        "input[id='otp']",
        "input[placeholder*='code' i]",
        "input[placeholder*='OTP' i]",
        "input[placeholder*='verification' i]",
        "input[maxlength='6']",
        "input[maxlength='4']",
        "input[type='number']",
    ]

    otp_typed = False
    for selector in otp_selectors:
        try:
            field = page.locator(selector).first
            if field.is_visible():
                field.click()
                field.fill(otp)
                otp_typed = True
                print(f"  OTP typed : {selector} ✓")
                break
        except Exception:
            continue

    if not otp_typed:
        raise Exception("Could not find OTP input field to type into.")

    # Click Verify / Confirm / Submit
    verify_selectors = [
        "button:has-text('Verify')",
        "button:has-text('Confirm')",
        "button:has-text('Submit')",
        "button:has-text('Continue')",
        "button:has-text('Login')",
        "button:has-text('Sign in')",
        "input[type='submit']",
        "button[type='submit']",
    ]

    for selector in verify_selectors:
        try:
            btn = page.locator(selector).first
            if btn.is_visible():
                btn.click()
                print(f"  Clicked submit : {selector} ✓")
                break
        except Exception:
            continue

    page.wait_for_load_state("networkidle")
    time.sleep(2)

    page.screenshot(path="login_result.png")
    print(f"\n  Final URL  : {page.url}")
    print(f"  Screenshot : login_result.png ✓")

def step_4_login_back(page, email):
    print("\n" + "=" * 55)
    print("  STEP 4: Force Loading Login")
    print("=" * 55)
    
    # Force a direct hit to the login URL
    page.goto("https://playground.mailslurp.com/login", wait_until="commit")
    page.wait_for_timeout(5000) # Wait for JS to settle
    
    if "NoSuchKey" in page.content():
        print("  [!] Server error detected. Forced Reloading...")
        page.reload()
        page.wait_for_timeout(5000)

    # Use the 'username' field specifically
    try:
        page.locator("input[name='username']").fill(email)
        page.locator("input[name='password']").fill(ACCOUNT_PASSWORD)
        page.get_by_role("button", name="Log in").click()
        
        page.wait_for_url("**/dashboard**", timeout=60000)
        print("  ✅ Dashboard reached!")
    except Exception as e:
        print(f"  Final Attempt Failed: {e}")
#  MAIN


def main():
    # Step -1 & 0: Create dynamic email and get token
    token = create_mailtm_account()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=600)
        context = browser.new_context()
        page    = context.new_page()

        try:
            # --- Registration Flow ---
            step1_create_account(page)
            otp = step2_get_otp(token)
            step3_submit_otp(page, otp)

            print("Waiting 10 seconds for the server to sync...")
            time.sleep(10) # Hard wait for slow networks

# Force a fresh start by clearing cookies for this domain if needed
# context.clear_cookies() 

            step_4_login_back(page, MAILTM_EMAIL)

            print("\n" + "=" * 55)
            print("  ✅ ALL AUTOMATION COMPLETE!")
            print("=" * 55)
        except Exception as error:
            print(f"\n❌ ERROR: {error}")
            page.screenshot(path="error_screenshot.png")
        finally:
            input("\nPress ENTER to close the browser...")
            context.close()
        browser.close()

if __name__ == "__main__":
    main()