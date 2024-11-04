<!-- ![Website Screenshot - Landing Page](./assets/landing_page_screenshot.png) -->

# College Marketplace 🛒🎓
![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)
![HTML5](https://img.shields.io/badge/html5-%23E34F26.svg?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/css3-%231572B6.svg?style=for-the-badge&logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/javascript-%23323330.svg?style=for-the-badge&logo=javascript&logoColor=%23F7DF1E)
![MySQL](https://img.shields.io/badge/mysql-4479A1.svg?style=for-the-badge&logo=mysql&logoColor=white)

## 📖 Introduction

Welcome to **College Marketplace**! This is a web-based application built with Flask, designed to connect students from different colleges through an online marketplace. The application allows users to explore and purchase products sold by various student organizations from the eight colleges of your institution.

The platform features a seller dashboard for organizations to manage their products and orders, while users can browse products from different colleges, place orders, and view their purchase history.

## ✨ Features

- **Landing Page**: Introduction to the platform with links to sign up or sign in.
- **User Authentication**: Secure user registration and login system.
- **Explore Page**: Browse products from various colleges.
- **Seller Dashboard**: Manage your products, view your orders, and track your sales.
- **College-Specific Pages**: Separate pages for each of the 8 colleges where users can explore products.
- **Order Management**: Users can track their orders, and sellers can manage orders from their dashboard.
  
## 🤖 Technologies Used

- **Flask**: Web framework used for the backend logic.
- **MySQL**: Database used to manage user accounts, products, and orders.
- **HTML/CSS/JavaScript**: Frontend technologies for designing a responsive and user-friendly interface.

## 🤔 Prerequisites

Before you begin, ensure you have met the following requirements:

- Python 3.x installed on your machine.
- MySQL server installed and running.
- Basic knowledge of Flask and MySQL.

## 💿 Installation

1. **Clone the repository**:
    ```bash
    git clone https://kishonshrill-admin@bitbucket.org/kishonshrill/unigear.git
    cd unigear
    ```

2. **Ask for the `.env` file to activate dot-env variables**

3. **Install the required Python packages**:
    ```bash
    pipenv install --dev
    ```

4. **Configure the database**:
   - Create a MySQL database named `college_marketplace`.
   - Update the `config.py` file with your MySQL credentials.
   - Run the following command to initialize the database:
        - Enter MySQL Terminal
        ```bash
        mysql -u root -p
        ```
        - Inside MySQL Terminal
        ```sql
        CREATE DATABASE college_marketplace;
        EXIT;
        ```
        - Back to Bash Terminal
        ```bash
        mysql -u root -p college_marketplace < initSQLData.sql
        ```

5. **Run the Flask application**:
    ```bash
    flask run --debug
    ```
    ⚠️ Use this command below if it doesn't work ⚠️
    ```bash
    flask --app run.py run --debug
    
    flask run --host=localhost --port=5000 --debug
    ```

6. **Access the application**:
   Open your browser and go to `http://localhost:5000`.

## ⚠️ Usage

- **Landing Page**: Start by signing up or signing in to your account.
- **Explore Products**: Browse products available from different colleges via the "Explore" page.
- **Seller Dashboard**: If you are a seller, access your dashboard to manage products and orders.
- **College Pages**: Navigate to specific college pages to explore products sold by organizations from that college.
- **Orders**: Users can view and manage their orders through their account page, and sellers can view order history.

---