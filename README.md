# Description
This is a simple shopping demo. Basically, there are two features in this project:
1. Membership: create account, log in, log out and reset password.
2. Cart: add to cart, view your items that you want to buy and edit or delete items.

# Structure
## Front End
HTML, CSS, JavaScript
## Programming Language
Python
## Web Application Framework
Flask
## Database
MongoDB

# Prerequisites
1. [Python ≥ 3.6](https://www.python.org/downloads/)
2. [MongoDB Community Server](https://www.mongodb.com/try/download/community)
3. Install required python packages: `pip install -r requirements.txt`
4. Go to lines 30 and replace the e-mail username and password with yours in modules/reset_password_email.py: (If you don't use gmail, then you must edit lines 29 to your SMTP hostname and port too.)
    
    # Send the message via SMTP server.
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login("Your e-mail address", "Your application password") 
        <!-- (p.s the application password please check the link below https://support.google.com/mail/answer/185833?hl=zh-Hant)
        server.send_message(message) -->
    
5. Go to lines 23 and replace the secret key with yours in shopping.py:<br />
    5.1 Lines 23 in shopping.py:
    
    # set up the secret key to save session
    shopping.secret_key = 'Secret key'
    
    5.2 How to generate a nice secret key:
    
    >>> import secrets
    >>> secrets.token_urlsafe(16)
        for example the key will like 'n2LzE3WSktAQua3EqwAX6A'
6. Here is the basic shopping website function.
    Login
    ![image](https://github.com/bebe018/shopping/blob/master/Login.png)
    Cart
    ![image](https://github.com/bebe018/shopping/blob/master/Cart.png)
    Forgot Password
    ![image](https://github.com/bebe018/shopping/blob/master/Forgot%20Password.png)
    Modify Password
    ![image](https://github.com/bebe018/shopping/blob/master/Modify%20Password.png)
    
  
# Test It Locally
Now, you can test it locally by the following commands:
1. `cd shopping`
2. `py shopping.py`
