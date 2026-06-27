# Accounts App API Documentation (Auth & Role-Based Access)

This document contains detailed information on API endpoints, payloads, role-based access controls (RBAC), and step-by-step instructions for testing JWT authentication in the accounts app.

---

## 1. API Endpoints Reference

### A. User Registration
*   **Endpoint**: `POST /api/accounts/register/`
*   **Access**: Public (Anonymous)
*   **Role Rules**: 
    *   Anyone can register as a `customer` (default).
    *   To register a user with role `theatre_manager` or `admin`, you must authenticate using an `admin` token in the request header.
*   **Request Payload**:
    ```json
    {
      "username": "johndoe",
      "email": "johndoe@example.com",
      "password": "SecurePassword123!",
      "confirm_password": "SecurePassword123!",
      "phone": "9876543210",
      "first_name": "John",
      "last_name": "Doe",
      "role": "customer"
    }
    ```
*   **Success Response (201 Created)**:
    ```json
    {
      "id": 2,
      "username": "johndoe",
      "email": "johndoe@example.com",
      "role": "customer",
      "phone": "9876543210",
      "first_name": "John",
      "last_name": "Doe",
      "date_joined": "2026-06-27T11:00:00Z"
    }
    ```

---

### B. User Login (Obtain JWT)
*   **Endpoint**: `POST /api/accounts/login/`
*   **Access**: Public (Anonymous)
*   **Request Payload**: Supports logging in with either the **username** or **email**.
    ```json
    {
      "username_or_email": "johndoe",
      "password": "SecurePassword123!"
    }
    ```
*   **Success Response (200 OK)**:
    ```json
    {
      "user": {
        "id": 2,
        "username": "johndoe",
        "email": "johndoe@example.com",
        "role": "customer",
        "phone": "9876543210",
        "first_name": "John",
        "last_name": "Doe",
        "date_joined": "2026-06-27T11:00:00Z"
      },
      "tokens": {
        "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
      }
    }
    ```

---

### C. Retrieve/Update User Profile
*   **Endpoint**: `GET` / `PUT` / `PATCH` `/api/accounts/profile/`
*   **Access**: Authenticated users only (`IsAuthenticated`)
*   **Header**: `Authorization: Bearer <access_token>`
*   **Request Payload (PUT / PATCH)**:
    ```json
    {
      "first_name": "Johnny",
      "phone": "9999999999",
      "username": "johndoe",
      "email": "johndoe@example.com"
    }
    ```
*   **Success Response (200 OK)**:
    ```json
    {
      "id": 2,
      "username": "johndoe",
      "email": "johndoe@example.com",
      "role": "customer",
      "phone": "9999999999",
      "first_name": "Johnny",
      "last_name": "Doe",
      "date_joined": "2026-06-27T11:00:00Z"
    }
    ```

---

### D. Change Password
*   **Endpoint**: `POST /api/accounts/change-password/`
*   **Access**: Authenticated users only (`IsAuthenticated`)
*   **Header**: `Authorization: Bearer <access_token>`
*   **Request Payload**:
    ```json
    {
      "old_password": "SecurePassword123!",
      "new_password": "NewSecurePassword456!",
      "confirm_new_password": "NewSecurePassword456!"
    }
    ```
*   **Success Response (200 OK)**:
    ```json
    {
      "detail": "Password has been changed successfully."
    }
    ```

---

### E. Token Refresh
*   **Endpoint**: `POST /api/token/refresh/`
*   **Access**: Public (Anonymous)
*   **Request Payload**:
    ```json
    {
      "refresh": "<refresh_token>"
    }
    ```
*   **Success Response (200 OK)**:
    ```json
    {
      "access": "new_access_token_value..."
    }
    ```

---

## 2. Step-by-Step Guidance to Test JWT Auth

You can test these endpoints using an API Client (e.g., **Postman** or VS Code extension **Thunder Client**). 

### Step 1: Start the Server
First, run your local development server:
```powershell
.\venv\Scripts\python manage.py runserver
```

### Step 2: Register a New Customer Account
1. Open your API client (Postman/Thunder Client).
2. Set the method to **`POST`** and enter the URL: `http://127.0.0.1:8000/api/accounts/register/`
3. Select **Body** -> **JSON** and paste the payload:
   ```json
   {
     "username": "customer1",
     "email": "customer1@example.com",
     "password": "PasswordTest123!",
     "confirm_password": "PasswordTest123!",
     "phone": "9876543210",
     "first_name": "Alice",
     "last_name": "Smith"
   }
   ```
4. Click **Send**. You should receive a `201 Created` status with the user details (password is omitted for security).

### Step 3: Login to Obtain Your JWT Tokens
1. Set the method to **`POST`** and URL to: `http://127.0.0.1:8000/api/accounts/login/`
2. Select **Body** -> **JSON** and log in using either the username or email:
   ```json
   {
     "username_or_email": "customer1@example.com",
     "password": "PasswordTest123!"
   }
   ```
3. Click **Send**.
4. In the response body, locate the `tokens` object. **Copy** the value of the `"access"` token.

### Step 4: Access a Protected Endpoint (e.g., Profile)
1. Set the method to **`GET`** and URL to: `http://127.0.0.1:8000/api/accounts/profile/`
2. First, click **Send** without adding any headers. 
   *   *Expected Result*: Status `401 Unauthorized` with detail `"Authentication credentials were not provided."`
3. Now, go to the **Headers** tab.
4. Add a new header:
   *   **Key**: `Authorization`
   *   **Value**: `Bearer <paste_your_copied_access_token_here>`
   *(Make sure there is a space between `Bearer` and the token code).*
5. Click **Send** again.
   *   *Expected Result*: Status `200 OK` with your registered profile details.

### Step 5: Test Role-Based Restrictions
1. Log out (or clear credentials) and try to register an admin account anonymously.
2. Set the method to **`POST`** and URL to: `http://127.0.0.1:8000/api/accounts/register/`
3. Enter the following JSON body (asking for `admin` role):
   ```json
   {
     "username": "fake_admin",
     "email": "fake_admin@example.com",
     "password": "PasswordTest123!",
     "confirm_password": "PasswordTest123!",
     "role": "admin"
   }
   ```
4. Click **Send**.
   *   *Expected Result*: Status `400 Bad Request` with response payload:
       ```json
       {
         "role": [
           "Only administrators can register users with elevated roles."
         ]
       }
       ```
5. To register this admin, you would have to add an `Authorization: Bearer <admin_token>` header using an already authenticated admin's access token.

### Step 6: Test Token Expiry & Refresh
1. Under settings.py, the `ACCESS_TOKEN_LIFETIME` is configured to `60 minutes`.
2. Once the access token expires, accessing `/api/accounts/profile/` will return a `401 Unauthorized` response with a code indicating the token has expired.
3. Instead of prompting the user to login again, send a request to:
   *   **Method**: `POST`
   *   **URL**: `http://127.0.0.1:8000/api/token/refresh/`
   *   **Body (JSON)**:
       ```json
       {
         "refresh": "<your_refresh_token_from_step_3>"
       }
       ```
4. Clicking **Send** will return a fresh `access` token. Use this new token to continue making authorized requests!
