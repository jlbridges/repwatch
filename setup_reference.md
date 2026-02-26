# Setup Reference for RepWatch

This document serves to help you get a working development environment going on your machine.

You will need Python 3.12 - 3.14 (I use Python 3.14.0)
## First time setup

1. **Initialize venv**  
When setting up for the first time, use the following command to initialize venv:  
`py -m venv .venv`  
Then enable it with  
`.\.venv\Scripts\activate`

2. **Install dependencies**  
`py -m pip install -r requirements.txt`

3. **Run migrations**  
`py manage.py migrate`

4. **Create admin user (optional)**  
`py manage.py createsuperuser`

After that, you're done with one-time setup.

## Continuing in environment

If you have already completed the setup, follow these steps to continue working with codebase.

1. **Enable venv if not enabled**  
`.\.venv\Scripts\activate`

## Common Commands

These are commands you will use often.

### Run Server ★
`py manage.py runserver`

### Re-run Migrations ★
`py manage.py migrate`

### Create migrations (only after adding models)  
`py manage.py makemigrations`

### Django shell  
`py manage.py shell`

## Current functioning URLs

http://127.0.0.1:8000 - Root URL, redirects to login when logged out
http://127.0.0.1:8000/accounts/login - Login (logging in takes you to dashboard view)
http://127.0.0.1:8000/accounts/signup/ - Register
http://127.0.0.1:8000/admin/ - Default django admin console