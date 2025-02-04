# Data Visualization Application with Streamlit

## Overview

This project utilizes **Streamlit** and **Pandas** to build an interactive web application that facilitates data exploration, analysis, and visualization. The app is designed to allow users to easily upload datasets, perform statistical analysis, and create visualizations, all in a user-friendly interface.

By using this application, users can quickly gain insights from their data, making it an ideal tool for data analysis, data science projects, and exploratory data visualization.

## Key Features

- **Data Import**: Upload CSV files directly into the application for analysis.
- **Statistical Analysis**: View descriptive statistics such as mean, median, standard deviation, and detect missing values within datasets.
- **Interactive Visualizations**: Generate a variety of visualizations including:
  - Histograms
  - Boxplots
  - Correlation heatmaps
- **Dynamic Column Selection**: Choose columns from the dataset (both numerical and categorical) for targeted analysis and visualization.
- **Customizable Plots**: Modify the appearance and styling of generated plots, such as color palettes and labels.

## Project Structure

The project is structured to keep the code organized and modular:

projet_final/ 
├── app.py # Main application script that runs the Streamlit app 
├── auth.py # User authentication logic (if applicable) 
├── api.py # API interactions for external data or services 
├── utils.py # Utility functions for data processing and analysis
├── tests/ # Unit tests and test cases to ensure code quality 
├── .github/ # GitHub Actions workflows for CI/CD integration 
├── .gitignore # Git ignore file to exclude unnecessary files from version control 
├── .pre-commit-config.yaml # Configuration for pre-commit hooks to enforce code quality
├── poetry.lock # Poetry lock file to manage dependencies 
├── pyproject.toml # Poetry configuration for the project 
└── README.md # Project documentation (this file)
