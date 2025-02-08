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
cd projet_final_data_viz ```

2️⃣ **Install dependencies (Using Poetry)**

```bash
poetry install

3️⃣ **Run the application**

```bash
streamlit run src/projet_final_data_viz/app.py 

### ✅ Best Practices Followed

-Robust prompt engineering to handle various data inputs.

-Meaningful visualizations to enhance data understanding.

-Software development best practices, including testing and documentation.

### 📂 Project Structure

```bash
├── .github/workflows/      # CI/CD workflows  
├── docs/                   # Sphinx documentation  
├── src/projet_final_data_viz/  # Main application code  
├── tests/                  # Unit tests  
├── pyproject.toml          # Project dependencies  
└── README.md               # Project overview  


