import urllib.request
import json
class CurrencyConverterAPI:
    def __init__(self):
        self.api_url = "https://open.er-api.com/v6/latest/INR"
    def get_exchange_rate(self, target_currency):
        target_currency = target_currency.upper()
        if target_currency == "INR":
            return 1.0
        try:
            with urllib.request.urlopen(self.api_url, timeout=4) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode())
                    rates = data.get("rates", {})
                    if target_currency in rates:
                        return rates[target_currency]
                    else:
                        print(f"\n[API] Currency '{target_currency}' not found. Defaulting to INR.")
                        return 1.0
        except Exception as e:
            print(f"\n[API Warning] Could not fetch live rates ({e}). Falling back to offline base rate.")
            return 1.0
class Product:
    def __init__(self, product_id, name, price_inr, stock):
        self.product_id = product_id
        self.name = name
        self.price_inr = price_inr  
        self.stock = stock
    def display_details(self):
        print(f"[{self.product_id}] {self.name:<25} | Price: ₹{self.price_inr:<7.2f} | Stock: {self.stock}")
    def reduce_stock(self, quantity):
        if self.stock >= quantity:
            self.stock -= quantity
            return True
        return False


class User:
    def __init__(self, user_id, username, email, is_premium=False):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.is_premium = is_premium
class Cart:
    def __init__(self):
        self.items = {}  
    def add_item(self, product: Product, quantity):
        if quantity <= 0:
            print("Quantity must be greater than 0.")
            return
        current_cart_qty = self.items.get(product, 0)
        total_requested = current_cart_qty + quantity
        if product.stock >= total_requested:
            self.items[product] = total_requested
            print(f"✓ Added {quantity}x '{product.name}' to your cart.")
        else:
            print(f"❌ Cannot add. Only {product.stock} units available in inventory.")
    def view_cart(self):
        if not self.items:
            print("\nYour cart is empty!")
            return False
        print("\n--- Current Shopping Cart ---")
        for product, qty in self.items.items():
            subtotal = product.price_inr * qty
            print(f"- {product.name:<20} x{qty:<3} | Subtotal: ₹{subtotal:.2f}")
        print(f"Total Base Amount: ₹{self.calculate_total():.2f} INR")
        return True
    def calculate_total(self):
        return sum(product.price_inr * qty for product, qty in self.items.items())
    def clear(self):
        self.items.clear()
class Order:
    def __init__(self, order_id, user: User, cart: Cart, currency_choice="INR"):
        self.order_id = order_id
        self.user = user
        self.items_snapshot = dict(cart.items)
        self.base_total = cart.calculate_total()
        self.currency = currency_choice.upper()
        self.discount = self.base_total * 0.10 if self.user.is_premium else 0.0
        self.discounted_base = self.base_total - self.discount
        api = CurrencyConverterAPI()
        self.exchange_rate = api.get_exchange_rate(self.currency)
        self.final_amount = self.discounted_base * self.exchange_rate
        for product, qty in self.items_snapshot.items():
            product.reduce_stock(qty)
    def print_invoice(self):
        print("\n" + "="*45)
        print(f"         E-COMMERCE ORDER INVOICE        ")
        print("="*45)
        print(f"Order ID:    #{self.order_id:<15} Customer: {self.user.username}")
        print(f"Email:       {self.user.email:<15} Premium:  {self.user.is_premium}")
        print(f"Currency:    {self.currency:<15} Live Rate (1 INR): {self.exchange_rate:.4f}")
        print("-"*45)
        for product, qty in self.items_snapshot.items():
            local_item_price = product.price_inr * self.exchange_rate
            local_subtotal = local_item_price * qty
            print(f" {product.name:<20} x{qty:<2} | {self.currency} {local_subtotal:.2f}")
        print("-"*45)
        if self.user.is_premium:
            local_discount = self.discount * self.exchange_rate
            print(f"Premium Discount (10%):  -{self.currency} {local_discount:.2f}")
        print(f"FINAL PAID AMOUNT:        {self.currency} {self.final_amount:.2f}")
        print("="*45)
        print("   Thank you for shopping with us online!   \n")
def main():
    inventory = {
        "P101": Product("P101", "MacBook Pro M3", 169900.00, 5),
        "P102": Product("P102", "iPhone 15 Pro", 129900.00, 10),
        "P103": Product("P103", "Sony WH-1000XM5", 29999.00, 15),
        "P104": Product("P104", "Mechanical Keyboard", 6500.00, 30)
    }
    print("========================================")
    print("Welcome to the Indian E-Commerce Portal Setup")
    print("========================================")
    name = input("Enter your username: ").strip()
    email = input("Enter your email address: ").strip()
    premium_input = input("Are you a premium member? (yes/no): ").strip().lower()
    is_prem = premium_input in ['yes', 'y']
    customer = User(user_id="U882", username=name, email=email, is_premium=is_prem)
    customer_cart = Cart()
    order_counter = 5001
    while True:
        print("\n----- MAIN MENU -----")
        print("1. View Store Catalog")
        print("2. Add Item to Cart")
        print("3. View Shopping Cart")
        print("4. Proceed to Checkout")
        print("5. Exit Application")
        choice = input("Select an option (1-5): ").strip()
        if choice == "1":
            print("\n--- AVAILABLE PRODUCTS ---")
            for prod in inventory.values():
                prod.display_details()
        elif choice == "2":
            p_id = input("Enter Product ID to add: ").strip().upper()
            if p_id in inventory:
                try:
                    qty = int(input(f"How many units of {inventory[p_id].name}? "))
                    customer_cart.add_item(inventory[p_id], qty)
                except ValueError:
                    print("❌ Error: Please enter a valid integer for quantity.")
            else:
                print("❌ Invalid Product ID.")
        elif choice == "3":
            customer_cart.view_cart()
        elif choice == "4":
            if not customer_cart.items:
                print("❌ Your cart is empty. Cannot checkout.")
                continue
            customer_cart.view_cart()
            confirm = input("\nDo you want to finalize payment? (yes/no): ").strip().lower()
            if confirm in ['yes', 'y']:
                print("\nSupported Currencies: INR, USD, EUR, GBP, CAD")
                curr = input("Select processing currency (Default INR): ").strip().upper()
                if not curr:
                    curr = "INR"
                final_order = Order(
                    order_id=order_counter, 
                    user=customer, 
                    cart=customer_cart, 
                    currency_choice=curr
                )
                final_order.print_invoice()
                
                customer_cart.clear()
                order_counter += 1
            else:
                print("Transaction Cancelled.")

        elif choice == "5":
            print("\nThank you for using our system. Goodbye!")
            break
        else:
            print("❌ Invalid option. Try again.")

if __name__ == "__main__":
    main()
