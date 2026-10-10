# OrganFlow — Smart Organ Match & Cold-Chain Transit Tracker

An educational DSA prototype using synthetic records to demonstrate organ registration, rule-based recipient eligibility, priority ranking, transit checkpoints, viability countdowns, temperature alerts, interruption handling, emergency prioritisation, and audit history.

## Run locally (Windows / VS Code)

Open the `OrganFlow_Updated` folder in VS Code, then in the terminal:

```powershell
cd frontend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

If PowerShell blocks activation, use Command Prompt and run `venv\Scripts\activate.bat`, or use `python -m pip install -r requirements.txt` and `python -m streamlit run app.py` without activating the environment.

## Folder structure

- `frontend/app.py` — Streamlit UI, preserving the OrganFlow blue/navy + orange visual style.
- `frontend/dsa.py` — hand-written linked list, queue, stack, priority queue and merge sort used by the running demo.
- `data/` — fictional CSV datasets for organs, recipients and hospitals.
- `java-lab/SmartOrganTracker.java` — original Java lab program retained as a separate source file.

## Important architecture note

The currently runnable Streamlit version calls `frontend/dsa.py`. The Java lab source is preserved, but is **not connected to the Streamlit UI** because the Java program is console-based (`Scanner`/menu) and has no HTTP API yet. To make the web UI call the Java implementation, a Java REST API adapter and parameter-based service methods must be added separately.

All data is synthetic and for educational demonstration only. This is not a medical system and must not be used for clinical decisions or real organ allocation.
