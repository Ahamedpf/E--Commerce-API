from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///crud.db'  
db = SQLAlchemy(app)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(255))

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'image_url': self.image_url
        }

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    def serialize(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'quantity': self.quantity
        }

@app.route('/products', methods=['GET'])
def get_all_products():
    products = Product.query.all()
    return jsonify([p.serialize() for p in products])

@app.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get(product_id)
    if product is None:
        return jsonify({'message': 'Product not found'}), 404
    return jsonify(product.serialize())

@app.route('/cart', methods=['POST', 'GET'])
def cart_actions():
    if request.method == 'POST':
        data = request.get_json()
        if not data or not data.get('product_id') or not data.get('quantity'):
            return jsonify({'message': 'Missing required fields'}), 400

        product_id = data['product_id']
        quantity = data['quantity']
        existing_item = CartItem.query.filter_by(product_id=product_id).first()

        if existing_item:
            existing_item.quantity += quantity
            db.session.commit()
            return jsonify({'message': 'Product quantity updated'}), 200

        new_item = CartItem(product_id=product_id, quantity=quantity)
        db.session.add(new_item)
        db.session.commit()
        return jsonify({'message': 'Product added to cart'}), 201

    cart_items = CartItem.query.all()
    return jsonify([item.serialize() for item in cart_items])

@app.route('/cart/<int:cart_item_id>', methods=['DELETE'])
def remove_from_cart(cart_item_id):
    cart_item = CartItem.query.get(cart_item_id)
    if cart_item is None:
        return jsonify({'message': 'Cart item not found'}), 404

    db.session.delete(cart_item)
    db.session.commit()
    return jsonify({'message': 'Product removed from cart'}), 200

if __name__ == '__main__':
    db.create_all()  
    app.run(debug=True)



