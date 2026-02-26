# RepWatch Django Templates

This folder contains the Django HTML templates for RepWatch’s UI. Most pages extend `base.html` and use [Bootstrap](https://getbootstrap.com/) (via CDN) for layout and styling.

---

## Folder Structure

```
templates/
├─ about.html
├─ base.html
├─ dashboard.html
├─ homepage.html
├─ login.html
└─ signup.html
```

> **Note:** In this repo, auth templates live at the top level (`login.html`, `signup.html`) rather than under `registration/` or `account/`.

---

## `base.html` (Shared Layout)

`base.html` provides:

- Shared `<head>` assets (Bootstrap + Bootstrap Icons via CDN)
- Optional header/nav + footer
- Template blocks used by child templates

### Template Blocks

- `{% block title %}` — Page title  
- `{% block content %}` — Main page content  

### Expected Context Variables

- `showlayout` (`bool`) — If `true`, show header/footer; if `false`, render only page content  
- `page` (`str`) — Used for simple nav/behavior switches (e.g., `"homepage"`, `"dashboard"`)  
- `user` — Used for the dashboard welcome message  

---

## Page Templates

### `homepage.html`
- Landing page  
- Loads `static/css/homepage.css`  
- Links to sign up / log in  

### `dashboard.html`
- Authenticated dashboard  
- Uses Bootstrap nav-pills tabs  
- Includes a Change Password section  
- Expects:
  - `passwordform`
  - Optionally `passwordsuccess`

### `login.html`
- Login form with CSRF  
- Shows field and non-field errors  
- Treats email as the username  

### `signup.html`
- Registration form with CSRF  
- Shows field and non-field errors  
- Includes typical user/address fields + password confirmation  

### `about.html`
- Informational page  
- Extends `base.html`  

---

## Styling

- Bootstrap is loaded in `base.html`
- Bootstrap Icons are loaded in `base.html`
- Custom homepage CSS lives in `static/css/homepage.css`  

> Keep custom CSS minimal; prefer Bootstrap utility classes.

---

## Adding a New Template

1. Start with:
   ```django
   {% extends "base.html" %}
   ```

2. Add `{% load static %}` only if you use static assets.

3. Put HTML inside:
   ```django
   {% block content %}
   {% endblock %}
   ```

4. In your view context, set:
   ```python
   showlayout = True
   ```
   to display the standard header/footer.

---

## Troubleshooting

- **Header/footer missing:** Check `showlayout`
- **Nav/conditional behavior wrong:** Confirm `page` is set (e.g., `"homepage"` or `"dashboard"`)
- **CSS/images missing:** Verify static files are configured and served correctly (and collected in production)