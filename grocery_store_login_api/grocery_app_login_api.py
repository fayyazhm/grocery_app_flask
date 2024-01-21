from flask import Flask,render_template,request,redirect
from models_grocery_login import *
from datetime import datetime,date,timedelta
from sqlalchemy.exc import IntegrityError
from flask_login import LoginManager,login_user,current_user,login_required,UserMixin,logout_user
from flask_restful import Api, Resource, reqparse, marshal_with, fields,abort


app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///grocery_login.sqlite3"
app.config['SECRET_KEY']= "SECRETKEYSECRETKEYSECRETKEY121213121312"
api=Api(app)
db.init_app(app)
login_manager=LoginManager()
login_manager.init_app(app)
app.app_context().push() 

#-----------------------------------------admin---------------------------------------------------------------------------------#

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)


@app.route("/admin",methods=["GET","POST"])
def admin():
    if request.method=='POST':
        all_values=request.form.to_dict()   
        user=all_values['username']
        password=all_values['password']
        det=Users.query.filter_by(username=user,role='admin').first()
        if det==None:
            return render_template('Invalid_username.html')  
        else:
            if det.password==password:
                login_user(det) 
                cat=Category.query.all()
                prod=Product.query.order_by(desc(Product.product_id)).all()
                if cat!=[]:
                    return render_template('category_present.html',cat=cat,prod=prod)
                else:
                    return render_template('category_home.html')
            else:
                return render_template('Invalid_username.html')    
    
    return render_template('admin_login.html')

@app.route("/admin/category", methods=["GET", "POST"])
@login_required
def add_category():
    if request.method=='GET' and current_user.role=='admin':
        return render_template('category_add.html')
    if request.method=='POST' and current_user.role=='admin':
        all_values=request.form.to_dict()
        new_category=Category(category_name=all_values['category_name']) 
        try:
            db.session.add(new_category)
            db.session.commit()
            cat=Category.query.all()
            prod=Product.query.order_by(desc(Product.product_id)).all()
            return render_template('category_present.html',cat=cat,prod=prod)
        except:
            return render_template('category_already_error.html',category_name=all_values['category_name'])


@app.route("/admin/category/edit/<int:category_id>", methods=["GET", "POST"])
@login_required
def edit_category(category_id):
    if request.method=='GET' and current_user.role=='admin':
        cat=Category.query.filter_by(category_id=category_id).first()
        return render_template('category_edit.html',cat=cat)
    if request.method=='POST' and current_user.role=='admin':
        all_values=request.form.to_dict()
        cat=Category.query.filter_by(category_id=category_id).first()
        for i in all_values:
            if i=='category_name':
                cat.category_name=all_values['category_name']
        try:
            db.session.commit()
            cat=Category.query.all()
            prod=Product.query.order_by(desc(Product.product_id)).all()
            return render_template('category_present.html',cat=cat,prod=prod)
        except IntegrityError:
            db.session.rollback()
            return render_template('category_already_error.html',category_name=all_values['category_name'])    

@app.route("/admin/category/delete/confirm/<int:category_id>")
@login_required
def deletcategoryconfirm(category_id):
    if current_user.role=='admin':
        cat=Category.query.filter_by(category_id=category_id).first()
        return render_template('category_deleteconfirm.html',cat=cat)

@app.route("/admin/category/delete/<int:category_id>")
@login_required
def deletcategory(category_id):
    if current_user.role=='admin':
        cat=Category.query.filter_by(category_id=category_id).first()
        prod=Product.query.filter_by(product_category=category_id).all()
        if prod!=[]:
            for i in prod:
                db.session.delete(i)
        db.session.delete(cat)
        try:
            db.session.commit()
            cat=Category.query.all()
            prod=Product.query.order_by(desc(Product.product_id)).all()
            if cat!=[]:
                return render_template('category_present.html',cat=cat,prod=prod)
            else:
                return render_template('category_home.html')
        except IntegrityError:
            db.session.rollback()
            return render_template('category_error.html',cat=cat)

@app.route("/admin/home", methods=["GET", "POST"])
@login_required
def admin_home():
    if request.method=='GET' and current_user.role=='admin':
        cat=Category.query.all()
        prod=Product.query.order_by(desc(Product.product_id)).all()
        if cat!=[]:
            return render_template('category_present.html',cat=cat,prod=prod)
        else:
            return render_template('category_home.html')
        

#----------------------------------------------------------admin/product/----------------------------------------------------------------------
@app.route("/admin/product/<int:category_id>", methods=["GET", "POST"])
@login_required
def add_product(category_id):
    if request.method=='GET' and current_user.role=='admin':
        cat=Category.query.filter_by(category_id=category_id).first()
        return render_template('product_add.html',category_name=cat.category_name,category_id=cat.category_id)
    if request.method=='POST' and current_user.role=='admin':
        all_values=request.form.to_dict()
        cat=Category.query.filter_by(category_id=category_id).first()
        [a,b,c]=all_values['product_expirydate'].split('-')
        exp_date=date(int(a),int(b),int(c))
        new_product=Product(product_name=all_values['product_name'],product_quantity=all_values['product_quantity'],product_manufacture=all_values['product_manufacture'],
                            product_rate=all_values['product_rate'],product_expirydate=exp_date,product_category=cat.category_id)       
        try:
            db.session.add(new_product)
            db.session.commit()
            cat=Category.query.all()
            prod=Product.query.order_by(desc(Product.product_id)).all()
            return render_template('category_present.html',cat=cat,prod=prod)
        except:
            return render_template('product_already_error.html',product=all_values['product_name'])
    
@app.route("/admin/product/edit/<int:product_id>", methods=["GET", "POST"])
@login_required
def edit_product(product_id):
    if request.method=='GET' and current_user.role=='admin':
        prod=Product.query.filter_by(product_id=product_id).first()
        cat=Category.query.filter_by(category_id=prod.product_category).first()
        return render_template('product_edit.html',prod=prod,cat=cat)
    if request.method=='POST' and current_user.role=='admin':
        all_values=request.form.to_dict()
        prod=Product.query.filter_by(product_id=product_id).first()
        for i in all_values:
            if i =='product_name':
                prod.product_name=all_values[i]
            if i=='product_quantity':
                prod.product_quantity=all_values[i]
            if i=='product_expirydate':
                [a,b,c]=all_values['product_expirydate'].split('-')
                exp_date=date(int(a),int(b),int(c))
                prod.product_expirydate=exp_date
            if i=='product_manufacture':
                prod.product_manufacture=all_values[i]
            if i=='product_rate':
                prod.product_rate=all_values[i]
            if i=='product_quantity':
                prod.product_quantity=all_values[i]
        try:
            db.session.commit()
            cat=Category.query.all()
            prod=Product.query.order_by(desc(Product.product_id)).all()
            return render_template('category_present.html',cat=cat,prod=prod)
        except:
            return render_template('product_already_error.html',product=all_values['product_name'])


@app.route("/product/delete/conf/<int:product_id>", methods=["GET", "POST"])
@login_required
def delete_confproduct(product_id):
    if current_user.role=='admin':
        prod=Product.query.filter_by(product_id=product_id).first()
        cat=Category.query.filter_by(category_id=prod.product_category).first()
        return render_template('product_deleteconfirm.html',cat=cat,prod=prod)

@app.route("/product/delete/<int:product_id>", methods=["GET", "POST"])
@login_required
def delete_product(product_id):
    if current_user.role=='admin':
        prod=Product.query.filter_by(product_id=product_id).first()
        try:
            db.session.delete(prod)
            db.session.commit()
            cat=Category.query.all()
            prod=Product.query.order_by(desc(Product.product_id)).all()
            return render_template('category_present.html',cat=cat,prod=prod)
            
        except IntegrityError:
            db.session.rollback()
            return render_template('product_error.html',prod=prod)
#--------------------------------------------------------------admin/summary----------------------------------------------------------------------------#

@app.route("/admin/summary", methods=["GET", "POST"])
@login_required
def summary():
    if current_user.role=='admin':
        return render_template('admin_summary.html')

@app.route("/admin/summary/category",methods=["GET","POST"])
@login_required
def categorysummary():
    if current_user.role=='admin':
        catq=Category.query.all()
        catl=[]
        for i in catq:
            catl.append(i.category_id)
        prodl={}
        totl={}
        proda={}
        ordl={}
        prod=Product.query.all()
        for i in catl:
            prodl[i]=[]
            totl[i]=0
            proda[i]=0   
        for i in prod:
            prodl[i.product_category].append(i.product_id)
            proda[i.product_category]+=i.product_quantity

        sora=[]
        for i in proda:
            sora.append(proda[i])
        sora.sort(reverse=True)
 
        sorc=[]
        
        for i in sora:
            for c in proda:
                if proda[c]==i:
                    sorc.append(c)
 
        cat=[]
        for i in sorc:
            for c in catq:
                if i==c.category_id:
                    cat.append(c)
        ord=Order.query.all()

        for i in ord:
            if i.order_productid not in ordl:
                ordl[i.order_productid]=i.order_qty
            else:
                ordl[i.order_productid]+=i.order_qty
        
        for i in ordl:
            for c in prodl:
                if i in prodl[c]:
                    totl[c]+=ordl[i]
        return render_template("category_summary.html",catl=catl,prodl=prodl,cat=cat,totl=totl,proda=proda)


@app.route("/admin/summary/category/<int:category_id>",methods=["GET","POST"])
@login_required
def categoryprodsummary(category_id):
    if current_user.role=='admin':
        prod=Product.query.filter_by(product_category=category_id).order_by(desc(Product.product_quantity)).all()
        ordl={}
        total_aqty=0
        for i in prod:
            ordl[i.product_id]=0
            total_aqty+=i.product_quantity
        total_pqty=0
        ord=Order.query.all()
        for i in ord:
            if i.order_productid in ordl:
                ordl[i.order_productid]+=i.order_qty
                total_pqty+=i.order_qty
        cat=Category.query.filter_by(category_id=category_id).first()
        return render_template('product_summary.html',prod=prod,ordl=ordl,dat=date.today(),total_pqty=total_pqty,total_aqty=total_aqty,cat=cat)

@app.route("/admin/summary/product",methods=["GET","POST"])
@login_required
def productsummary():
    if current_user.role=='admin':
        prod=Product.query.order_by(desc(Product.product_quantity)).all()
        ordl={}
        total_aqty=0
        for i in prod:
            ordl[i.product_id]=0
            total_aqty+=i.product_quantity
        ord=Order.query.all()
        total_pqty=0
        for i in ord:
            ordl[i.order_productid]+=i.order_qty
            total_pqty+=i.order_qty
    
        return render_template('product_summary.html',prod=prod,ordl=ordl,dat=date.today(),total_pqty=total_pqty,total_aqty=total_aqty,cat='cat')

@app.route("/admin/summary/order",methods=["GET","POST"])
@login_required
def ordersummary():
    if current_user.role=='admin':
        tot=Total.query.all()
        ord=Order.query.all()
        user=Users.query.all()
        name={}        
        for i in ord:
            name[i.order_number]=Users.query.filter_by(id=i.order_userid).first().username
        return render_template('order_summary.html',tot=tot,name=name)

@app.route("/admin/order/<int:order_number>")
@login_required
def ordernumber(order_number):
    if current_user.role=='admin':
        prod=Product.query.all()
        ord=Order.query.filter_by(order_number=order_number).all()
        tot=Total.query.filter_by(total_ordernumber=order_number).first()
        name={}        
        for i in ord:
            name[i.order_number]=Users.query.filter_by(id=i.order_userid).first().username
        nam=name[order_number]
        return render_template('order_numbersummary.html',prod=prod,ord=ord,tot=tot,nam=nam)
            




#---------------------------------------------------------------------------------user-----------------------------------------------------------------#

@app.route("/user",methods=["GET","POST"])
def user():
    if request.method=='POST':
        all_values=request.form.to_dict()   
        username=all_values['username']
        password=all_values['password']
        user=Users.query.filter_by(username=username,role='user').first()
        if user==None:
            return render_template('Invalid_username.html')  
        else:
            if user.password==password:
                login_user(user)
                catall=Category.query.all()
                cat=[]
                for i in catall:
                    if Product.query.filter_by(product_category=i.category_id).all()!=[]:
                        cat.append(i)
                prod=Product.query.order_by(desc(Product.product_id)).all()
                cartn=len(Cart.query.filter_by(cart_user=user.id).all())
                return render_template('user_dashboard.html',cat=cat,prod=prod,user=user,dat=date.today(),cartn=cartn)
                
            else:
                return render_template('Invalid_username.html')    
    else:
        return render_template('user_login.html')

@app.route("/user/registration",methods=["GET","POST"])
def userregistration():
    if request.method=='POST':
        all_values=request.form.to_dict()
        use=Users(username=all_values['username'],password=all_values['password'],address=all_values['address'],address2=all_values['address2'],
                  city=all_values['city'],state=all_values['state'],zip=all_values['zip'],role='user')
        try:
            db.session.add(use)
            db.session.commit()
            return redirect('/user')
        except IntegrityError:
            return render_template('username_already.html',username=all_values['username'])
    if request.method=='GET':
        return render_template('user_registration.html')

@app.route("/user/cart/<int:sl_no>/<int:product_id>",methods=["GET","POST"])
@login_required
def usercartadd(sl_no,product_id):
    if request.method=='GET' and current_user.role=='user':
        user=Users.query.filter_by(id=sl_no).first()
        prod=Product.query.filter_by(product_id=product_id).first()
        cat=Category.query.filter_by(category_id=prod.product_category).first()
        if prod.product_quantity>0:
            return render_template('user_cartadd.html',prod=prod,cat=cat,user=user,dat=date.today())
        else:
            return render_template('product_nil.html',user=user,prod=prod,dat=date.today())
        
    if request.method=='POST' and current_user.role=='user':
        all_values=request.form.to_dict()
        user=Users.query.filter_by(id=sl_no).first()
        prod=Product.query.filter_by(product_id=product_id).first()
        carto=Cart.query.filter_by(cart_product=product_id,cart_user=sl_no).first()
        if carto==None:
            cart=Cart(cart_product=prod.product_id,cart_productqty=all_values['cart_qty'],cart_productprice=prod.product_rate,cart_user=user.id)
            db.session.add(cart)
        else:
            qty=carto.cart_productqty + int(all_values['cart_qty'])
            if qty <= prod.product_quantity:
                carto.cart_productqty=qty
            else:
                return render_template('user_carterror.html',qty=qty,prod=prod,user=user,dat=date.today())
        db.session.commit()
        catall=Category.query.all()
        cat=[]
        for i in catall:
            if Product.query.filter_by(product_category=i.category_id).all()!=[]:
                cat.append(i)
        prod=Product.query.order_by(desc(Product.product_id)).all()
        cartn=len(Cart.query.filter_by(cart_user=user.id).all())
        return render_template('user_dashboard.html',cat=cat,prod=prod,user=user,dat=date.today(),cartn=cartn)

@app.route("/user/cart/<int:id>",methods=["GET","POST"])
@login_required
def usercart(id):
    if request.method=='GET' and current_user.role=='user':
        user=Users.query.filter_by(id=id).first()
        car=Cart.query.filter_by(cart_user=id).all()
        prod=Product.query.all()
        total=0
        for i in car:
            total+=(i.cart_productqty*i.cart_productprice)
        
        return render_template("user_cart.html",car=car,user=user,prod=prod,total=total,dat=date.today())

@app.route("/user/cart/edit/<int:cart_id>/<int:id>",methods=["GET","POST"])
@login_required
def usercartedit(cart_id,id):
    if request.method=='GET' and current_user.role=='user':
        user=Users.query.filter_by(id=id).first()
        car=Cart.query.filter_by(cart_id=cart_id).first()
        prod=Product.query.filter_by(product_id=car.cart_product).first()
        cat=Category.query.filter_by(category_id=prod.product_category).first()
        cartn=len(Cart.query.filter_by(cart_user=user.id).all())
        if prod.product_quantity>0:
            return render_template('user_cartedit.html',car=car,user=user,prod=prod,cat=cat,dat=date.today(),cartn=cartn)
        else:
            pass
    if request.method=='POST' and current_user.role=='user':
        all_values=request.form.to_dict()
        care=Cart.query.filter_by(cart_id=cart_id).first()
        care.cart_productqty=all_values['cart_qty']
        db.session.commit()
        user=Users.query.filter_by(id=id).first()
        car=Cart.query.filter_by(cart_user=id).all()
        prod=Product.query.all()
        total=0
        for i in car:
            total+=(i.cart_productqty*i.cart_productprice)
        return render_template("user_cart.html",car=car,user=user,prod=prod,total=total,dat=date.today())

@app.route("/user/cart/delete/<int:cart_id>/<int:id>",methods=["GET","POST"])
@login_required
def usercartdelete(cart_id,id):
    if request.method=='GET' and current_user.role=='user':
        carde=Cart.query.filter_by(cart_id=cart_id).first()
        if carde!=None:
            db.session.delete(carde)
            db.session.commit()
        user=Users.query.filter_by(id=id).first()
        car=Cart.query.filter_by(cart_user=id).all()
        prod=Product.query.all()
        total=0
        for i in car:
            total+=(i.cart_productqty*i.cart_productprice)
        return render_template("user_cart.html",car=car,user=user,prod=prod,total=total,dat=date.today())

@app.route('/user/order/conf/<int:id>',methods=["GET","POST"])
@login_required
def userorderconf(id):
    if request.method=='GET' and current_user.role=='user':
        user=Users.query.filter_by(id=id).first()
        car=Cart.query.filter_by(cart_user=id).all()
        total=0
        carno=[]
        for k in car:
            prod=Product.query.filter_by(product_id=k.cart_product).first()
            if k.cart_productqty<=prod.product_quantity:
                total+=(k.cart_productqty*k.cart_productprice)
            else:
                carno.append(k)
                db.session.delete(k)
        if carno!=[]:
            db.session.commit()
        prod=Product.query.all()
        car=Cart.query.filter_by(cart_user=id).all()
        return render_template('user_orderconf.html',carno=carno,car=car,prod=prod,user=user,total=total,dat=date.today())
        


@app.route('/user/order/<int:id>',methods=["GET","POST"])
@login_required
def userorder(id):
    if request.method=='POST' and current_user.role=='user':
        user=Users.query.filter_by(id=id).first()
        cart=Cart.query.filter_by(cart_user=id).all()
        all_values=request.form.to_dict()
        carno=[]
        carav=[]
        if cart !=[]:
            total=0
            for k in cart:
                prod=Product.query.filter_by(product_id=k.cart_product).first()
                if k.cart_productqty<=prod.product_quantity:
                    total+=(k.cart_productqty*k.cart_productprice)
                    carav.append(k)
                else:
                    carno.append(k)
                    db.session.delete(k)
            if carno!=[]:
                db.session.commit()
            
            num=0
            ord=Order.query.order_by(desc(Order.order_number)).first()
            if ord==None:
                order_numb=1
            else:
                order_numb=ord.order_number + 1
            for i in carav:
                prod=Product.query.filter_by(product_id=i.cart_product).first()
                num=num+1
                new_order=Order(order_number=order_numb,order_itemprice=i.cart_productprice,order_qty=i.cart_productqty,order_userid=i.cart_user,order_productid=i.cart_product,order_itemnumber=num)
                db.session.add(new_order)
            db.session.commit()
            for i in cart:
                prou=Product.query.filter_by(product_id=i.cart_product).first()
                if i in carav:
                    prou.product_quantity=prou.product_quantity-i.cart_productqty
                db.session.delete(i)
            if carav!=[]:
                totu=Total(total_ordernumber=order_numb,total_orderamount=total,total_orderaddress=all_values['address'],total_orderaddress2=all_values['address2'],
                           total_ordercity=all_values['city'],total_orderzip=all_values['zip'],total_orderstate=all_values['state'],total_orderdate=date.today())
                db.session.add(totu)
            db.session.commit()    
            user=Users.query.filter_by(id=id).first()
            prod=Product.query.all()
            ordc=Order.query.filter_by(order_number=order_numb).all()
            tot=Total.query.filter_by(total_ordernumber=order_numb).first()
            delivery_date=date.today()+timedelta(days=3)
            if tot!=None:
                return render_template('user_orderthanks.html',ordc=ordc,user=user,prod=prod,tot=tot,carno=carno,dat=date.today(),delivery_date=delivery_date)
            else:
                return render_template('user_orderthanks.html',ordc=ordc,user=user,prod=prod,carno=carno,dat=date.today(),delivery_date=delivery_date)
        else:
            user=Users.query.filter_by(id=id).first()
            prod=Product.query.all()
            ordc=[]
            ordc.append(Order.query.filter_by(order_userid=id).order_by(desc(Order.order_number)).first())
            tot=Total.query.filter_by(total_ordernumber=ordc[0].order_number).first()
            return render_template('user_orderthanks.html',ordc=ordc,user=user,prod=prod,total=tot.total_orderamount,dat=date.today(),delivery_date=delivery_date)
    
    if request.method=='GET' and current_user.role=='user':
        return redirect(f'/user/home/{id}')

@app.route('/user/order/history/<int:id>',methods=["GET","POST"])
@login_required
def userorderhistory(id):
    ord=Order.query.filter_by(order_userid=id).all()
    prod=Product.query.all()
    tot=Total.query.all()
    user=Users.query.filter_by(id=id).first()
    ordn=[]
    ordl=[]
    
    for i in ord:
        if i.order_number not in ordn:
            ordn.append(i.order_number)
    for i in ordn:
        lis=[]
        for c in ord:
            if c.order_number==i:
                lis.append(c)
        ordl.append(lis)
    cartn=len(Cart.query.filter_by(cart_user=user.id).all())
    return render_template('user_booking.html',ordl=ordl,prod=prod,tot=tot,user=user,dat=date.today(),cartn=cartn)

@app.route("/user/home/<int:sl_no>",methods=["GET"])
@login_required
def userhome(sl_no):
    if current_user.role=='user':
        user=Users.query.filter_by(id=sl_no).first()
        catall=Category.query.all()
        cat=[]
        for i in catall:
            if Product.query.filter_by(product_category=i.category_id).all()!=[]:
                cat.append(i)
        prod=Product.query.order_by(desc(Product.product_id)).all()
        cartn=len(Cart.query.filter_by(cart_user=user.id).all())
        return render_template('user_dashboard.html',cat=cat,prod=prod,user=user,dat=date.today(),cartn=cartn)


#---------------------------------------------------------------------------------user_rating------------------------------------------------------------------#

@app.route('/user/rating/<int:id>/<int:total_ordernumber>',methods=["GET","POST"])
@login_required
def userrating(id,total_ordernumber):
    if request.method=='POST' and current_user.role=='user':
        all_values=request.form.to_dict()
        for i in all_values.keys():
            k=i
            break
        k=k.split('_')
        tot=Total.query.filter_by(total_ordernumber=total_ordernumber).first()
        tot.total_orderrating=int(k[-1])
        db.session.commit()

        return redirect(f'/user/order/history/{id}')

@app.route('/user/rate/edit/<int:id>/<int:total_ordernumber>',methods=["GET","POST"])
@login_required
def usereditrating(id,total_ordernumber):
    if request.method=='GET' and current_user.role=='user':
        tot=Total.query.filter_by(total_ordernumber=total_ordernumber).first()
        tot.total_orderrating=0
        db.session.commit()

        return redirect(f'/user/order/history/{id}')
    




#------------------------------------------------------------------------userprofile-------------------------------------------------------------------#
@app.route('/user/profile/<int:sl_no>',methods=["GET","POST"])
@login_required
def userprofile(sl_no):
    if request.method=='GET' and current_user.role=='user':
        user=Users.query.filter_by(id=sl_no).first()
        cartn=len(Cart.query.filter_by(cart_user=user.id).all())
        return render_template('user_profile.html',user=user,dat=date.today(),cartn=cartn)
    if request.method=='POST' and current_user.role=='user':
        all_values=request.form.to_dict()
        user=Users.query.filter_by(id=sl_no).first()
        cartn=len(Cart.query.filter_by(cart_user=user.id).all())
        for i in all_values:
            if i =='username':
                user.username=all_values[i]
            if i=='address':
                user.address=all_values[i]
            if i=='address2':
                user.address2=all_values[i]
            if i =='city':
                user.city=all_values[i]
            if i=='state':
                user.state=all_values[i]
            if i=='zip':
                user.zip=all_values[i]
            db.session.commit()
        return redirect(f'/user/profile/{sl_no}')
    
#----------------------------------------------------------------search-----------------------------------------------------------------------------------#

@app.route("/user/search/<int:sl_no>",methods=["GET","POST"])
@login_required
def usersearch(sl_no):
    if request.method=='POST' and current_user.role=='user':
        user=Users.query.filter_by(id=sl_no).first()
        all_values=request.form.to_dict()
        k='%'+all_values['search']+'%'
        prod = Product.query.filter(Product.product_name.ilike(k)).order_by(desc(Product.product_id)).all()
        catal=[]
        cat=[]
        v='product'
        if prod !=[]:
            for i in prod:
                v=Category.query.filter_by(category_id=i.product_category).first()
                if v.category_id not in catal:
                    catal.append(v.category_id)
            catal.sort()
            for i in catal:
                cat.append(Category.query.filter_by(category_id=i).first())
            cartn=len(Cart.query.filter_by(cart_user=user.id).all())
            return render_template('user_dashboard.html',cat=cat,prod=prod,user=user,dat=date.today(),cartn=cartn)
        else:
            return render_template('search_error.html',k=k.strip('%'),v=v,user=user,dat=date.today())
    if request.method=='GET' and current_user.role=='user':
        user=Users.query.filter_by(id=sl_no).first()
        catall=Category.query.all()
        cat=[]
        for i in catall:
            if Product.query.filter_by(product_category=i.category_id).all()!=[]:
                cat.append(i)
        prod=Product.query.order_by(desc(Product.product_id)).all()
        cartn=len(Cart.query.filter_by(cart_user=user.id).all())
        return render_template('user_dashboard.html',cat=cat,prod=prod,user=user,dat=date.today(),cartn=cartn)
    

@app.route("/user/advsearch/<int:sl_no>",methods=["GET","POST"])
@login_required
def useradvsearch(sl_no):
    if current_user.role=='user' and request.method=='POST':
        all_values=request.form.to_dict()
        user=Users.query.filter_by(id=sl_no).first()
        if all_values['criteria']=='product':
            k='%'+all_values['search']+'%'
            prod = Product.query.filter(Product.product_name.ilike(k)).order_by(desc(Product.product_id)).all()
            catal=[]
            cat=[]
            v='product'
            if prod !=[]:
                for i in prod:
                    v=Category.query.filter_by(category_id=i.product_category).first()
                    if v.category_id not in catal:
                        catal.append(v.category_id)
                catal.sort()
                for i in catal:
                    cat.append(Category.query.filter_by(category_id=i).first())
                cartn=len(Cart.query.filter_by(cart_user=user.id).all())
                return render_template('user_dashboard.html',cat=cat,prod=prod,user=user,dat=date.today(),cartn=cartn)
            else:
                return render_template('search_error.html',v=v,k=k.strip('%'),user=user,dat=date.today())
        

        if all_values['criteria']=='category':
            k='%'+all_values['search']+'%'
            catall=Category.query.filter(Category.category_name.ilike(k)).all()
            cat=[]
            v='category'
            for i in catall:
                if Product.query.filter_by(product_category=i.category_id).all()!=[]:
                    cat.append(i)
            prodall=Product.query.order_by(desc(Product.product_id)).all()
            prod=[]
            catno=[]
            if cat!=[]:
                for i in cat:
                    catno.append(i.category_id)
                for c in prodall:
                    if c.product_category in catno:
                        prod.append(c)
                cartn=len(Cart.query.filter_by(cart_user=user.id).all())
                return render_template('user_dashboard.html',cat=cat,prod=prod,user=user,dat=date.today(),cartn=cartn)
            else:
                return render_template('search_error.html',k=k.strip('%'),v=v,user=user,dat=date.today())


        if all_values['criteria']=='order':
            k=all_values['search']
            ord=Order.query.filter_by(order_number=k,order_userid=sl_no).all()
            v='order'
            if ord!=[]:
                prod=Product.query.all()
                tot=Total.query.all()
                user=Users.query.filter_by(id=sl_no).first()
                ordn=[]
                ordl=[]    
                for i in ord:
                    if i.order_number not in ordn:
                        ordn.append(i.order_number)

                for i in ordn:
                    lis=[]
                    for c in ord:
                        if c.order_number==i:
                            lis.append(c)
                    ordl.append(lis)
                return render_template('user_booking.html',ordl=ordl,prod=prod,tot=tot,user=user,dat=date.today())
            else:
                return render_template('search_error.html',k=k,v=v,user=user,dat=date.today())

        if all_values['criteria']=='price_less':
            k=int(all_values['search'])
            prod=Product.query.filter(Product.product_rate<=k).order_by(desc(Product.product_id)).all()
            catal=[]
            cat=[]
            v='price'
            if prod !=[]:
                for i in prod:
                    v=Category.query.filter_by(category_id=i.product_category).first()
                    if v.category_id not in catal:
                        catal.append(v.category_id)
                catal.sort()
                for i in catal:
                    cat.append(Category.query.filter_by(category_id=i).first())
                cartn=len(Cart.query.filter_by(cart_user=user.id).all())
                return render_template('user_dashboard.html',cat=cat,prod=prod,user=user,dat=date.today(),cartn=cartn)
            else:
                return render_template('search_error.html',v=v,k=k,user=user,dat=date.today())
    
        if all_values['criteria']=='price_more':
            k=int(all_values['search'])
            prod=Product.query.filter(Product.product_rate>=k).order_by(desc(Product.product_id)).all()
            catal=[]
            cat=[]
            v='price'
            if prod !=[]:
                for i in prod:
                    v=Category.query.filter_by(category_id=i.product_category).first()
                    if v.category_id not in catal:
                        catal.append(v.category_id)
                catal.sort()
                for i in catal:
                    cat.append(Category.query.filter_by(category_id=i).first())
                cartn=len(Cart.query.filter_by(cart_user=user.id).all())
                return render_template('user_dashboard.html',cat=cat,prod=prod,user=user,dat=date.today(),cartn=cartn)
            else:
                return render_template('search_error.html',v=v,k=k,user=user,dat=date.today())


        if all_values['criteria']=='expiry_date':
            c=all_values['search']
            t=c.split('-')
            k=''
            for i in range(3):
                if i!=2:
                    k='-'+t[i]+k
                else:
                    k=t[i]+k
            prod=Product.query.filter(Product.product_expirydate<=k).order_by(desc(Product.product_id)).all()
            catal=[]
            cat=[]
            v='expiry-date'
            if prod !=[]:
                for i in prod:
                    v=Category.query.filter_by(category_id=i.product_category).first()
                    if v.category_id not in catal:
                        catal.append(v.category_id)
                catal.sort()
                for i in catal:
                    cat.append(Category.query.filter_by(category_id=i).first())
                cartn=len(Cart.query.filter_by(cart_user=user.id).all())
                return render_template('user_dashboard.html',cat=cat,prod=prod,user=user,dat=date.today(),cartn=cartn)
            else:
                return render_template('search_error.html',v=v,k=k,user=user,dat=date.today()) 

        if all_values['criteria']=='CRITERIA FOR SEARCH':
            user=Users.query.filter_by(id=sl_no).first()
            return render_template('user_search.html',user=user,dat=date.today())


    if current_user.role=='user' and request.method=='GET':
        user=Users.query.filter_by(id=sl_no).first()
        return render_template('user_search.html',user=user,dat=date.today())
    
#---------------------------------------------------------------------------------login------------------------------------------------------------------#

@app.route("/")
def screen():
    return render_template('homepage.html')

@app.route("/logout")
@login_required
def user_logout():
    logout_user()
    return render_template('user_logout.html') 
#-------------------------------------------------------------------------------------api------------------------------------------------------------------#


categ=reqparse.RequestParser()
categ.add_argument("category_name",type=str)


class CategoryRc(Resource):
    def get(self,id):
        catq=Category.query.filter_by(category_id=id).first()
        if catq!=None:
            return{
                "category_id": catq.category_id,
                "category_name": catq.category_name
                }
        else:
            abort(404, message="category not found")

    def post(self):
        cat=categ.parse_args()
        if cat["category_name"]==None or cat["category_name"]=='':
            abort(409,message="Category Name is Required")
        already=Category.query.filter_by(category_name=cat["category_name"]).all()
        if len(already)==0:
            catadd=Category(category_name=cat["category_name"])
            db.session.add(catadd)
            db.session.commit()
            cc=Category.query.filter_by(category_name=cat["category_name"]).first()
            return{ 
                "category_id":cc.category_id,
                "category_name":cc.category_name
            },201
        else:
            abort(409,message="category name already present")
    

    def delete(self,id):
        catq=Category.query.filter_by(category_id=id).first()
        if catq==None:
            abort(404, message="category not found")
        else:
            try:
                db.session.delete(catq)
                db.session.commit()
                return "Category Successfully Deleted",200
            except IntegrityError:
                abort(
                    404, message="Products in the category already booked by user cannot be deleted")
 
    
    def put(self,id):
        catq=Category.query.filter_by(category_id=id).first()
        if catq==None:
            abort(404, message="category not found")
        else:
            cat=categ.parse_args()
            if cat["category_name"]==None:
                abort(409,message="Category Name is Required")
            already=Category.query.filter_by(category_name=cat["category_name"]).all()
            if len(already)==0:
                catq.category_name=cat["category_name"]
                db.session.commit()
                cc=Category.query.filter_by(category_id=id).first()
                return{
                    "category_id":cc.category_id,
                    "category_name":cc.category_name
                },201
            else:
                abort(409,message="category name already present")
api.add_resource(CategoryRc,"/api/category","/api/category/<int:id>")

prodeg=reqparse.RequestParser()
prodeg.add_argument("product_name",type=str)
prodeg.add_argument("product_quantity",type=int)
prodeg.add_argument("product_rate",type=int)
prodeg.add_argument("product_manufacture",type=str)
prodeg.add_argument("product_expirydate",type=str)
prodeg.add_argument("product_category",type=int)

class ProductRc(Resource):
    def get(self,id):
        prodq=Product.query.filter_by(product_id=id).first()
        if prodq!=None:
            return{
                "product_id": prodq.product_id,
                "product_name": prodq.product_name,
                "product_quantity": prodq.product_quantity,
                "product_rate": prodq.product_rate,
                "product_manufacture": prodq.product_manufacture,
                "product_expirydate": str(prodq.product_expirydate),
                "product_category":prodq.product_category
                }
        else:
            abort(404, message="product not found")

    def post(self):
        prod=prodeg.parse_args()
        if prod["product_name"]==None or prod["product_name"]=='':
            abort(409,message="Product Name is Required")
        if prod["product_quantity"]==None or prod["product_quantity"]=='':
            abort(409,message="Product Qty is Required")
        if prod["product_rate"]==None or prod["product_rate"]=='':
            abort(409,message="Product Rate is Required")
        if prod["product_manufacture"]==None or prod["product_manufacture"]=='':
            abort(409,message="Product Manufacture Name is Required")
        if prod["product_expirydate"]==None or prod["product_expirydate"]=='':
            abort(409,message="Product expiry date is Required")
        if prod["product_category"]==None or prod["product_category"]=='':
            abort(409,message="Product category id is Required")
        already=Product.query.filter_by(product_name=prod["product_name"]).all()
        if len(already)==0:
            [a,b,c]=prod["product_expirydate"].split('-')
            exp_date=date(int(c),int(b),int(a))
            prodadd=Product(product_name=prod["product_name"],product_quantity=prod["product_quantity"],product_rate=prod["product_rate"],
                            product_manufacture=prod["product_manufacture"],product_expirydate=exp_date,
                            product_category=prod["product_category"])
            db.session.add(prodadd)
            db.session.commit()
            cc=Product.query.filter_by(product_name=prod["product_name"]).first()
            return{ 
                "product_id":cc.product_id,
                "product_name":cc.product_name,
                "product_quantity":cc.product_quantity,
                "product_rate":cc.product_rate,
                "product_expirydate":str(cc.product_expirydate),
                "product_category":cc.product_category
            },201
        else:
            abort(409,message="Product name already present")
    

    def delete(self,id):
        prodq=Product.query.filter_by(product_id=id).first()
        if prodq==None:
            abort(404, message="product not found")
        else:
            try:
                db.session.delete(prodq)
                db.session.commit()
                return "Product Successfully Deleted",200
            except IntegrityError:
                abort(
                    404, message="Products in the category already booked by user cannot be deleted")
 
    
    def put(self,id):
        prodq=Product.query.filter_by(product_id=id).first()
        if prodq==None:
            abort(404, message="product not found")
        else:
            prod=prodeg.parse_args()
            if prod["product_name"]==None or prod["product_name"]=='':
                abort(409,message="Product Name is Required")
            if prod["product_quantity"]==None or prod["product_quantity"]=='':
                abort(409,message="Product Qty is Required")
            if prod["product_rate"]==None or prod["product_rate"]=='':
                abort(409,message="Product Rate is Required")
            if prod["product_manufacture"]==None or prod["product_manufacture"]=='':
                abort(409,message="Product Manufacture Name is Required")
            if prod["product_expirydate"]==None or prod["product_expirydate"]=='':
                abort(409,message="Product expiry date is Required")
            if prod["product_category"]==None or prod["product_category"]=='':
                abort(409,message="Product category id is Required")
            already=Product.query.filter_by(product_name=prod["product_name"]).all()
            if len(already)==0:
                prodq.product_name=prod["product_name"]
                prodq.product_quantity=prod["product_quantity"]
                prodq.product_rate=prod["product_rate"]
                prodq.product_manufacture=prod["product_manufacture"]
                [a,b,c]=prod["product_expirydate"].split('-')
                exp_date=date(int(c),int(b),int(a))
                prodq.product_expirydate=exp_date
                prodq.product_category=prod["product_category"]
                try:
                    db.session.commit()
                    cc=Product.query.filter_by(product_name=prod["product_name"]).first()
                    return{ 
                        "product_id":cc.product_id,
                        "product_name":cc.product_name,
                        "product_quantity":cc.product_quantity,
                        "product_rate":cc.product_rate,
                        "product_expirydate":str(cc.product_expirydate),
                        "product_category":cc.product_category
                        },201
                except IntegrityError:
                    abort(409,message="product name already present")                            
            else:
                abort(409,message="product name already present")
api.add_resource(ProductRc,"/api/product","/api/product/<int:id>")

class CatagprodRC(Resource):

    def get(self,id):
        prodq=Product.query.filter_by(product_category=id).all()
        Lis=[]
        if prodq !=[]:
            for i in prodq:
              Lis.append({ 
                "product_id":i.product_id,
                "product_name":i.product_name,
                "product_quantity":i.product_quantity,
                "product_rate":i.product_rate,
                "product_expirydate":str(i.product_expirydate),
                "product_category":i.product_category
                        })  
            return Lis,201
        else:
            abort (404, message="No products are listed for the mentioned category")
api.add_resource(CatagprodRC,"/api/category/product","/api/category/product/<int:id>")

#-------------------------------------------------------------------------------run------------------------------------------------------------------#
if __name__=="__main__":
    app.run(host='0.0.0.0',debug=True)
