
import streamlit as st
import time
import pandas as pd
import random
import uuid
import json
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def save_to_google_sheets(df, sheet_name="Responses"):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_dict = st.secrets["GSPREAD_KEY"]  # No json.loads() here
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    sheet = client.open("Trivia_Responses").worksheet(sheet_name)
    for _, row in df.iterrows():
        sheet.append_row(row.astype(str).tolist())

# st.markdown("### Debug Secrets Format")
# st.write("Type of GSPREAD_KEY:", type(st.secrets["GSPREAD_KEY"]))
# st.write("GSPREAD_KEY content:", st.secrets["GSPREAD_KEY"])


with open("stimuli.json", "r") as f:
    full_stimuli = json.load(f)

true_pool = [s for s in full_stimuli if s["truth"]]
false_pool = [s for s in full_stimuli if not s["truth"]]

def create_balanced_stimuli(n_true=8, n_false=8, n_photo_each=4):
    sampled_true = random.sample(true_pool, n_true)
    sampled_false = random.sample(false_pool, n_false)

    # Combine and shuffle first
    combined = sampled_true + sampled_false
    random.shuffle(combined)

    # Select items with valid photos
    with_photo_candidates = [s for s in combined if s.get("photo", "").endswith(".png")]

    # Randomly pick 8 total to show photo (4 from true pool, 4 from false)
    photo_ids = set()
    true_count = 0
    false_count = 0
    random.shuffle(with_photo_candidates)
    for s in with_photo_candidates:
        if s["truth"] and true_count < n_photo_each:
            photo_ids.add(s["id"])
            true_count += 1
        elif not s["truth"] and false_count < n_photo_each:
            photo_ids.add(s["id"])
            false_count += 1
        if true_count == n_photo_each and false_count == n_photo_each:
            break

    # Assign show_photo flag
    for s in combined:
        s["show_photo"] = s["id"] in photo_ids

    return combined

if "participant_id" not in st.session_state:
    st.session_state.participant_id = str(uuid.uuid4())

if "group" not in st.session_state:
    st.session_state.group = random.choice(["Explain", "Emotion"])

if "stimuli_subset" not in st.session_state:
    st.session_state.stimuli_subset = create_balanced_stimuli()

if "responses" not in st.session_state:
    st.session_state.responses = []

if "current_index" not in st.session_state:
    st.session_state.current_index = 0

st.title("Trivia!")
if st.session_state.current_index == 0 and not st.session_state.get("instructions_shown", False):
    st.markdown("### Instructions")
    st.markdown("""
    Welcome! This is a trivia quiz. You will be presented with a series of factual statements — some of them are true, some are false.

    Your task is to decide whether each statement is **True** or **False**. 

    Additionally:
    """)
    if st.session_state.group == "Explain":
        st.markdown("- Provide a **brief explanation** of why you think the statement is true or false.")
    else:
        st.markdown("- Share **how the statement makes you feel** — your emotional response.")
    st.markdown("Please answer as accurately and thoughtfully as you can. The quiz will begin once you click the button below.")
    if st.button("Start Quiz"):
        st.session_state.instructions_shown = True
        st.rerun()
    st.stop()

stimuli = st.session_state.stimuli_subset
current_idx = st.session_state.current_index

if current_idx < len(stimuli):
    stim = stimuli[current_idx]
    st.subheader(f"Statement {current_idx + 1} of {len(stimuli)}")
    st.write(stim["text"])

    image_path = os.path.join("images", stim["photo"]) if stim["photo"] else None
    
    # # 🔍 Debugging output
    # st.markdown("**🛠️ DEBUG INFO**")
    # st.write("Current ID:", stim["id"])
    # st.write("Photo file:", stim["photo"])
    # st.write("Should show photo?", stim["show_photo"])
    # st.write("Image path exists?", os.path.exists(image_path) if image_path else "None")
    
    if stim["show_photo"] and image_path and os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            st.image(img_file.read(), width=300)

    if "start_time" not in st.session_state:
        st.session_state.start_time = time.time()

    answer = st.radio("Is this statement true or false?", ["-- Select an answer --", "True", "False"], key=f"radio_{current_idx}")
    response_text = st.text_area(
        "Explain your answer:" if st.session_state.group == "Explain" else "How does this statement make you feel:",
        key=f"text_{current_idx}"
    )

    if st.button("Submit and Continue"):
        if answer == "-- Select an answer --" or response_text.strip() == "":
            st.warning("Please complete both parts before continuing.")
        else:
            rt = round(time.time() - st.session_state.start_time, 2)
            st.session_state.responses.append({
                "participant_id": st.session_state.participant_id,
                "group": st.session_state.group,
                "stimulus_id": stim["id"],
                "text": stim["text"],
                "truth": stim["truth"],
                "photo": stim["photo"],
                "show_photo": stim["show_photo"],
                "answer": answer,
                "response_text": response_text,
                "response_time": rt
            })
            st.session_state.current_index += 1
            st.rerun()
else:
    st.balloons()
    st.success("Thank you for participating! Your responses have been saved.")
    df = pd.DataFrame(st.session_state.responses)
    master_file = "all_responses.csv"
    if os.path.exists(master_file):
        existing = pd.read_csv(master_file)
        df = pd.concat([existing, df], ignore_index=True)
    df.to_csv(master_file, index=False)
    save_to_google_sheets(df)
    st.markdown("### Debriefing")
    st.markdown("""
    Thank you for completing this short trivia survey!

    This study is part of a research project investigating how visual cues (like unrelated photos) and different kinds of reasoning (explanation vs. emotion) affect people’s perception of truth.

    Some of the statements you saw were factually accurate, while others were not. And some were accompanied by images that were not directly related to the content.

    By analyzing how people respond under different conditions, we hope to better understand how misinformation spreads online — especially when it's paired with persuasive visuals.

    Your responses have been recorded anonymously and will help support research in cognitive psychology and digital media literacy.

    If you have any questions, feel free to reach out to the research team at **aw3088@columbia.edu**. Thank you again!
    """)
