# Opensource G-ADK Agents

A powerful, open-source AI agent interface built with Google's Agent Development Kit (ADK), FastAPI, and LiteLLM. This project demonstrates how to build interactive data science agents that can query databases, visualize data with dynamic charts, and provide intelligent insights via a modern chat interface.

## Features

-   **Interactive Chat Interface**: A beautiful, mobile-responsive UI with glassmorphism design, streaming responses, and markdown support.
-   **Data Science Agent**: Analyze data from a SQLite database (convertible to AlloyDB) using natural language.
-   **Dynamic Visualizations**: Generate interactive Bar, Line, Scatter, and Pie charts using Plotly.
-   **Database Manager**: Built-in UI to view, edit, and manage your database tables directly.
-   **Open Source & Low Cost**: Designed to work with open-source models via LiteLLM (supports OpenAI, Anthropic, Bedrock, etc. with compatible APIs).
-   **Mobile Ready**: Fully optimized for mobile devices with touch-friendly scrolling and layout.

## Tech Stack

-   **Frontend**: HTML5, Vanilla CSS (Glassmorphism), JavaScript, Plotly.js, FontAwesome.
-   **Backend**: Python, FastAPI.
-   **AI Framework**: Google ADK (Agent Development Kit).
-   **LLM Integration**: LiteLLM (Universal LLM API).
-   **Database**: SQLite (Local demo), scalable to PostgreSQL/AlloyDB.

## Prerequisites

-   Python 3.10+
-   An API Key for your preferred LLM provider (e.g., OpenAI, Groq, etc.)

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/opensource-g-adk-agents.git
    cd opensource-g-adk-agents
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment:**
    Create a `.env` file in the root directory and add your API credentials:
    ```env
    GROQ_API_KEY=your_groq_api_key_here
    ```

## Running the Application

1.  **Initialize the Database:**
    Run the setup script to create the sample database:
    ```bash
    python setup_database.py
    ```

2.  **Start the Server:**
    Run the FastAPI server with hot reload:
    ```bash
    uvicorn app.main:app --reload
    ```

3.  **Access the App:**
    Open your browser and navigate to:
    -   Chat Interface: `http://127.0.0.1:8000`
    -   Data Manager: `http://127.0.0.1:8000/static/data_manager.html`

## Usage

-   **Ask Questions**: "Show me a pie chart of sales by product", "What is the total revenue?", "Plot a line chart of sales over time".
-   **Manage Data**: Use the Data Manager to add new sales records or modify existing data to test the agent's capabilities.

## License

This project is open-source and available under the simple MIT License.
