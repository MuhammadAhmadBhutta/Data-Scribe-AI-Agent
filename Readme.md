# 🖋️ Data Scribe AI Agent

**Data Scribe AI Agent** is a high-reliability, local web scraping and data extraction tool. It is designed to extract structured data (tables, lists, headers) from any URL without requiring external APIs, using a combination of Selenium's browser automation and BeautifulSoup's parsing capabilities.

## 🚀 Key Features
- **Local-First Architecture:** No API keys required. All data processing and storage happens on your machine.
- **Glassmorphism UI:** A premium, modern dashboard built with HTML5, CSS3, and Bootstrap 5.
- **Automated Data Extraction:**
    - **Tables:** Automatically identifies and converts HTML tables into structured datasets using Polars and Pandas.
    - **Lists & Headlines:** Captures unordered/ordered lists and hierarchy headers (H1-H3).
- **Multi-Format Export:** Saves extracted data directly into the `data/` folder as:
    - **JSON:** Complete session data.
    - **CSV:** Individual tables for easy analysis.
    - **Markdown:** Clean, readable summaries of the page content.
- **Custom Project Naming:** Allows you to name your extractions for better organization.
- **Real-Time Agent Console:** A live log relay that shows the agent's "thinking" process as it navigates and parses targets.
- **Visual Analytics:** Interactive charts using Plotly to show data distribution at a glance.

## 🛠️ Technology Stack
- **Backend:** [FastAPI](https://fastapi.tiangolo.com/) (Python)
- **Scraping Engine:** [Selenium](https://www.selenium.dev/) & [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/)
- **Data Handling:** [Pandas](https://pandas.pydata.org/) & [Polars](https://pola.rs/)
- **Frontend UI:** HTML5, CSS3 (Vanilla + Glassmorphism), Bootstrap 5
- **Data Visualization:** [Plotly.js](https://plotly.com/javascript/)

## 📦 Installation & Setup
1.  **Clone the project** to your local machine:
    ```bash
    git clone https://github.com/MuhammadAhmadBhutta/Data-Scribe-AI-Agent
    ```
2.  **Navigate to the project directory**:
    ```bash
    cd "Data Scribe AI Agent"
    ```
3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
4.  **Run the application (FastAPI)**:
    ```bash
    uvicorn main:app --reload
    ```
5.  **Access the Dashboard**: Open your browser and navigate to `http://127.0.0.1:8000`.

## 📂 Project Structure
- `main.py`: The FastAPI application and API endpoints.
- `app_logic.py`: The core ScribeAgent logic including Selenium automation and data extraction.
- `templates/`: Contains `index.html` (the primary dashboard).
- `data/`: The local vault where all your extracted JSON, CSV, and Markdown files are stored.

---

### 🎓 Learn More
**Subscribe my chennel for more AI and Data Science learning Videos:**
👉 [**CODE WITH BHUTTAG**](https://www.youtube.com/@CODEWITHBHUTTAG)

---
*Developed with ❤️ for the Data Science & AI community.*
