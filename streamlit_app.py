import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta

# Database functions
def create_table():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            subject TEXT,
            deadline DATETIME,
            state TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_item(title, description, subject, deadline, state):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute('INSERT INTO items (title, description, subject, deadline, state) VALUES (?,?,?,?,?)',
              (title, description, subject, deadline, state))
    conn.commit()
    conn.close()

def get_all_items():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute('SELECT * FROM items')
    data = c.fetchall()
    conn.close()
    return data

def update_item_state(item_id, state):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute('UPDATE items SET state=? WHERE id=?', (state, item_id))
    conn.commit()
    conn.close()

def delete_item(item_id):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute('DELETE FROM items WHERE id=?', (item_id,))
    conn.commit()
    conn.close()

# Create the table
create_table()

# Streamlit app
st.title("Simple Checklist App")

# Collapsible form to add new item
with st.expander("Add New Item"):
    with st.form("Add New Item Form"):
        title = st.text_input("Title")
        description = st.text_area("Description")
        subject = st.text_input("Subject")
        deadline = st.date_input("Deadline Date")
        deadline_time = st.time_input("Deadline Time")
        state = st.selectbox("State", ["Not Done", "Done"])
        submitted = st.form_submit_button("Add Item")
        if submitted:
            # Combine deadline date and time
            deadline_datetime = datetime.combine(deadline, deadline_time)
            add_item(title, description, subject, deadline_datetime.strftime("%Y-%m-%d %H:%M:%S"), state)
            st.success("Item added successfully")
            st.rerun()

# Get all items
items = get_all_items()

if items:
    # Convert to DataFrame
    columns = ['id', 'title', 'description', 'subject', 'deadline', 'state']
    df = pd.DataFrame(items, columns=columns)

    # Filter by subject
    subjects = df['subject'].unique().tolist()
    selected_subject = st.sidebar.selectbox("Filter by Subject", ['All'] + subjects)

    if selected_subject != 'All':
        df = df[df['subject'] == selected_subject]

    # Sort by deadline
    sort_by_deadline = st.sidebar.checkbox("Sort by Deadline")

    # Convert deadline to datetime
    df['deadline'] = pd.to_datetime(df['deadline'])

    if sort_by_deadline:
        df = df.sort_values(by='deadline')

    # Compute countdown
    df['time_remaining'] = df['deadline'] - datetime.now()

    def format_timedelta(td):
        if td.total_seconds() < 0:
            return "Expired"
        else:
            days = td.days
            hours, remainder = divmod(td.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            return f"{days}d {hours}h {minutes}m"

    df['countdown'] = df['time_remaining'].apply(format_timedelta)

    # Display items
    for index, row in df.iterrows():
        st.write(f"**Title**: {row['title']}")
        st.write(f"**Description**: {row['description']}")
        st.write(f"**Subject**: {row['subject']}")
        st.write(f"**Time Remaining**: {row['countdown']}")
        st.write(f"**State**: {row['state']}")

        # Create columns for buttons
        col1, col2 = st.columns(2)

        with col1:
            if row['state'] == 'Not Done':
                if st.button("Mark as Done", key=f"done_{row['id']}"):
                    update_item_state(row['id'], 'Done')
                    st.rerun()
            else:
                st.write("✅ Done")

        with col2:
            if st.button("Delete", key=f"delete_{row['id']}"):
                delete_item(row['id'])
                st.rerun()

        st.write("---")
else:
    st.write("No items to display.")
