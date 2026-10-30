# Kim Joshua C. Paltingca - Developer Portfolio (Streamlit)

Dark navy/cyan portfolio with 8 pages: Home, About Me, Education, Skills, Projects, Experience, Career Goals, Contact.

## Edit your information
Everything personal is in `data/portfolio_data.py`. Replace every "Add ..." placeholder (school names,
graduation year, job dates, GitHub links, social links). Skill levels start unset: tick "Edit proficiency levels"
on the Skills page, or fill `SKILL_LEVELS` in the data file with honest values.

## Add your pictures
Copy images into `assets/` using these exact names: `profile.jpg`, `arallink.png`, `mediwise.png`,
`wildmeow.png`, `movie_booking.png`. Optional: `resume.pdf` adds a PDF download button.
Missing images show a placeholder.

## Run in VS Code (Windows)
1. File > Open Folder > select this folder.
2. Terminal > New Terminal, then:
```
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m streamlit run app.py
```
(Using the venv's python directly avoids the PowerShell activation error.)
3. Open http://localhost:8501 if it does not open automatically.

## Deploy to Streamlit Community Cloud
1. Push this folder to a GitHub repository (include `.streamlit/config.toml`).
2. Go to https://share.streamlit.io, sign in with GitHub, click Create app.
3. Choose the repo and branch, set main file to `app.py`, then Deploy.
4. Submit the app URL for the bonus points.

The contact form is a demo: it validates input and shows a success message, but sends no email.
