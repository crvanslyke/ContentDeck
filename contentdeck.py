import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect('content_deck.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tasks
                 (id INTEGER PRIMARY KEY, 
                  title TEXT, 
                  type TEXT, 
                  priority TEXT, 
                  notes TEXT, 
                  status TEXT, 
                  created_at TEXT)''')
    conn.commit()
    conn.close()

def run_query(query, params=()):
    conn = sqlite3.connect('content_deck.db')
    c = conn.cursor()
    c.execute(query, params)
    if query.strip().upper().startswith("SELECT"):
        data = c.fetchall()
        columns = [description[0] for description in c.description]
        conn.close()
        return pd.DataFrame(data, columns=columns)
    else:
        conn.commit()
        conn.close()

# --- APP CONFIG ---
st.set_page_config(page_title="The Content Deck", layout="wide")
init_db()

# --- SIDEBAR: ADD TASK ---
st.sidebar.title("Add New Task")

title = st.sidebar.text_input("Title")
task_type = st.sidebar.selectbox("Type", ["Podcast", "Newsletter", "Academic", "Other"])
priority = st.sidebar.selectbox("Priority", ["High", "Medium", "Low"])
notes = st.sidebar.text_area("Notes")

col1, col2 = st.sidebar.columns(2)
add_to_ideas = col1.button("Add to Ideas", use_container_width=True)
add_to_hopper = col2.button("Add to Hopper", use_container_width=True)

if (add_to_ideas or add_to_hopper) and title:
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    initial_status = "Ideas" if add_to_ideas else "The Hopper"
    
    run_query("INSERT INTO tasks (title, type, priority, notes, status, created_at) VALUES (?, ?, ?, ?, ?, ?)",
              (title, task_type, priority, notes, initial_status, created_at))
    st.sidebar.success(f"Added to {initial_status}!")
    st.rerun()

# --- MAIN KANBAN BOARD ---
st.title("The Content Deck")
st.markdown("---")

statuses = ["Ideas", "The Hopper", "In the Lab", "In Production", "Shipped"]
cols = st.columns(len(statuses))
df = run_query("SELECT * FROM tasks")

for i, status in enumerate(statuses):
    with cols[i]:
        st.subheader(status)
        status_tasks = df[df['status'] == status]
        
        for index, row in status_tasks.iterrows():
            with st.container(border=True):
                st.markdown(f"**{row['title']}**")
                st.caption(f"{row['type']} • {row['priority']}")
                if row['notes']:
                    st.text(row['notes'])
                
                # Edit Section
                with st.expander("Edit Details"):
                    with st.form(f"edit_{row['id']}"):
                        new_title = st.text_input("Title", value=row['title'])
                        
                        # Handle selectbox defaults safely
                        type_opts = ["Podcast", "Newsletter", "Academic", "Other"]
                        try:
                            type_idx = type_opts.index(row['type'])
                        except:
                            type_idx = 0
                            
                        priority_opts = ["High", "Medium", "Low"]
                        try:
                            priority_idx = priority_opts.index(row['priority'])
                        except:
                            priority_idx = 1
                            
                        new_type = st.selectbox("Type", type_opts, index=type_idx)
                        new_priority = st.selectbox("Priority", priority_opts, index=priority_idx)
                        new_notes = st.text_area("Notes", value=row['notes'])
                        
                        if st.form_submit_button("Save Changes"):
                            run_query("UPDATE tasks SET title=?, type=?, priority=?, notes=? WHERE id=?", 
                                     (new_title, new_type, new_priority, new_notes, row['id']))
                            st.rerun()

                # Navigation Buttons
                c1, c2, c3 = st.columns([1, 1, 1])
                with c1:
                    if i > 0:
                        if st.button("⬅️", key=f"prev_{row['id']}"):
                            run_query("UPDATE tasks SET status = ? WHERE id = ?", (statuses[i-1], row['id']))
                            st.rerun()
                with c3:
                    if i < len(statuses) - 1:
                        if st.button("➡️", key=f"next_{row['id']}"):
                            run_query("UPDATE tasks SET status = ? WHERE id = ?", (statuses[i+1], row['id']))
                            st.rerun()
                with c2:
                    if st.button("🗑️", key=f"del_{row['id']}"):
                        run_query("DELETE FROM tasks WHERE id = ?", (row['id'],))
                        st.rerun()
