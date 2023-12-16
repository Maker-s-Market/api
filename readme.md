# Maker's Market API

Maker's Market is an e-commerce platform for buying and selling handmade goods. This repository contains the backend code for the application.

## Features

- **Product Management**: Handles all product-related operations, including product creation, updates, and deletion.
- **Shopping Cart Management**: Manages user's shopping cart, including adding products, removing products, and checkout operations.
- **User Authentication**: Handles user registration, login, and profile update operations.
- **Product Reviews and Ratings**: Manages reviews and ratings for products.
- **Seller Tools**: Provides endpoints for sellers to manage their products.
- **Search and Category Filtering**: Provides search functionality and category-based filtering for products.
- **Wishlist Management**: Manages user's wishlist, including adding and removing products.
- **Order History**: Provides endpoints for users to view their past orders.

## Tech Stack

- **Backend**: Python
- **Package Management**: pip

## Getting Started

To get a local copy up and running, follow these steps:

1. Clone the repository.
2. Install the required pip packages using `pip install -r requirements.txt`.
3. Start the development server.

## Code Structure

The codebase is organized into several directories:

- `app/routes`: Contains the different routes of the application, such as product routes, user routes, and order routes.
- `app/models`: Contains the data models used in the application.
- `app/services`: Contains the business logic for handling different operations.
- `app/utils`: Contains utility functions and components like authentication middleware.