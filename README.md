<!-- ![Website Screenshot - Landing Page](./assets/landing_page_screenshot.png) -->

# College Marketplace 🛒🎓
![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)
![HTML5](https://img.shields.io/badge/html5-%23E34F26.svg?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/css3-%231572B6.svg?style=for-the-badge&logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/javascript-%23323330.svg?style=for-the-badge&logo=javascript&logoColor=%23F7DF1E)
![MySQL](https://img.shields.io/badge/mysql-4479A1.svg?style=for-the-badge&logo=mysql&logoColor=white)

> **⚠️ Branch Notice:** The **`main`** branch is the active, updated, and upstream version of this project. The **`master`** branch represents the older legacy version. All new development, pull requests, and checkouts should use the **`main`** branch.

## 📖 Introduction

Welcome to **College Marketplace**! This is a web-based application built with Flask, designed to connect students from different colleges through an online marketplace. The application allows users to explore and purchase products sold by various student organizations from the eight colleges of your institution.

The platform features a seller dashboard for organizations to manage their products and orders, while users can browse products from different colleges, place orders, and view their purchase history.

## 🌿 Repository & Branching Structure

- **`main` (Upstream / Active)**: Contains the latest refactored architecture, including:
  - Database schema migrations CLI (`flask db migrate`, `flask db status`, `flask db create`).
  - Resource-safe connection management with `get_db_cursor`.
  - CSRF protection (`Flask-WTF`) and enhanced session security.
  - Reusable authentication decorators (`@login_is_required`, `@seller_required`).
  - Comprehensive automated test suite (`pytest`) and linting (`ruff`).
- **`master` (Legacy)**: The initial legacy version of the application preserved for historical reference.

## ✨ Features

- **Landing Page**: Introduction to the platform with links to sign up or sign in.
- **User Authentication**: Secure user registration, login system, and Google OAuth integration.
- **Explore Page**: Browse products across various colleges.
- **Seller Dashboard**: Manage products, view orders, track sales, and export order CSVs.
- **College-Specific Pages**: Dedicated storefronts for all 8 colleges (CASS, CBA, CCS, CED, COE, CHS, CSM).
- **Order Management**: Preorder tracking, order cancellation, and proof-of-payment receipt uploads.
  
## 🤖 Technologies Used

- **Flask**: Web framework for backend routing and application logic.
- **MySQL**: Relational database managing users, organizations, products, and orders.
- **Flask-WTF & WTForms**: CSRF security and form validation.
- **Cloudinary**: Cloud image storage and management.
- **Pytest**: Automated testing framework.
- **Ruff**: Fast Python linter and formatter.
- **HTML5 / CSS3 / JavaScript**: Responsive and interactive user interface.

## 🤔 Prerequisites

Before you begin, ensure you have met the following requirements:

- **Python 3.10+** and **Pipenv** installed.
- **MySQL Server** installed and running.
- Cloudinary credentials and Google OAuth client secrets (for full feature functionality).

## 💿 Installation & Setup

1. **Clone the repository and checkout `main`**:
    ```bash
    git clone https://kishonshrill-admin@bitbucket.org/kishonshrill/unigear.git
    cd unigear
    git checkout main
    ```

2. **Configure Environment Variables**:
   - Create and configure your `.env` file in the project root with database credentials, Flask secret key, Cloudinary keys, and mail configuration.

3. **Install Python dependencies**:
    ```bash
    pipenv install --dev
    ```
    If you encounter Pipenv or dependency issues, consult [DEBUG.md](./DEBUG.md).

4. **Configure the Database**:
   - Create a MySQL database:
     ```sql
     CREATE DATABASE college_marketplace;
     ```
   - Apply all pending schema migrations:
     ```bash
     flask db migrate
     ```
   - *(Optional Fallback)*: You can restore sample data directly using the SQL dump:
     ```bash
     mysql -u root -p college_marketplace < unigear_sample_data.sql
     ```

5. **Run the Flask Application**:
    ```bash
    flask run --debug
    ```
    Or explicitly referencing the application entry point:
    ```bash
    flask --app run.py run --debug
    ```
    Or on a custom host/port:
    ```bash
    flask run --host=localhost --port=5000 --debug
    ```

6. **Access the application**:
   Open your browser and navigate to `http://localhost:5000`.

## 🧪 Testing & Code Quality

- **Run the Pytest suite**:
  ```bash
  pipenv run pytest
  ```
- **Check code quality with Ruff**:
  ```bash
  pipenv run ruff check .
  ```
- **Format code**:
  ```bash
  pipenv run ruff format .
  ```

## ⚠️ Usage

- **Landing Page**: Start by signing up or signing in to your account.
- **Explore Products**: Browse products available from different colleges via the "Explore" page.
- **Seller Dashboard**: If you are a seller, access your dashboard to manage products and orders.
- **College Pages**: Navigate to specific college pages to explore products sold by organizations from that college.
- **Orders**: Users can view and manage their orders through their account page, and sellers can view order history.

---
