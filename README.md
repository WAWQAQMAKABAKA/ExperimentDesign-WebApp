## Project 3 - Experiment Web App "Test Your Trivia Knowledge!" <br>

-- The Effect of Explanation and Nonprobative Photos on Perceived Truthfulness

This study investigates the impact of nonprobative photos and the requirement for explanations on judgment accuracy and response times in evaluating trivia statements. Previous research has shown that nonprobative photos can enhance the perceived truthfulness of claims. We explore whether demanding explanations for judgments counteracts this photo effect. Participants were randomly assigned into two groups: one providing explanations for their judgments (Explain group) and another expressing emotional responses (Emotion group). We hypothesized that the Explain group would show a reduced influence of nonprobative photos on judgment accuracy and response time. Our findings, however, revealed no significant interaction between photo presence and explanation requirement on judgment accuracy. Interestingly, nonprobative photos significantly affected response times, suggesting their influence on cognitive processing speed.

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

### Live Demo
Deployed on Streamlit Cloud: [[Streamlit Cloud link here](https://project35243-6yvhmwmldeqrn63pytqunj.streamlit.app/)]

---

For questions or feedback, feel free to open an issue or contact the repository owner.

