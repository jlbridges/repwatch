# RepWatch – Templates Documentation 👁️

This directory contains Django HTML templates

Structure:
- `registration/` contains templates used by Django's authentication system
- Top-level templates are application pages (homepage, login, signup, dashboard)

Templates are resolved via Django's template loader

---

## Directory Structure:

### base.html

The main layout template. 

contains:
- Global HTML structure
- Navigation bar
- Footer
- CSS links from static folder
- Template blocks

### homepage.html

lanfing page of the application. User will be able to raed about our goal web app, and the login or signup.

Purpose: 
- intrduces RepWatch
- Displays welcom content
- Navigation entry point (login and signup)

### account/login.html

User authenticated page. For current user will be able to introduce their gmail and passwords in order to login.

Purpose:
- Login form
- Error handling display
- Django form rendering

### account/signup.html

User registration page. For new user, they will introduce their names, gamil, and password.

Purpose:
- User registration form
- Form validation feedback
- Styled input fields

## dashboard.html

User dashboard nterface. After the user login or signup will be ale to see the dashboard.

Purpose:
- Displays user-specific data
- Structured layout for reports/monitoring
- Organized content sections

Tabs:

- Overview:
    - Your representatives --> spring #2
        - Name
        - US senador
    - Tracked Legislation --> spring #3
        - label or number bill
        - Official tittle of the bill


- My reps:
    - Photo
    - First name
    - Last name
    - U.S. Senator    -
    - Politic Party and where state is.
    ---------
    - Term expires: MM/DD/YYYY
    ----------
    - Legislative activity:
        - sponsored: 
        - Co-sponsored: 
    ----------
    Policy Focus
    (example: Agriculture, samll Business, ect...)
    ----------
    Committeess
    (examples: committee on Armed Services, Veterans' Affairs, etc...)
    ----------
    Personal contact (out fo scope):
        - Phone
        - Email

- My Bills (Display):
    - label or number bill
    - Official tittle of the bill
    - Status
    -----------
    - tag
    - Congress-specific
    - Cosponsors
    -----------
    - Sponsor and politic party (D or R)
    - Introduced: MM/DD/YYYY
    - Summary
    - Latest Action

- Search:
    - Find Representatives:
        - Stret Address
        - city
        - State
        - ZIP

    - Search Bills:
        - Search Bills
        - Status
        - Policy Subject
        - Sponsor Name
        - Date From
        - Date To

- Settings:
    - Display: "Profile information (manage your account details and contac information)"
    - Full Name
    - Email
    - address (street, city, State, Zip)
    - reset passwords
    - Delete profile

