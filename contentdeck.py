"sy-kw">import streamlit "sy-kw">as "sy-cls">st
"sy-kw">import"sy-cls">sqlite3
"sy-kw">import pandas "sy-kw">as "sy-cls">pd
"sy-kw">from"sy-cls">datetime "sy-kw">import "sy-cls">datetime
"sy-com"># --- DATABASE SETUP ---
"sy-kw">def init_db():
    "sy-cls">conn = "sy-cls">sqlite3.connect('content_deck.db')
    "sy-cls">c = "sy-cls">conn.cursor()
    "sy-cls">c.execute('''CREATE TABLE IF NOT EXISTS tasks
                 (id INTEGER PRIMARY KEY, 
                  title TEXT, 
                  type TEXT, 
                  priority TEXT, 
                  notes TEXT, 
                  status TEXT, 
                  created_at TEXT)''')
    "sy-cls">conn.commit()
    "sy-cls">conn.close()
"sy-kw">def run_query(query, params=()):
    "sy-cls">conn = "sy-cls">sqlite3.connect('content_deck.db')
    "sy-cls">c = "sy-cls">conn.cursor()
    "sy-cls">c.execute(query, params)
    "sy-kw">if query.strip().upper().startswith("SELECT"):
        data = "sy-cls">c.fetchall()
        columns = [description[0] "sy-kw">for description "sy-kw">in "sy-cls">c.description]
        "sy-cls">conn.close()
        "sy-kw">return"sy-cls">pd.DataFrame(data, columns=columns)
    "sy-kw">else:
        "sy-cls">conn.commit()
        "sy-cls">conn.close()
"sy-com"># --- APP CONFIG ---
"sy-cls">st.set_page_config(page_title="The Content Deck", layout="wide")
init_db()
"sy-com"># --- SIDEBAR: ADD TASK ---
"sy-cls">st.sidebar.title("Add New Task")
title = "sy-cls">st.sidebar.text_input("Title")
task_type = "sy-cls">st.sidebar.selectbox("Type", ["Podcast", "Newsletter", "Academic", "Other"])
priority = "sy-cls">st.sidebar.selectbox("Priority", ["High", "Medium", "Low"])
notes = "sy-cls">st.sidebar.text_area("Notes")
col1, col2 = "sy-cls">st.sidebar.columns(2)
add_to_ideas = col1.button("Add to Ideas", use_container_width=True)
add_to_hopper = col2.button("Add to Hopper", use_container_width=True)
"sy-kw">if (add_to_ideas or add_to_hopper) and title:
    created_at = "sy-cls">datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    initial_status = "Ideas" "sy-kw">if add_to_ideas "sy-kw">else "The Hopper"
    
    run_query("INSERT INTO tasks (title, type, priority, notes, status, created_at) VALUES (?, ?, ?, ?, ?, ?)",
              (title, task_type, priority, notes, initial_status, created_at))
    "sy-cls">st.sidebar.success(f"Added to {initial_status}!")
    "sy-cls">st.rerun()
"sy-com"># --- MAIN KANBAN BOARD ---
"sy-cls">st.title("The Content Deck")
"sy-cls">st.markdown("---")
statuses = ["Ideas", "The Hopper", "In the Lab", "In Production", "Shipped"]
cols = "sy-cls">st.columns("sy-func">len(statuses))
df = run_query("SELECT * FROM tasks")
"sy-kw">for i, status "sy-kw">in "sy-func">enumerate(statuses):
    "sy-kw">with cols[i]:
        "sy-cls">st.subheader(status)
        status_tasks = df[df['status'] == status]
        
        "sy-kw">for index, row "sy-kw">in status_tasks.iterrows():
            "sy-kw">with"sy-cls">st.container(border=True):
                "sy-cls">st.markdown(f"**{row['title']}**")
                "sy-cls">st.caption(f"{row['type']} • {row['priority']}")
                "sy-kw">if row['notes']:
                    "sy-cls">st.text(row['notes'])
                
                "sy-com"># --- EDIT EXPANDER ---
                "sy-kw">with"sy-cls">st.expander("Edit Details"):
                    "sy-kw">with"sy-cls">st.form(f"edit_{row['id']}"):
                        new_title = "sy-cls">st.text_input("Title", value=row['title'])
                        new_type = "sy-cls">st.selectbox("Type", ["Podcast", "Newsletter", "Academic", "Other"], index=["Podcast", "Newsletter", "Academic", "Other"].index(row['type']))
                        new_priority = "sy-cls">st.selectbox("Priority", ["High", "Medium", "Low"], index=["High", "Medium", "Low"].index(row['priority']))
                        new_notes = "sy-cls">st.text_area("Notes", value=row['notes'])
                        "sy-kw">if"sy-cls">st.form_submit_button("Save Changes"):
                            run_query("UPDATE tasks SET title=?, type=?, priority=?, notes=? WHERE id=?", 
                                     (new_title, new_type, new_priority, new_notes, row['id']))
                            "sy-cls">st.rerun()
                "sy-com"># --- CONTROLS ---
                c1, c2, c3 = "sy-cls">st.columns([1, 1, 1])
                "sy-kw">with c1:
                    "sy-kw">if i > 0:
                        "sy-kw">if"sy-cls">st.button("⬅️", key=f"prev_{row['id']}"):
                            run_query("UPDATE tasks SET status = ? WHERE id = ?", (statuses[i-1], row['id']))
                            "sy-cls">st.rerun()
                "sy-kw">with c3:
                    "sy-kw">if i < "sy-func">len(statuses) - 1:
                        "sy-kw">if"sy-cls">st.button("➡️", key=f"next_{row['id']}"):
                            run_query("UPDATE tasks SET status = ? WHERE id = ?", (statuses[i+1], row['id']))
                            "sy-cls">st.rerun()
                "sy-kw">with c2:
                    "sy-kw">if"sy-cls">st.button("🗑️", key=f"del_{row['id']}"):
                        run_query("DELETE FROM tasks WHERE id = ?", (row['id'],))
                        "sy-cls">st.rerun()