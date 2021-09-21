from flask import Flask, request, render_template, redirect
# from flask.helpers import url_for
import psycopg2


conn = psycopg2.connect(database='dchl22fvc5rqoo', user='xnvpmadkuzsgll',
                        host='ec2-54-195-195-81.eu-west-1.compute.amazonaws.com',
                         password='d018681e80fd99ec185da392c5a79692bcf01272e1945eb79457f77fb8e4264d',
                          port='5432')
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS product1(id serial PRIMARY KEY,name VARCHAR(100),buying_price INT, selling_price INT,stock_quantity INT);")
cur.execute("CREATE TABLE IF NOT EXISTS sales(id serial PRIMARY KEY,product_id INT,quantity INT,created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW())")
conn.commit()
app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


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
        print(g)
        b=y[0]-g
        print(b)
        if b>=0:
            cur.execute(""" UPDATE product1 SET stock_quantity=%(b)s WHERE id=%(g)s""",{"b":b,"g":g})
            cur.execute("""INSERT INTO sales(product_id,quantity) VALUES(%(r)s,%(g)s);""",{"r":r,"g":g})
            conn.commit()
            print(r,g)

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
    # cur.execute(""" SELECT sum((product1.selling_price-buying_price)*sales,quantity) as profit FROM product1 JOIN sales on sales.product_id=product1.id """)
    # s=cur.fetchall()
    # c=[]
    # n=[]
    # for i in s:
    #     c.append([s])
    #     n.append([s])
    #     print(s)
    cur.execute("""SELECT sum((product1.selling_price-product1.buying_price)*sales.quantity) as profit FROM product1 JOIN sales on  sales.product_id=product1.id group by product1.name""")
    j=cur.fetchall()
    f=[]
    v=[]
    for i in j:
        f.append(j[0])
        v.append(j[1])
        print(j)
    return render_template("dashboard.html",j=j,f=f,v=v)


@app.route("/stock")
def stock():
    return render_template("stock.html")


app.run()
