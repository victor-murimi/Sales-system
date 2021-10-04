from flask import Flask, request, render_template, redirect
from flask.helpers import url_for
import psycopg2

# conn = psycopg2.connect(database='myduka', user='postgres',host='localhost',password='0742978312',port='5432')

conn = psycopg2.connect(database='dchl22fvc5rqoo', user='xnvpmadkuzsgll',
                        host='ec2-54-195-195-81.eu-west-1.compute.amazonaws.com',
                         password='d018681e80fd99ec185da392c5a79692bcf01272e1945eb79457f77fb8e4264d',
                          port=5432)
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS product1(id serial PRIMARY KEY,name VARCHAR(100),buying_price INT, selling_price INT,stock_quantity INT);")
cur.execute("CREATE TABLE IF NOT EXISTS sales(id serial PRIMARY KEY,product_id INT,quantity INT,created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW())")
cur.execute("CREATE TABLE IF NOT EXISTS users(id serial PRIMARY KEY,user_name VARCHAR(25),email VARCHAR(25),password VARCHAR(15))")
conn.commit()
app = Flask(__name__)


@app.route("/")
def index():

    return render_template("index.html")


@app.route("/login",methods=["POST","GET"])
def login():
    if request.method =="POST":
        cur=conn.cursor()
        z=request.form["email"]
        y=request.form["password"]
        cur.execute("""SELECT %(z)s from users where id=%(y)s""",{"z":z,"y":y})
        conn.commit()
        return redirect("/dashboard")
    else:
        print("not found")
        return render_template("login.html")

@app.route("/signup",methods=["POST","GET"])
def signup():
    if request.method =="POST":
      cur=conn.cursor()
      a=request.form["email"]
      b=request.form["username"]
      c=request.form["password"]
      cur.execute("""INSERT INTO users (user_name,email,password)VALUES(%(a)s,%(b)s,%(c)s);""",{"a":a,"b":b,"c":c})
      conn.commit()
      return redirect("/dashboard")
    else:
        print("not found")
        return render_template("signup.html")


@app.route("/inventory", methods=["POST", "GET"])
def inventory():
    if request.method == "POST":
        cur = conn.cursor()
        m = request.form["name"]
        n = request.form["BP"]
        o = request.form["SP"]
        p = request.form["quantity"]
        cur.execute("""INSERT INTO product1(
	 name, buying_price, selling_price, stock_quantity)
	VALUES (%(m)s,%(n)s,%(o)s,%(p)s);""", {"m":m, "n": n, "o": o, "p": p})
        conn.commit()
        # print(m,n,o,p)

        return redirect("/inventory")
    else:
        cur = conn.cursor()
        cur.execute("""SELECT *  from product1""")
        y = cur.fetchall()
        
        return render_template("inventory.html", y=y)


@app.route("/sales", methods =["POST","GET"])
def sales():
    if request.method == "POST":
        cur = conn.cursor()
        r = request.form["product_id"]
        g = request.form["quantity"]
        cur.execute(""" select stock_quantity from product1 where id=%(r)s""",{"r":r})
        y=cur.fetchone()
        g=int(g)
        # print(g)
        b=y[0]-g
        # print(b)
        if b>=0:
            cur.execute(""" UPDATE product1 SET stock_quantity=%(b)s WHERE id=%(g)s""",{"b":b,"g":g})
            cur.execute("""INSERT INTO sales(product_id,quantity) VALUES(%(r)s,%(g)s);""",{"r":r,"g":g})
            conn.commit()
            # print(r,g)

            return redirect("/sales")
        else:
            pass    
    else:
     cur = conn.cursor()
     cur.execute("""SELECT * from sales""")
     x = cur.fetchall()
     
     return render_template("sales.html", x=x)


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
    return render_template("dashboard.html",j=j,f=f,v=v,h=h,g=g,c=c)


@app.route("/stock")
def stock():
    return render_template("stock.html")


if __name__ == "__main__":
    app.run(debug=True)
