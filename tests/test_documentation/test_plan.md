TEST PLAN
1. Overview

This test plan verifies the functionality of the web application, focusing on:

User authentication (login/logout/registration)
Dashboard access and stability
Profile and settings (address validation & updates)
Bill management (save/remove)
Bill search and filtering
External API integrations (Smarty, Geocodio)


2. Test Objectives
✔ Ensure users can authenticate correctly
✔ Ensure dashboard loads without errors
✔ Ensure profile updates only save valid addresses
✔ Ensure invalid addresses are rejected
✔ Ensure users can save/remove bills
✔ Ensure search filters work correctly
✔ Ensure API failures do not crash the app


3. Scope
In Scope
Backend logic (views, models, services)
API validation (mocked + real behavior)
Database interactions
User session handling


Out of Scope
Frontend styling/UI layout
Performance/load testing
Security penetration testing


4. Test Strategy
Type	Description
Unit Testing	Helper functions and services
Integration Testing	Views + DB interactions
API Mock Testing	External services mocked
End-to-End	Client requests through Django test client


5. Test Environment
Framework: Django 5.x
Language: Python 3.13
Test Tool: pytest
Database: SQLite (test DB)
OS: Windows


6. Test Data
Valid Address:
123 Main St, Raleigh, NC 27601

Invalid Address:
Main Street
Fake City, NC 00000

User:
john@example.com / SuperSecret123

Sample Bill:
HR 123 – Test Bill


7. Test Cases
Authentication
ID	Test	Expected Result
TC-01	User login	Session created
TC-02	Wrong password	Login fails
TC-03	Logout	Session cleared


Dashboard
ID	Test	Expected Result
TC-04	Access dashboard (logged in)	Page loads (200)
TC-05	Access without login	Redirect to login


Profile / Settings
ID	Test	Expected Result
TC-06	Valid address update	Profile updated
TC-07	Invalid address update	No change
TC-08	Missing fields	Validation error


Bills
ID	Test	Expected Result
TC-09	Save bill	User added to tracked_by
TC-10	Remove bill	User removed
TC-11	View saved bills	Displayed in My Bills


Search
ID	Test	Expected Result
TC-12	Search by title	Matching bills shown
TC-13	Filter by congress	Correct results
TC-14	Filter by type	Correct results
TC-15	No results	Empty state shown


API Handling
ID	Test	Expected Result
TC-16	Smarty valid address	Returns cleaned data
TC-17	Smarty invalid address	Returns None
TC-18	API failure	App does not crash


8. Risks
⚠ External API rate limits
⚠ Missing API credentials
⚠ Database schema mismatches
⚠ Tests relying on live API responses