# Epicure Backend
Epicure is a comprehensive restaurant management system that offers features such as table reservations, menu management, special offers, and payment processing.

## Project Overview
Epicure backend provides a RESTful API for managing restaurants, reservations, menu items, orders, and user profiles. The system is designed to be integrated with the Epicure frontend application.

## Technologies Used
- **Python 3.11**
- **Django & Django REST Framework**
- **JWT Authentication**
- **Swagger/OpenAPI Documentation**
- **Docker & Docker Compose**
- **Stripe Payment Integration**
- **Google OAuth Integration**

## Frontend Repository
The frontend repository is available at:
[https://github.com/kalkadam404/Epicure_frontend](https://github.com/kalkadam404/Epicure_frontend)

## Live Demo
The application is deployed and accessible at:
[https://epicuresite.vercel.app/KZ](https://epicuresite.vercel.app/)


## Features
- User authentication and profile management
- Restaurant profile management
- Menu and product catalog
- Table reservations and room bookings
- Special promotional offers
- Online payments via Stripe
- City-based filtering

## Installation and Setup

### Prerequisites
- Python 3.11+
- Docker and Docker Compose (optional, for containerized setup)
- Git

### Option 1: Using Docker
1. Clone the repository:
```bash
git clone <repository-url>
cd Epicure-Backend/Epicure
```

2. Create a `.env` file in the root directory with necessary environment variables:
```
DEBUG=True
SECRET_KEY=your_secret_key
```

3. Run with Docker Compose:
```bash
docker-compose up --build
```

The API will be available at: http://localhost:8000

### Option 2: Local Setup
1. Clone the repository:
```bash
git clone <repository-url>
cd Epicure-Backend/Epicure
```

2. Create and activate a virtual environment:
```bash
python -m venv myenv
source myenv/bin/activate  # On Windows: myenv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

5. Create a superuser (optional):
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

The API will be available at: http://localhost:8000

## API Documentation
Once the server is running, you can access the API documentation at:
- Swagger UI: `http://localhost:8000/api/docs/swagger/`
- ReDoc: `http://localhost:8000/api/docs/redoc/`

## Environment Variables
The following environment variables can be configured:
- `DEBUG`: Set to 'True' or 'False' (default: 'True')
- `SECRET_KEY`: Django secret key
- `STRIPE_SECRET_KEY`: Stripe API secret key
- `STRIPE_PUBLISHABLE_KEY`: Stripe publishable key
- `STRIPE_WEBHOOK_SECRET`: Stripe webhook secret
- `FRONTEND_BASE_URL`: Frontend application URL

## Project Structure
The project consists of several Django applications:
- `cities`: City management
- `users`: User authentication and profiles
- `restaurant`: Restaurant management
- `products`: Menu and product management
- `offers`: Special offers and promotions
- `table_service`: Table reservation system
- `room`: Room booking system
- `payments`: Payment processing with Stripe

## Testing
Run tests with:
```bash
python manage.py test
```

## Contributing
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License
This project is licensed under the MIT License.