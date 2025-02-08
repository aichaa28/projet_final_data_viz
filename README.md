# 📊 Final Data Viz Project

## 🚀 Project Overview

This project aims to develop an application that:  
- Accepts **any tabular dataset** as input.  
- **Answers questions** about the dataset.  
- Generates **multiple visualizations and interpretations** to provide meaningful insights.  

The goal is to build a robust and efficient interface that ensures relevant results while handling various data input challenges.  

## 🛠️ Technologies Used

### 📌 **AI Models**
- **TAPAS**: A model by Google designed for answering questions on tables.  
- **Claude**: An advanced natural language processing model used for question understanding.  

### 📌 **Deployment Framework**
The application is developed and deployed using **Streamlit**, providing an interactive and user-friendly interface.  

## 📖 Documentation

The full documentation is available [here](https://aichaa28.github.io/projet_final_data_viz/).  
It includes:  
- **Project setup and installation guide**  
- **Usage instructions**  
- **Technical details on TAPAS and Claude integration**  

## 🔧 Installation & Usage

1️⃣ **Clone the repository**  
```bash
git clone https://github.com/aichaa28/projet_final_data_viz.git
cd projet_final_data_viz
```

2️⃣ **Install dependencies (Using Poetry)**

```bash
poetry install
```

3️⃣ **Run the application**

```bash
streamlit run src/projet_final_data_viz/app.py 
 ```
### ✅ Best Practices Followed

-Robust prompt engineering to handle various data inputs.

-Meaningful visualizations to enhance data understanding.

-Software development best practices, including testing and documentation.

### 📂 Project Structure

## 📂 Project Structure

- **.github/**                  # GitHub Actions workflows
  - **workflows/**               # CI/CD workflows
- **docs/**                      # Sphinx documentation
- **src/**                       # Main source code
  - **projet_final_data_viz/**   # Application logic
    - **__init__.py**            # Initialization file
    - **agents.py**              # Claude integration
    - **api.py**                 # API related logic
    - **app.py**                 # Main app file
    - **auth.py**                # Authentication logic
    - **description.py**         # Description handling
    - **tapas_code.py**          # TAPAS model related code
- **tests/**                     # Unit tests
  - **__pycache__**              # Cached bytecode
  - **__init__.py**              # Initialization file
  - **test_api.py**              # API tests
  - **test_app.py**              # App tests
  - **test_auth.py**             # Authentication tests
  - **test_description.py**      # Description tests
  - **test_tapas.py**            # TAPAS model tests
- **.coverage**                  # Code coverage report
- **.gitignore**                 # Git ignore file
- **.pre-commit-config.yaml**    # Pre-commit configuration
- **pyproject.toml**             # Project dependencies
- **poetry.lock**                # Poetry lock file
- **pytest.ini**                 # Pytest configuration
- **README.md**                  # Project overview
- **utils.py**                   # Utility functions


