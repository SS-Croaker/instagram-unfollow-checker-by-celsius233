import streamlit as st
import pandas as pd
import json
from datetime import datetime

st.set_page_config(page_title="Insta Unfollow Checker by Celsius 233", layout="centered")

st.title("📉 Insta Unfollow Checker by Celsius 233")
st.markdown("Upload your Instagram follower and following `.json` files to see who you follow that doesn't follow you back.")

# Upload widgets with larger size
with st.container():
    st.markdown("### 📤 Upload `following.json`")
    following_file = st.file_uploader(
        label="Drag and drop file here or click to browse",
        type="json",
        key="following_json",
        label_visibility="collapsed"
    )

with st.container():
    st.markdown("### 📤 Upload `followers_1.json`")
    followers_file = st.file_uploader(
        label="Drag and drop file here or click to browse",
        type="json",
        key="followers_json",
        label_visibility="collapsed"
    )

# Processing function
def extract_entries(data):
    entries = []
    for entry in data:
        try:
            s = entry["string_list_data"][0]
            username = s["value"]
            link = s["href"]
            timestamp = s["timestamp"]
            entries.append({
                "Username": username,
                "Link": link,
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

# Show button after both files are uploaded
if following_file and followers_file:
    if st.button("🔍 Reveal Unfollowers"):
        # Load data
        following_json = json.load(following_file)
        followers_json = json.load(followers_file)

        following_data = following_json.get("relationships_following", []) if isinstance(following_json, dict) else following_json
        followers_data = followers_json.get("followers_1", []) if isinstance(followers_json, dict) else followers_json

        following_entries = extract_entries(following_data)
        follower_usernames = {entry["string_list_data"][0]["value"] for entry in followers_data if "string_list_data" in entry}

        # Filter and sort
        not_following_back = [entry for entry in following_entries if entry["Username"] not in follower_usernames]
        not_following_back.sort(key=lambda x: x["Timestamp"])

        if not_following_back:
            st.success(f"Found {len(not_following_back)} users who don’t follow you back.")

            # Optional download at the top
            df = pd.DataFrame(not_following_back)
            df["Followed On"] = df["Timestamp"].apply(format_timestamp)
            df = df[["Username", "Link", "Followed On"]]
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download CSV", csv, "unfollow_checker_results.csv", "text/csv")

            # Show list
            st.markdown("### 👇 Here's your list:")
            for idx, user in enumerate(not_following_back, 1):
                readable_time = format_timestamp(user["Timestamp"])
                st.markdown(f"**{idx}.** [{user['Username']}]({user['Link']}) — _Followed on:_ `{readable_time}`")
        else:
            st.info("✅ Everyone you follow follows you back.")
