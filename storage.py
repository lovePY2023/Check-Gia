import json
import os
from supabase import create_client, Client

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data_store.json")

import streamlit as st

def get_supabase():
    try:
        # Load from st.secrets or os.environ
        url = st.secrets["SUPABASE_URL"] if "SUPABASE_URL" in st.secrets else os.environ.get("SUPABASE_URL")
        key = st.secrets["SUPABASE_KEY"] if "SUPABASE_KEY" in st.secrets else os.environ.get("SUPABASE_KEY")
        if url and key:
            return create_client(url, key)
    except Exception as e:
        print(f"Lỗi khởi tạo Supabase: {e}")
    return None

def get_previous_data():
    supabase = get_supabase()
    if supabase:
        try:
            response = supabase.table("products").select("*").execute()
            return response.data
        except Exception as e:
            print(f"Supabase error: {e}")
    
    # Fallback to local
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_new_data(data):
    supabase = get_supabase()
    if supabase:
        try:
            # Delete old and insert new (simple sync)
            # Or use upsert if data has unique IDs. 
            # Here we use 'link' as a unique constraint in Supabase if possible.
            # Simplified: just upsert using link
            for item in data:
                supabase.table("products").upsert(item).execute()
            return
        except Exception as e:
            print(f"Supabase save error: {e}")

    # Fallback to local
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

VATTU_FILE = os.path.join(BASE_DIR, "data_vattu.json")

def get_vattu_data():
    supabase = get_supabase()
    if supabase:
        try:
            response = supabase.table("vattu").select("*").execute()
            return response.data
        except Exception as e:
            print(f"Supabase error: {e}")
    
    if os.path.exists(VATTU_FILE):
        with open(VATTU_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_vattu_data(data):
    supabase = get_supabase()
    if supabase:
        try:
            # Simple sync
            for item in data:
                # Use name as unique if possible, or category+name
                supabase.table("vattu").upsert(item).execute()
            return
        except Exception as e:
            print(f"Supabase save error: {e}")

    with open(VATTU_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def compare_data(new_data):
    old_data_list = get_previous_data()
    old_data = {item['link']: item for item in old_data_list}
    
    report = {
        "price_changes": [],
        "new_items": [],
        "removed_items": []
    }
    
    for item in new_data:
        link = item['link']
        if link in old_data:
            # Clean price for comparison
            # Handle cases where price might be string or int
            def clean(p):
                if isinstance(p, int): return p
                import re
                return int(re.sub(r'\D', '', str(p))) if p else 0

            old_p = clean(old_data[link]['price'])
            new_p = clean(item['price'])
            
            if new_p != old_p and new_p > 0:
                report["price_changes"].append({
                    "name": item['name'],
                    "old_price": old_data[link]['price'],
                    "new_price": item['price'],
                    "diff": new_p - old_p
                })
        else:
            report["new_items"].append(item)
            
    # Save the latest data
    save_new_data(new_data)
    return report
