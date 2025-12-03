# The Content Deck
A local Kanban board to manage content creation tasks, built with Streamlit and SQLite.
## Features
- **Kanban Board:** Visual drag-and-drop style management (via buttons).
- **Lanes:** Ideas, The Hopper, In the Lab, In Production, Shipped.
- **Task Management:** Add, Edit, Delete, and Prioritize tasks.
## Setup
1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Run the App:**
   ```bash
   streamlit run content_deck.py
   ```
3. **Data:**
   The app will automatically create a local `content_deck.db` file upon first run.