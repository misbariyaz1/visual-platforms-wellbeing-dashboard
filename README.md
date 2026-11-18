# Visual Platforms & Wellbeing Dashboard

An interactive Plotly Dash dashboard exploring the relationship between Instagram behaviour and mental health indicators. Built for the BEMM461 coursework at the University of Exeter.

## What it shows
- **Engagement vs self-presentation:** each dot is one Instagram user (1,000 users, 500 female and 500 male), coloured by gender and sized by followers
- **Mental health indicators by gender:** population-level survey data on anxiety and depressive symptoms
- **Mental health across age groups:** the 18 to 29 group stands out as the core Instagram demographic
- **Filters** for gender and follower segment, with live KPI cards for average engagement, self-presentation and followers

## Key findings
- Engagement rate and self-presentation ratio show no linear relationship (r ≈ 0.00) across the 1,000 users
- In the survey data, anxiety symptoms are higher among women (32.5%) than men (24.9%), and highest among 18 to 29-year-olds (41.5%)
- The two datasets are separate, so the dashboard shows context side by side and does not claim that Instagram use causes anxiety

## Run it
```bash
pip install -r requirements.txt
python dashboard.py
```
Then open http://127.0.0.1:8050 in your browser.

## Files
- `dashboard.py`: the Dash app
- `instagram_clean.csv`: cleaned Instagram user data
- `anxiety_gender_dashboard.csv`, `anxiety_age_dashboard.csv`: survey indicators by gender and age group

## Author
Misba Riyaz | MSc Business Analytics, University of Exeter | [LinkedIn](https://www.linkedin.com/in/misbariyaz)
