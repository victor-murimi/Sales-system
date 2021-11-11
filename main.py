from flask import Flask, request, render_template, redirect, flash, session
from functools import wraps
from flask.helpers import url_for
import psycopg2


conn = psycopg2.connect(database='myduka', user='postgres',
                        host='localhost', password='0742978312', port='5432')

# conn = psycopg2.connect(database='dchl22fvc5rqoo', user='xnvpmadkuzsgll',
#                         host='ec2-54-195-195-81.eu-west-1.compute.amazonaws.com',
#                          password='d018681e80fd99ec185da392c5a79692bcf01272e1945eb79457f77fb8e4264d',
#                           port=5432)
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS product1(id serial PRIMARY KEY,name VARCHAR(100),buying_price INT, selling_price INT,stock_quantity INT);")
cur.execute("CREATE TABLE IF NOT EXISTS sales(id serial PRIMARY KEY,product_id INT,quantity INT,created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW())")
cur.execute("CREATE TABLE IF NOT EXISTS users(id serial PRIMARY KEY,email VARCHAR(30),username VARCHAR(20),password VARCHAR(15))")
conn.commit()
app = Flask(__name__)

app.secret_key = 'super secret key'

    
@app.route("/")
def index():

    # session['logged_in'] = False
    # if session['logged_in'] == False:
    user = None
    return render_template("index.html", user =user )


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized! Please log in', 'danger')
            return redirect(url_for('login', next=request.url))
    return wrap


@app.route("/login", methods=["POST", "GET"])
# @login_required
def login():
    
    if request.method == "POST":
        cur = conn.cursor()
        z = request.form["email"]
        y = request.form["password"]
        cur.execute(
            """SELECT * from users WHERE email=%(z)s OR password=%(y)s """, {"z": z, "y": y})
        user = cur.fetchone()
        # ail=[]
        # word=[]

        if user:
            # session['logged_in'] = True
            # login_user(user)
            print("something")
            print(user)
            if user[1] == z and user[3] == y:
                session["user"] = user
                print("correct credentials")
                return redirect(url_for('dashboard'))

            else:
                print("kataa")
                return redirect(url_for('login'))

        else:
            print("User does not exist")
            return redirect(url_for('login'))

    else:

        flash("login unseccessful")
        return render_template('login.html')


@app.route("/signup", methods=["POST", "GET"])
def signup():
    if request.method == "POST":
        cur=conn.cursor()
        email=request.form["email"]
        username=request.form["username"]
        password=request.form["password"]
        cur.execute("""SELECT email FROM users""")
        allemails=cur.fetchall()
        print(allemails)
        myemails=[]
        for mail in allemails:
          myemails.append(mail[0])
          print(myemails)

        if email not in myemails:
            cur.execute("""INSERT INTO users (email,username,password) VALUES(%(email)s,%(username)s,%(password)s);""", {
                "email": email, "username": username, "password": password})
            conn.commit()
            print(" si hapa", email)

        else:
            pass
            flash("email  already exists")
            print("hapa", email)
            return redirect("/login")

    else:
        print("not found")
        return render_template("signup.html")


@app.route("/inventory", methods=["POST", "GET"])
@login_required
def inventory():
    if "user" in session:
      user=session["user"]
      
      if request.method == "POST":
            cur=conn.cursor()
            m=request.form["name"]
            n=request.form["BP"]
            o=request.form["SP"]
            p=request.form["quantity"]
            cur.execute("""INSERT INTO product1(
        name, buying_price, selling_price, stock_quantity)
        VALUES (%(m)s,%(n)s,%(o)s,%(p)s);""", {"m": m, "n": n, "o": o, "p": p})
            conn.commit()
            # print(m,n,o,p)

            return redirect("/inventory")
      else:
            cur=conn.cursor()
            cur.execute("""SELECT *  from product1""")
            y=cur.fetchall()

            return render_template("inventory.html", y=y)
    else:
         return redirect(url_for("login"))
@app.route("/sales", methods=["POST", "GET"])
# @login_required
def sales():
    if "user" in session:
        user=session["user"]
        if request.method == "POST":
            cur=conn.cursor()
            r=request.form["product_id"]
            g=request.form["quantity"]
            cur.execute(
                """ select stock_quantity from product1 where id=%(r)s""", {"r": r})
            y=cur.fetchone()
            g=int(g)
            # print(g)
            b=y[0]-g
            # print(b)
            if b >= 0:
                cur.execute(""" UPDATE product1 SET stock_quantity=%(b)s WHERE id=%(g)s""", {
                            "b": b, "g": g})
                cur.execute("""INSERT INTO sales(product_id,quantity) VALUES(%(r)s,%(g)s);""", {
                            "r": r, "g": g})
                conn.commit()
                # print(r,g)

                return redirect("/sales")
            else:
                pass
        else:
            cur=conn.cursor()
            cur.execute("""SELECT * from sales""")
            x=cur.fetchall()

            return render_template("sales.html", x=x)
    else:
        return redirect(url_for("login"))

@app.route("/dashboard")
def dashboard():
    cur=conn.cursor()
    cur.execute(""" SELECT product1.name ,SUM(sales.quantity)FROM sales JOIN product1 ON sales.product_id=product1.id
    GROUP BY product1.name""")
    h=cur.fetchall()
    g=[]
    c=[]
    for o in h:
        g.append(o[0])
        c.append(o[1])
    # print(g)
    cur.execute("""SELECT sum((product1.selling_price-product1.buying_price)*sales.quantity) as profit,name FROM product1 JOIN sales on  sales.product_id=product1.id group by product1.name""")
    j=cur.fetchall()
    f=[]
    v=[]
    for i in j:
        f.append(i[0])
        v.append(i[1])
    # print(j)
    return render_template("dashboard.html", j=j, f=f, v=v, h=h, g=g, c=c)


@app.route("/stock")
# @login_required
def stock():
    return render_template("stock.html")


if __name__ == "__main__":
    app.run(debug=True)
