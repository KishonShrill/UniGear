# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Environment Setup
- Activate/enter virtual environment:
  ```bash
  pipenv shell
  ```
- Install dependencies:
  ```bash
  pipenv install --dev
  ```

### Database Setup & Migrations
- Apply all pending database schema migrations:
  ```bash
  flask db migrate
  ```
- Check migration status:
  ```bash
  flask db status
  ```
- Create a new migration file:
  ```bash
  flask db create <migration_name>
  ```
- Manual database restore (optional fallback):
  ```bash
  mysql -u root -p college_marketplace < unigear_sample_data.sql
  ```

### Running the Application
- Run development server with debug mode:
  ```bash
  flask run --debug
  ```
  or explicitly referencing the application entry point:
  ```bash
  flask --app run.py run --debug
  ```
- Run on custom host/port:
  ```bash
  flask run --host=localhost --port=5000 --debug
  ```

### Testing & Code Quality
- Run the full test suite with pytest:
  ```bash
  pipenv run pytest
  # Or run a specific test file
  pipenv run pytest tests/test_migrations.py
  ```
- Run linting with Ruff:
  ```bash
  pipenv run ruff check .
  # Auto-fix linting issues
  pipenv run ruff check --fix .
  ```
- Check code formatting:
  ```bash
  pipenv run ruff format --check .
  # Format code
  pipenv run ruff format .
  ```

## Architecture & Code Structure

### Overview
UniGear (College Marketplace) is a Flask-based multi-college e-commerce web application where student organizations from 8 colleges can sell merchandise and manage preorders, and students can browse, order, and submit payment proof.

### Application Factory & Configuration
- **`run.py`**: Loads `.env` and initializes the Flask application by calling `create_app()`.
- **`config.py`**: Reads environment variables for database credentials, Cloudinary, Mailtrap/SMTP, and Flask `SECRET_KEY`.
- **`app/__init__.py`**: Configures Flask-MySQLdb, CSRF protection (`Flask-WTF`), Cloudinary SDK, session lifetimes, error handlers (`401`, `404`), and registers blueprints.

### Blueprints & Routes (`app/routes/`)
- **`auth.py` (`auth_bp`)**: Handles registration (`/sign-up`, `/sign-up2`), sign-in (`/sign-in`), Google OAuth verification, session state, and route protection decorators:
  - `@login_is_required`: Enforces user session authentication (aborts with `401` if not logged in).
  - `@seller_required`: Enforces seller role authorization (`session['role'] == 'seller'`).
- **`website.py` (`website_bp`)**: Public browsing, landing page (`/`), explore page (`/explore`), search, product view, and order placement.
- **`colleges.py` (`colleges_bp`)**: College storefront routes (`/college-<college_code>`) for all 8 colleges (CASS, CBA, CCS, CED, COE, CHS, CSM) and API to fetch student organizations by college.
- **`seller.py` (`seller_bp`)**: Seller dashboard (`/seller/my-products`, `/seller/my-orders`), product CRUD operations, preorder status toggling, CSV exports, and Cloudinary image uploads.
- **`user.py` (`user_bp`)**: Student order tracking (`/user/my-orders`), order cancellation, proof-of-payment receipt uploads, wishlist, and profile management.

### Models & Data Access (`app/models/`)
Data access relies on parameterized raw SQL queries using the exception-safe `get_db_cursor` context manager (`app/utils/db.py`) rather than an ORM.
- **`User` (`app/models/user.py`)**: User authentication, password hashing (`werkzeug.security`), role assignment (`user` vs `seller`), and Google account provisioning.
- **`Product` (`app/models/product.py`)**: Product lifecycle management, sizing mappings (`product_sizes`), picture associations (`pictures`), preorder counts vs goals, catalog queries, and order pagination.
- **`Order` (`app/models/order.py`)**: Order creation (`ordered_by`), atomic preorder placement, status tracking (`0` unpaid, `1` paid), receipt fetching, payment proof uploads, and order deletion.
- **`Organization` (`app/models/organization.py`)**: College-to-organization mapping and executive council sorting queries.
- **`Favorite` (`app/models/favorite.py`)**: User wishlist queries and atomic favorite toggling.

### Utilities & Infrastructure (`app/utils/` & `app/cli.py`)
- **`app/utils/db.py`**: Exception-safe `get_db_cursor` context manager handling cursor lifecycles, connection commits (`commit=True`), and rollback recovery on errors.
- **`app/utils/migrator.py`**: Lightweight raw SQL migration engine supporting multi-statement execution, DDL/DML transactions, `schema_migrations` tracking, and automatic file scaffolding.
- **`app/utils/image_service.py`**: Cloudinary upload/deletion abstraction with file validation and public ID extraction.
- **`app/utils/decorators.py`**: Route authentication and authorization decorators (`@login_is_required`, `@seller_required`).
- **`app/utils/helpers.py`**: Address parsing/formatting and size conversions.
- **`app/cli.py`**: Flask CLI integration providing `flask db` subcommands.

### Database Schema (`migrations/` & `unigear_sample_data.sql`)
- **`college` & `organization`**: Relational hierarchy of colleges and student organizations.
- **`user`**: Users with roles (`user` or `seller`) optionally linked to an `org_id`.
- **`products`**: Product listings with types, price, order type (regular or preorder), release dates, and goals.
- **`sizes` & `product_sizes`**: Size definitions and stock/preorder quantities per product.
- **`pictures`**: Cloudinary URLs associated with products.
- **`favorites`**: User product wishlist mappings.
- **`ordered_by`**: Order transactions linking users, products, sizes, quantities, payment status, and proof of payment URLs.
- **`schema_migrations`**: Migration history tracking table.
