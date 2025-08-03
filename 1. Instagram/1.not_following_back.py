import json
import os
import tkinter as tk
from tkinter import filedialog
import pandas as pd

CONFIG_FILE = 'last_dir.txt'

def get_last_dir():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return f.read().strip()
    return os.getcwd()

def set_last_dir(path):
    with open(CONFIG_FILE, 'w') as f:
        f.write(path)

def load_json_file(prompt):
    root = tk.Tk()
    root.withdraw()
    initial_dir = get_last_dir()
    file_path = filedialog.askopenfilename(
        title=prompt,
        initialdir=initial_dir,
        filetypes=[("JSON files", "*.json")]
    )
    if not file_path:
        print(f"{prompt} cancelled.")
        exit(1)
    set_last_dir(os.path.dirname(file_path))
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

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
                "Instagram Link": link,
                "Follow Timestamp": timestamp
            })
        except Exception:
            continue
    return entries

def main():
    print("📁 Select 'following.json' file...")
    following_json = load_json_file("Select following.json")

    if isinstance(following_json, dict):
        following_data = following_json.get("relationships_following", [])
    else:
        following_data = following_json

    print("📁 Select 'followers_1.json' file...")
    followers_json = load_json_file("Select followers_1.json")

    if isinstance(followers_json, dict):
        followers_data = followers_json.get("followers_1", [])
    else:
        followers_data = followers_json

    # Extract detailed entries
    following_entries = extract_entries(following_data)
    follower_usernames = {entry["string_list_data"][0]["value"] for entry in followers_data if "string_list_data" in entry}

    # Filter: people you follow but who don't follow you back
    not_following_back = [entry for entry in following_entries if entry["Username"] not in follower_usernames]

    if not not_following_back:
        print("✅ Everyone you follow follows you back.")
        return

    # Sort by timestamp (ascending)
    not_following_back.sort(key=lambda x: x["Follow Timestamp"])

    # Add serial number
    for idx, entry in enumerate(not_following_back, 1):
        entry["S. No."] = idx

    # Reorder columns
    df = pd.DataFrame(not_following_back)[["S. No.", "Username", "Instagram Link", "Follow Timestamp"]]

    output_file = "not_following_back_detailed.csv"
    df.to_csv(output_file, index=False)
    print(f"📄 Saved {len(df)} entries to '{output_file}'.")

if __name__ == "__main__":
    main()
