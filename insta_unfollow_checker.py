import streamlit as st
import pandas as pd
import json
import zipfile
import tempfile
import os
from datetime import datetime, date
import mimetypes
from pathlib import Path

# ----------------- SETTINGS -----------------
MAX_FILE_SIZE_MB = 5
EXPECTED_FILES = {"followers_1.json", "following.json"}

# ------------- PAGE SETUP -------------------
st.set_page_config(page_title="Insta Unfollow Checker by Celsius 233", layout="centered")
st.title("Insta Unfollow Checker by Celsius 233")
st.markdown("""
Upload the ZIP file you downloaded from Instagram to see who you follow that doesn’t follow you back.
""")
st.markdown(
    '<small>Need help? <a href="https://help.instagram.com/181231772500920" target="_blank">Learn how to download your followers & following list</a> → '
    '<em>"Accounts Center → Your information and permissions → Download your information → Select the profile → Some of your information → Connections → Followers and Following → Download to device → Date Range (All time) → "JSON" → Create files"</em>.</small>',
    unsafe_allow_html=True
)


# ----------- HELPERS -------------------------
def is_safe_path(base_path, target_path):
    return os.path.commonpath([base_path]) == os.path.commonpath([base_path, target_path])

def sanitize_filename(name):
    return os.path.basename(name)

def extract_entries(data):
    entries = []
    for entry in data:
        try:
            s = entry["string_list_data"][0]
            username = s["value"]
            ig_link = s["href"]
            timestamp = s["timestamp"]
            threads_link = f"https://www.threads.net/@{username}"
            entries.append({
                "Username": username,
                "Instagram Link": ig_link,
                "Threads Link": threads_link,
                "Timestamp": timestamp
            })
        except:
            continue
    return entries

def format_timestamp(ts):
    try:
        return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M')
    except:
        return ts

def is_valid_json_structure(data):
    return isinstance(data, list) and all("string_list_data" in d for d in data)

# ---------- ZIP EXTRACTION ------------------
def extract_from_zip(uploaded_zip):
    followers_json, following_json = None, None

    with tempfile.TemporaryDirectory() as tmpdirname:
        zip_path = os.path.join(tmpdirname, "insta.zip")

        # Write ZIP to temp file
        with open(zip_path, "wb") as f:
            f.write(uploaded_zip.getvalue())

        # MIME type check
        mime_type, _ = mimetypes.guess_type(zip_path)
        if mime_type != "application/zip":
            st.error("Invalid file type. Please upload a valid .zip file.")
            st.stop()

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Safety check for ZIP paths
            for member in zip_ref.namelist():
                member_path = os.path.join(tmpdirname, sanitize_filename(member))
                if not is_safe_path(tmpdirname, member_path):
                    st.error("Unsafe file path in ZIP. Aborting.")
                    st.stop()

            zip_ref.extractall(tmpdirname)

        # Walk and find target files
        for root, _, files in os.walk(tmpdirname):
            for file in files:
                if file in EXPECTED_FILES:
                    full_path = os.path.join(root, file)
                    try:
                        with open(full_path, "r", encoding="utf-8") as f:
                            content = json.load(f)
                            if file == "followers_1.json":
                                followers_json = content
                            elif file == "following.json":
                                following_json = content
                    except Exception:
                        st.error(f"Error reading `{file}`. Please make sure the file is correct.")
                        st.stop()
    return followers_json, following_json

# ------------- FILE UPLOAD ------------------
st.markdown("### 📤 Upload ZIP file from Instagram")
zip_file = st.file_uploader("Upload Instagram data ZIP", type="zip", key="zip_upload")

st.caption("🔒 Your uploaded files are processed securely in your browser session and are not stored on any server.")

# ------------- VALIDATION ------------------
if zip_file and zip_file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
    st.error(f"❌ File too large. Max allowed is {MAX_FILE_SIZE_MB}MB.")
    st.stop()

followers_json, following_json = None, None
if zip_file:
    followers_json, following_json = extract_from_zip(zip_file)

# ------------- PROCESSING ------------------
if followers_json and following_json:
    if st.button("🔍 Reveal Unfollowers"):
        following_data = following_json.get("relationships_following", []) if isinstance(following_json, dict) else following_json
        followers_data = followers_json.get("followers_1", []) if isinstance(followers_json, dict) else followers_json

        following_entries = extract_entries(following_data)
        follower_usernames = {entry["string_list_data"][0]["value"] for entry in followers_data if "string_list_data" in entry}

        not_following_back = [entry for entry in following_entries if entry["Username"] not in follower_usernames]
        not_following_back.sort(key=lambda x: x["Timestamp"])

        if not_following_back:
            st.success(f"Found {len(not_following_back)} users who don’t follow you back.")

            for idx, entry in enumerate(not_following_back, 1):
                entry["S. No."] = idx
                entry["Followed On"] = format_timestamp(entry["Timestamp"])

            df = pd.DataFrame(not_following_back)[["S. No.", "Username", "Instagram Link", "Threads Link", "Followed On"]]

            today = date.today().isoformat()
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Download CSV",
                csv,
                f"unfollow_checker_results_by_celsius_233_{today}.csv",
                "text/csv"
            )

            st.markdown("### 👇 Here's your list:")
            for _, row in df.iterrows():
                st.markdown(
                    f"""**{row['S. No.']}. {row['Username']}** - [Instagram]({row['Instagram Link']}) | [Threads]({row['Threads Link']}) — Followed on: `{row['Followed On']}`""",
                    unsafe_allow_html=True
                )
        else:
            st.info("✅ Everyone you follow follows you back.")
else:
    st.info("⬆️ Please upload the required ZIP file to begin.")

# ------------- FOOTER ------------------
st.markdown("---")
st.markdown("### 🔗 Support & Follow Celsius 233")
st.markdown("""
- [Buy Me a Coffee](https://buymeacoffee.com/celsius233books)
- [PayPal](https://paypal.me/celsius233books)
- [Instagram](https://www.instagram.com/celsius233books)
- [YouTube](https://www.youtube.com/@Celsius233Books)
- [Threads](https://www.threads.net/@celsius233books)
- [Full Social List → Celsius 233 Universe](https://celsius233.com/universe)
""")
