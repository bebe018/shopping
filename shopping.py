import socket
import secrets
from flask import Flask
from flask import request
from flask import redirect
from flask import Markup
from flask import render_template
from flask import session
from flask_bcrypt import Bcrypt
from modules import connect_to_MongoDB , flask_tb, reset_password_email
from validate_email import validate_email



shopping=Flask(
    __name__,
    static_folder="static",
    static_url_path="/static",
    template_folder="templates"
    
)

shopping.secret_key=""

bcrypt=Bcrypt(shopping)

@shopping.route("/")
def index():
    return render_template("index.html")

@shopping.route("/search_results")
def search_results():
    search = "%s" % request.args.get("search")
    if search != "" and not search.isspace():
        collection = connect_to_MongoDB.get_connection("products")
        query = {
            "product_name":{
                "$regex": "[%s]" % search,
                "$options": "i"
            }
        }
        count = collection.count_documents(query)
        if count != 0:
            documents, search_results, = collection.find(query).sort("category"),""
            for docu in documents:
                search_results += """
                <a href="/products/%s">
                    <img src="/static/%s.jpg" width="100" height="100" style="vertical-align: middle;" />%s
                </a><br /><br />
                """ % (docu["category"], docu["category"], docu["product_name"])
            search_results = Markup(search_results)
        else:
            search_results = "Sorry, there are no match keyword %s in our shopping website." % search
        return render_template("search_results.html", search_results=search_results, search=search)
    else:
        search_results = "You must input somthing."
        return render_template("search_results.html", search_results=search_results, search=search)
    
    
    



@shopping.route("/products/<category>", methods=["POST","GET"])
def products(category):
    if request.method != "POST":
        return render_template("%s.html" % category)
    else:
        collection, query = connect_to_MongoDB.get_connection("products"), {"category": "%s" % category}
        docu = collection.find_one(query)
        product_name, price, quantity = docu["product_name"], docu["price"], request.form["quantity"]
        if "username" not in session:
            col = "cart" + str(socket.gethostbyaddr(request.remote_addr))
        else:
            col = "cart" + str(socket.gethostbyaddr(request.remote_addr))
            collection = connect_to_MongoDB.get_connection(col)
            count = collection.estimated_document_count(col)
            col = "cart(%s)" % session["username"]
            if count != 0:
                collection.rename(col, dropTarget=True)
        collection = connect_to_MongoDB.get_connection(col)
        subtotal = int(price) * int(quantity)
        newvalues = {
            "$set":{
                "product_name":product_name,
                "price":price,
                "quantity":quantity,
                "subtotal":subtotal,
                "last_modified":"0"
            }
        }
        collection.update_one(query, newvalues, upsert=True)
        return render_template("%s.html" % category)



@shopping.route("/cart")
def cart():
    if "username" not in session:
        return render_template("login.html")
    else:
        col = "cart" + str(socket.gethostbyaddr(request.remote_addr))
        collection = connect_to_MongoDB.get_connection(col)
        col = "cart(%s)" % session["username"]
        if collection.estimated_document_count() != 0:
            collection.rename(col, dropTarget=True)
        collection = connect_to_MongoDB.get_connection(col)
        count = collection.estimated_document_count()
        if count != 0:
            documents, items, total= collection.find().sort("category"), [], 0
            for docu in documents:
                category = """
                <a href="/products/%s">
                    <img src="/static/%s.jpg" width="100" height="100" style="vertical-align: middle;" />%s
                </a>
                """ % (docu["category"], docu["category"], docu["product_name"])
                quantity = """
                <form action="/cart_modify" method="POST">
                    <input type="hidden" name="category" value="%s" />
                    <select name="quantity" onchange="this.form.submit()">
                        <option value="1">1</option>
                        <option value="2">2</option>
                        <option value="3">3</option>
                        <option value="4">4</option>
                        <option value="5">5</option>
                        <option value="6">6</option>
                        <option value="7">7</option>
                        <option value="8">8</option>
                        <option value="9">9</option>
                        <option value="10">10</option>
                    </select>
                </form>
                """.replace("<option value=\"%s\">" % docu["quantity"],
                            "<option value=\"%s\" selected>" % docu["quantity"]) % docu["category"]
                delete = """
                <form action="/cart_delete" method="POST">
                    <input type="hidden" name="category" value="%s" />
                    <input type="image" src="/static/delete.jpg" alt="Delete" width="25" height="25" />
                </form>
                """ % docu["category"]
                if docu["last_modified"] != 0:
                    query, newvalue = {"category":docu["category"]}, {"$set":{"last_modified":"0"}}
                    collection.update_one(query, newvalue)
                    # quantity = quantity.replace("<select name=\"quantity\" onchange=\"this.form.submit()\">",
                    #                             "<select name=\"quantity\" onchange=\"this.form.submit()\" autofocus>")
                items.append(flask_tb.Item(Markup(category), docu["price"], Markup(quantity), docu["subtotal"], Markup(delete)))
                total += int(docu["subtotal"])
            total = "{:.2f}".format(total)
            items.append(flask_tb.Item("Total:", "", "", total,""))
            table = flask_tb.ItemTable(items)
        else:
            collection.drop()
            table = "You have nothing in the cart"
        return render_template("cart.html", table = table)

@shopping.route("/cart_modifify", methods=["POST"])
def cart_modify():
    if "username" not in session:
        return redirect("/login")
    else:
        col = "cart(%s)" % session["username"]                
        collection = connect_to_MongoDB.get_connection(col)
        category, quantity = "%s" % request.form["category"], "%s" % request.form["quantity"]
        query = {"category":category}
        docu = collection.find_one(query)
        price = docu["price"]
        subtotal = int(price) * int(price)
        newvalues= {
            "$set":{
                "quantity" : quantity, 
                "subtotal" : subtotal, 
                "last_mofified" : "1"
            }
        }
        collection.update_one(query, newvalues, upsert=True)
        return redirect("/cart")
                
@shopping.route("/cart_delete", methods=["POST"])
def cart_delete():
    if "username" not in session:
        return redirect("/login")
    else:
        col = "cart(%s)" % session["username"]
        collection = connect_to_MongoDB.get_connection(col)
        category = "%s" % request.form["category"]
        query = {"category":category}
        collection.delete_one(query)
        return redirect("/cart")

    

@shopping.route("/login",methods=["POST","GET"])
def login():
    if request.method!="POST" and "username" not in session:
        return render_template("login.html")
    elif request.method!="GET" and "username" not in session:
        session
        username=f'{request.form["username"]}'.lower()
        password=f'{request.form["password"]}'
        collection, query= connect_to_MongoDB.get_connection("accounts"), {"username":username}
        count=collection.count_documents(query)
        if count!=0:
            account = collection.find_one(query)
            check_password = bcrypt.check_password_hash(account["password"] , password)
            if check_password != True:
                error = "Wrong Password, please type the password correctly!"
                return render_template("login.html", username=username, error=error)
            else:
                session["username"] = username
                return render_template("action.html", action = "Hello %s, Welcome to shopping website!" % username)
        else:
            error = "This account %s doesn't exist!" % username
            return render_template("login.html", username=username, error=error)
    else:
        return redirect("/member")
    
@shopping.route("/logout")
def logout():
    if "username" not in session:
        return redirect("/login")
    else:
        session.pop("username", None)
        action="Logout successfully"
        return render_template("action.html", action=action)

@shopping.route("/signup", methods=["POST","GET"])
def signup():
    if request.method!="POST" and "username" not in session:
        return render_template("signup.html")
    elif request.method != "GET" and "username" not in session:
        username, password, Check_Password, email = "%s".lower() % request.form["username"], request.form["password"], request.form["Check_Password"], request.form["email"]
        collection, query = connect_to_MongoDB.get_connection("accounts"), {"username":username}
        if username.isalnum() != True:
            error = "Error, the username can only contain numbers and letters"
            return render_template("signup.html", usernme = username, error = error, email = email)
        elif not len(username) >= 6 and len(username) <= 16:
            error = "Error, the length of username must between 6-16."
            return render_template("signup.html", username = username, error = error, email = email)
        elif collection.count_documents(query) != 0:
            error = "Error, the username: %s has been used" % username
            return render_template("signup.html", error = error, username = username, email = email)
        if password != "" and " " not in password:
            if not len(password) >= 8 and len(password) <= 16:
                error = "Error, the length of paaword must between 8-16."
                return render_template("signup.html", username = username, error = error, email = email)
        else:
            error = "Error, the password should not contain space"
            return render_template("sign.html", username = username, error = error, email = email)
        if password != Check_Password:
            error = "Error, the password is not eqaul to Check_Password"
            return render_template("signup.html", username = username, error = error, email = email)

        email_valid = validate_email(email_address=email, check_format=True, check_blacklist=True, check_dns=True,
                                     dns_timeout=1, check_smtp=True, smtp_timeout=1, smtp_helo_host=None,
                                     smtp_from_address=None, smtp_debug=False)
        if email_valid == True:
            collection, query = connect_to_MongoDB.get_connection("accounts"), {"email":email}
            count = collection.count_documents(query)
            if count != 0:
                error = "Error, the email address has been used."
                return render_template("signup.html", username = username, error = error, email = email)
            else:
                password = bcrypt.generate_password_hash(password)
                document = {
                    "username":username,
                    "password":password,
                    "email":email,
                    "urlsafe":"0"
                }
                collection.insert_one(document)
                return render_template("action.html", action="We're happy to have you here")
        else:
            error = "Error, invalid email address"
            return render_template("signup.html", username= username, error = error, email = email)
    else:
        return redirect("/member")


@shopping.route("/member", methods=["POST","GET"])
def member():
    if "username" not in session:
        return redirect("/login")
    elif request.method != "POST":
        return render_template("member.html", username="%s" % session["username"])
    else:
        password = "%s" % request.form["password"]
        collection, query = connect_to_MongoDB.get_connection("accounts"), {"username": "%s" % session["username"]}
        docu = collection.find_one(query)
        check_password = bcrypt.check_password_hash(docu["password"], password)

        if check_password != True:
            error = "Error, Wrong password"
            return render_template("member.html", error=error, username="%s" % session["username"])

        new_password, check_new_password = "%s" % request.form["new_password"], "%s" % request.form["check_new_password"]

        if new_password != "" and " " not in new_password:
            if not (len(new_password) >=8 and len(new_password) <= 16):
                error = "Error, the length of password must between 8-16."
                return render_template("member.html", error=error, username="%s" % session["username"])
        else:
            error = "Error, the password should not contain space."

        if new_password != check_new_password:
            error = "Error, the new_password is not equal to check_new_password"
            return render_template("member.html", error=error, username="%s" % session["username"])
        else:
            new_password = bcrypt.generate_password_hash(new_password)
            newvalue = {"$set":{"password":new_password}}
            collection.update_one(query,newvalue)
            action = "Modified Password Successfully"
            return render_template("action.html", action = action)


@shopping.route("/forgot_password", methods=["POST", "GET"])
def forgot_password():
    if request.method != "POST" and "username" not in session:
        return render_template("forgot_password.html")
    elif request.method != "GET" and "username" not in session:
        email = "%s" % request.form["email"]
        collection, query = connect_to_MongoDB.get_connection("accounts"), {"email":email}
        count = collection.count_documents(query)
        if count != 0:
            docu = collection.find_one(query)
            username, urlsafe = docu["username"], secrets.token_urlsafe()
            newvalue = {"$set":{"urlsafe":urlsafe}}
            collection.update_one(query,newvalue)
            url = "http://127.0.0.1:3000/reset_password/%s/%s" % (username,urlsafe)
            reset_password_email.send(email,url)
            action="Please check your inbox to reset password"
            return render_template("action.html", action = action)
        else:
            error = "Error, the email: %s does not exist" % email
            return render_template("forgot_password.html", error=error, email = email)
    else:
        return redirect("/member")

@shopping.route("/reset_password/<username>/<urlsafe>", methods=["GET","POST"])
def reset_password(username, urlsafe):
    if request.method != "POST":
        collection = connect_to_MongoDB.get_connection("accounts")
        query = {
            "username":"%s".lower() % username,
            "urlsafe":"%s" % urlsafe
        }
        count = collection.count_documents(query)
        if count != 0:
            return render_template("reset_password.html", username="%s" % username, urlsafe="%s" % urlsafe)
        else:
            return redirect("/")
    else:
        password, check_password = "%s" % request.form["password"], "%s" % request.form["check_password"]
        if password != "" and " " not in password:
            if not(len(password) >= 8 and len(password) <= 16):
                error = "Error, the length od password must between 8-16."
                return render_template("reset_password.html", error=error, username=username, urlsafe=urlsafe)
        else:
            error = "Error, the password should not contain space"
            return render_template("reset_password.html", error=error, username=username, urlsafe=urlsafe)

        if password != check_password:
            error = "Error, the password is not equal to check_password"
            return render_template("resrt_password.html", error=error, username=username, urlsafe=urlsafe)
        else:
            password = bcrypt.generate_password_hash(password)
            query = {
                "username":username,
                "urlsafe":urlsafe
            }
            newvalues = {
                "$set":{
                    "password":password,
                    "urlsafe":"0"
                }
            }
            collection = connect_to_MongoDB.get_connection("accounts")
            collection.update_one(query,newvalues)
            return render_template("action.html", action="Reset password successfully")
            



if __name__=='__main__':
    shopping.run(port=3000)
