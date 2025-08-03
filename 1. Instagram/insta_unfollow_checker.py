import streamlit as st
import pandas as pd
import json
from datetime import datetime, date
import streamlit.components.v1 as components

# Page setup
st.set_page_config(page_title="Insta Unfollow Checker by Celsius 233", layout="centered")
st.title("Insta Unfollow Checker by Celsius 233")
st.markdown("Upload your Instagram follower and following `.json` files to see who you follow that doesn't follow you back.")
st.markdown(
    '<small>Need help? <a href="https://help.instagram.com/181231772500920" target="_blank">Learn how to download your followers & following list</a> → '
    '<em>Select "Some of your information → Connections → Followers and Following"</em>.</small>',
    unsafe_allow_html=True
)

# Upload blocks
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

# Action button and logic
if following_file and followers_file:
    if st.button("🔍 Reveal Unfollowers"):
        following_json = json.load(following_file)
        followers_json = json.load(followers_file)

        following_data = following_json.get("relationships_following", []) if isinstance(following_json, dict) else following_json
        followers_data = followers_json.get("followers_1", []) if isinstance(followers_json, dict) else followers_json

        following_entries = extract_entries(following_data)
        follower_usernames = {entry["string_list_data"][0]["value"] for entry in followers_data if "string_list_data" in entry}

        not_following_back = [entry for entry in following_entries if entry["Username"] not in follower_usernames]
        not_following_back.sort(key=lambda x: x["Timestamp"])

        if not_following_back:
            st.success(f"Found {len(not_following_back)} users who don’t follow you back.")

            # Add columns
            for idx, entry in enumerate(not_following_back, 1):
                entry["S. No."] = idx
                entry["Followed On"] = format_timestamp(entry["Timestamp"])

            df = pd.DataFrame(not_following_back)[["S. No.", "Username", "Instagram Link", "Threads Link", "Followed On"]]

            # CSV download
            today = date.today().isoformat()
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Download CSV",
                csv,
                f"unfollow_checker_results_by_celsius_233_{today}.csv",
                "text/csv"
            )

            # Display
            st.markdown("### 👇 Here's your list:")
            for _, row in df.iterrows():
                # st.markdown(
                #     f"""**{row['S. No.']}. {row['Username']}** - [Instagram]({row['Instagram Link']}) | [Threads]({row['Threads Link']}) — Followed on: `{row['Followed On']}`""",
                #     unsafe_allow_html=True
                # )
                st.markdown(
                    f"""<div style="display:flex; align-items:center;">
                        <input type="text" value="{row['Username']}" id="user-{row['S. No.']}" readonly style="margin-right: 10px;"/>
                        <button onclick="navigator.clipboard.writeText('{row['Username']}')">Copy</button>
                        <span style="margin-left: 10px;">
                            <a href="{row['Instagram Link']}" target="_blank">Instagram</a> |
                            <a href="{row['Threads Link']}" target="_blank">Threads</a> —
                            <code>{row['Followed On']}</code>
                        </span>
                    </div>""",
                    unsafe_allow_html=True
                )
        else:
            st.info("✅ Everyone you follow follows you back.")

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
