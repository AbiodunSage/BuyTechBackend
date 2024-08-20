import pyrebase
from flask import Flask, abort, jsonify, render_template, request
from flask_cors import CORS

Config = {
    "apiKey": "AIzaSyBy6ESU3Ash8nzRnM1jQobRuEdbZ8qp8Og",
    "authDomain": "ecommerce-e6182.firebaseapp.com",
    "databaseURL": "https://ecommerce-e6182-default-rtdb.firebaseio.com",
    "projectId": "ecommerce-e6182",
    "storageBucket": "ecommerce-e6182.appspot.com",
    "messagingSenderId": "694607965954",
    "appId": "1:694607965954:web:9f29f327203a39a6855c1b",
  }

firebase = pyrebase.initialize_app(Config)
auth = firebase.auth()
storage = firebase.storage()
db = firebase.database()

app = Flask(__name__)
CORS(app)

@app.route("/products", methods=['GET'])
def get_products():
    try:
        all_user = db.child("products").get()
        products = all_user.val()
        return jsonify(products)
    except Exception as e:
        return jsonify({"error": str(e)})


@app.route("/signup", methods=['POST'] )
def signup():
    ref = firebase.database().child("Users")
    data = request.get_json()
    
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    user_data = {
        "name": name,
        "email":email,
        "cart":{}        
    }

    if not name or not email or not password:
        return jsonify({"error":"Name,Email and Password are required"}),400

    try:
        user = auth.create_user_with_email_and_password(email,password)

        user_id = user['localId']
        ref.child(user_id).set(user_data)
        return jsonify({"message":"Succesfully created user"}),201

        
        
    except Exception as e:
        print(f"Error creating user: {str(e)}")
        return jsonify({"error": "Falied to create user"}),500   
    
@app.route("/login",methods=['POST'])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error":"Email and Password are required"}),400

    try:
        login = auth.sign_in_with_email_and_password(email,password)
        
        return jsonify({"message":"logged in succesfully"}),201
    except:
        return jsonify({"message":"Invalid email or password"})

@app.route("/Addproducts", methods=['POST'])
def addProducts():
    try:
        ref = firebase.database().child("products")
        data = request.get_json()

        product_name = data.get("name")
        product_price = data.get("price")
        product_code = data.get("product_code")

        product_data = {
            "name": data.get("name"),
            "price":data.get("price"),
            "product_code":data.get("product_code")
        }
        key = ref.child(product_code).set(product_data)
        return jsonify({"message":"Product added succesfully", "key":product_code})
    except Exception as e:
        print(f"Error adding product: {str(e)}")
        return jsonify({"error":"Failed to add product"})
    
@app.route("/ProductPage/<product_key>", methods=['POST'])
def Product(product_key):
    try:
        product_ref = db.child('products').child(product_key).get()
        product_data = product_ref.val()

        if product_data:
            """ print(f"User Data: {user_doc.to_dict()}") """
            return jsonify({"product":product_data})
        else:
            print({"Error":"No such user!"})
            return None
            
    except Exception as e:
        return jsonify({"Error":"Error occurred"})
    



@app.route("/cart/add", methods=['POST'])
def AddtoCart():
    data = request.get_json()

    user_id = data.get('user_id')
    product_key = data.get('product_key')


    if not user_id or not product_key :
        return jsonify({"Error":"User ID is required"})

    try:
        product_ref = db.child('products').child(product_key).get()
        product_data = product_ref.val()

        if product_data:
            cart_ref = db.child('users').child(user_id).child('cart').child(product_key)
            cart_ref.set(product_data)
            return jsonify({"message":"product added succesfully to cart","product":product_data})
        else:
            print({"Error":"No such product"})
            
            
    except Exception as e:
        return jsonify({"Error":"Error occurred","details": str(e)})

@app.route("/cart/delete", methods = ['DELETE'])
def delete_from_cart():
    data = request.get_json()

    user_id = data.get('user_id')
    product_key = data.get('product_key')

    if not user_id or not product_key:
        return jsonify({"error":"User Id and Product key are required"})
    try:
        cart_ref = db.child("user").child(user_id).child('cart').child(product_key)
        
        if cart_ref.get().val():
            cart_ref.remove()
            return jsonify({"message":"Product removed succesfully from cart"})
        else:
            return jsonify ({"error":"product not found in cart"})
    except Exception as e:
        return jsonify({"error":"An Error occurred","detaiils":str(e)})
    
@app.route("/cart/view", methods = ['GET'])
def view_cart():
    data = request.get_json()
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({"error":"User ID is required"})
    try:
        cart_ref = db.child('users').child(user_id).child('cart')

        cart_items = cart_ref.get().val()
        if cart_items:
            return jsonify({"cart":cart_items})
        else:
            return jsonify({"message":"Cart is empty"})
    except Exception as e:
        return jsonify({"error":"An error occured","details": str(e)})
    
 

if __name__ == "__main__":
    app.run(debug=True)
