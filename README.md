## Project 3 - Psychology Experiment Web App

This repository contains the source code for a psychology experiment web app designed to test the influence of nonprobative photos and explanatory reasoning on truth judgments.

### Collaborators
- Ziyue Gao (ziyuegao0302)  
- Keito Taketomi (kt2849)  
- Anqi Wu (Owner of this repo, WAWQAQMAKABAKA)  
- Yixin Xiao (yx2888)  

### Overview
Participants are shown trivia statements, some accompanied by images, and asked to judge whether the statements are true or false. The study investigates how explanation prompts and image presence affect accuracy and response time in truth assessments.

### File Structure

```
Project3_5243/
├── experiment_app.py          # Main Streamlit application
├── stimuli.json               # Contains all trivia statements and metadata
├── image_folder/              # Folder of images referenced in the study
├── result.csv                 # Data output file from completed participant responses
├── Analysisv1.ipynb           # Statistical analysis and visualization notebook
├── requirements.txt           # Python dependencies
└── README.md                  # You are here
```

### Running the App
To run the experiment locally:

#### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 2. Launch the App
```bash
streamlit run experiment_app.py
```

### Study Design
- **Groups:** Participants are randomly assigned to one of two groups:
  - **Explain**: Asked to explain their reasoning for each truth judgment
  - **Emotion**: Asked to describe their emotional response
- **Conditions:**
  - Photo-present vs. photo-absent conditions within each group
- **Measures:**
  - Accuracy of truth judgment
  - Response time (as a proxy for cognitive effort)

### Output
- Results are saved in `result.csv`, including:
  - Participant response
  - Accuracy
  - Response time
  - Group and condition information

### Acknowledgements
This project was conducted for educational purposes as part of a course assignment. No formal IRB approval was obtained, but ethical guidelines were followed with informed consent and a debriefing section included in the app.

### Live Demo (if applicable)
If deployed: [[Streamlit Cloud link goes here](https://project35243-6yvhmwmldeqrn63pytqunj.streamlit.app/)]

---

For questions or feedback, feel free to open an issue or contact the repository owner.

