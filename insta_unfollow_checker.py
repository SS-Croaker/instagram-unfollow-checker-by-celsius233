import streamlit as st
import pandas as pd
import json
import zipfile
import tempfile
import os
from datetime import datetime, date
import streamlit.components.v1 as components

# Page setup
st.set_page_config(page_title="Insta Unfollow Checker by Celsius 233", layout="centered")
st.title("Insta Unfollow Checker by Celsius 233")
st.markdown("""
Upload the ZIP file you downloaded from Instagram or the individual follower and following `.json` files **or**  to see who you follow that doesn’t follow you back.
""")
st.markdown(
    '<small>Need help? <a href="https://help.instagram.com/181231772500920" target="_blank">Learn how to download your followers & following list</a> → '
    '<em>"Accounts Center → Your information and permissions → Download your information → Select the profile → Some of your information → Connections → Followers and Following → Download to device → Date Range (All time) → Create files"</em>.</small>',
    unsafe_allow_html=True
)

# Upload blocks
# with st.container():
#     st.markdown("### 📤 Upload `following.json`")
#     following_file = st.file_uploader(
#         label="Drag and drop file here or click to browse",
#         type="json",
#         key="following_json",
#         label_visibility="collapsed"
#     )

# with st.container():
#     st.markdown("### 📤 Upload `followers_1.json`")
#     followers_file = st.file_uploader(
#         label="Drag and drop file here or click to browse",
#         type="json",
#         key="followers_json",
#         label_visibility="collapsed"
# #     )
# st.caption("🔒 Your uploaded files are processed securely in your browser session and are not stored on any server.")

# Processing
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
    
def extract_from_zip(uploaded_zip):
    followers_json, following_json = None, None
    with tempfile.TemporaryDirectory() as tmpdirname:
        zip_path = os.path.join(tmpdirname, "insta.zip")
        with open(zip_path, "wb") as f:
            f.write(uploaded_zip.getvalue())
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(tmpdirname)
        for root, dirs, files in os.walk(tmpdirname):
            for file in files:
                if file == "followers_1.json":
                    with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                        followers_json = json.load(f)
                if file == "following.json":
                    with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                        following_json = json.load(f)
    return followers_json, following_json


# --- Upload Inputs ---
st.markdown("### 📦 Option 1: Upload ZIP file from Instagram")
zip_file = st.file_uploader("Upload Instagram data ZIP", type="zip", key="zip_upload")

st.caption("🔒 Your uploaded files are processed securely in your browser session and are not stored on any server.")

st.markdown("---")

st.markdown("### 📤 Option 2: Upload individual JSON files")

# Custom CSS to increase uploader box height
st.markdown("""
    <style>
    .big-uploader .stFileUploader {
        padding: 20px 10px;
        background-color: #f9f9f9;
        border: 2px dashed #FF6F31;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# Section Header
st.markdown("### 📤 Option 2: Upload individual JSON files")

# Columns for following and followers_1
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="big-uploader">', unsafe_allow_html=True)
    following_file = st.file_uploader("Upload `following.json`", type="json", key="following_json")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="big-uploader">', unsafe_allow_html=True)
    followers_file = st.file_uploader("Upload `followers_1.json`", type="json", key="followers_json")
    st.markdown('</div>', unsafe_allow_html=True)

st.caption("🔒 Your uploaded files are processed securely in your browser session and are not stored on any server.")

# --- Load Files ---
followers_json, following_json = None, None

if zip_file:
    followers_json, following_json = extract_from_zip(zip_file)
elif followers_file and following_file:
    followers_json = json.load(followers_file)
    following_json = json.load(following_file)

# # Action button and logic
# if following_file and followers_file:
#     if st.button("🔍 Reveal Unfollowers"):
#         following_json = json.load(following_file)
#         followers_json = json.load(followers_file)

#         following_data = following_json.get("relationships_following", []) if isinstance(following_json, dict) else following_json
#         followers_data = followers_json.get("followers_1", []) if isinstance(followers_json, dict) else followers_json

#         following_entries = extract_entries(following_data)
#         follower_usernames = {entry["string_list_data"][0]["value"] for entry in followers_data if "string_list_data" in entry}

#         not_following_back = [entry for entry in following_entries if entry["Username"] not in follower_usernames]
#         not_following_back.sort(key=lambda x: x["Timestamp"])

#         if not_following_back:
#             st.success(f"Found {len(not_following_back)} users who don’t follow you back.")

#             # Add columns
#             for idx, entry in enumerate(not_following_back, 1):
#                 entry["S. No."] = idx
#                 entry["Followed On"] = format_timestamp(entry["Timestamp"])

#             df = pd.DataFrame(not_following_back)[["S. No.", "Username", "Instagram Link", "Threads Link", "Followed On"]]

#             # CSV download
#             today = date.today().isoformat()
#             csv = df.to_csv(index=False).encode('utf-8')
#             st.download_button(
#                 "📥 Download CSV",
#                 csv,
#                 f"unfollow_checker_results_by_celsius_233_{today}.csv",
#                 "text/csv"
#             )

#             # Display
#             st.markdown("### 👇 Here's your list:")
#             for _, row in df.iterrows():
#                 st.markdown(
#                     f"""**{row['S. No.']}. {row['Username']}** - [Instagram]({row['Instagram Link']}) | [Threads]({row['Threads Link']}) — Followed on: `{row['Followed On']}`""",
#                     unsafe_allow_html=True
#                 )
#         else:
#             st.info("✅ Everyone you follow follows you back.")

# --- Processing ---
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
    st.info("⬆️ Please upload the required files above to begin.")


# Footer
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
