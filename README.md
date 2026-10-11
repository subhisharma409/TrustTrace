
# TrustTrace

**Explainable Hidden Connection Investigator**

TrustTrace is a graph-based investigation demo that explores connections between fictional reports through shared phone identifiers, website domains, and email identifiers.

## Features

- Multi-hop report connection investigation using Neo4j Aura
- Interactive Streamlit web interface
- Graph path visualization
- Evidence tables and CSV exports
- Shared-identifier analytics and connector-report candidates
- Gemini-powered explanations grounded in retrieved graph evidence

## Tech Stack

- Python
- Neo4j Aura
- Streamlit
- Plotly
- Google Gemini API

## Setup

### 1. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 3. Configure environment variables

Set the following variables in your terminal. Replace the placeholders with your own credentials.

PowerShell:

```powershell
$env:NEO4J_URI="neo4j+s://YOUR-INSTANCE.databases.neo4j.io"
$env:NEO4J_USERNAME="neo4j"
$env:NEO4J_PASSWORD="YOUR_DATABASE_PASSWORD"
$env:GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
```

Never commit actual credentials to GitHub.

### 4. Generate the synthetic dataset

```bash
python generate_dataset.py
python validate_dataset.py
```

### 5. Import data into Neo4j Aura

```bash
python import_to_neo4j.py
```

Ensure your Aura database is running before importing.

### 6. Launch TrustTrace

```bash
python -m streamlit run app.py
```

## Responsible Use

The included dataset is synthetic. Shared identifiers and graph connections are investigative leads, not proof of common ownership or wrongdoing. The evidence-prioritization index is a heuristic, not a calibrated fraud probability.

## Limitations

This is a prototype and has not been validated for real-world fraud detection. AI explanations can contain errors and should be checked against the underlying evidence.
