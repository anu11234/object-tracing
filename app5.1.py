import os
import sqlite3
import qrcode
from flask import Flask, request, redirect, send_file, abort

app = Flask(__name__)

# Database setup
def init_db():
    conn = sqlite3.connect("items.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            description TEXT,
            price REAL
        )
    ''')
    conn.close()

# Generate QR code for an item
def generate_qr_code(item_id):
    # Replace with your deployed app URL once hosted
    public_url = "https://your-app-name.onrender.com"  # <-- Replace this with your deployment URL
    qr_url = f"{public_url}/item/{item_id}"
    qr = qrcode.make(qr_url)

    # Ensure the directory for QR codes exists
    output_dir = os.path.join("static", "qr_codes")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    qr_path = os.path.join(output_dir, f"item_{item_id}.png")
    qr.save(qr_path)
    print(f"QR Code generated at: {qr_path}")  # Debug print
    return qr_path

# Home page - Admin Panel
@app.route("/")
def admin_panel():
    conn = sqlite3.connect("items.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items")
    items = cursor.fetchall()
    conn.close()

    # HTML content for the admin panel
    html = """
    <!doctype html>
    <html>
    <head>
        <title>Admin Panel</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }
            table, th, td { border: 1px solid black; }
            th, td { padding: 10px; text-align: left; }
            .button { padding: 5px 10px; text-decoration: none; color: white; border-radius: 3px; }
            .edit { background-color: orange; }
            .delete { background-color: red; }
            .qr { background-color: green; }
            .add { background-color: blue; margin-bottom: 20px; display: inline-block; }
        </style>
    </head>
    <body>
        <h1>Admin Panel</h1>
        <a href="/add" class="button add">Add New Item</a>
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Description</th>
                    <th>Price</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
    """

    for item in items:
        html += f"""
        <tr>
            <td>{item[0]}</td>
            <td>{item[1]}</td>
            <td>{item[2]}</td>
            <td>₹{item[3]:,.2f}</td>
            <td>
                <a href="/edit/{item[0]}" class="button edit">Edit</a>
                <a href="/qr/{item[0]}" class="button qr">Download QR</a>
                <a href="/delete/{item[0]}" class="button delete" onclick="return confirm('Are you sure you want to delete this item?');">Delete</a>
            </td>
        </tr>
        """

    html += """
            </tbody>
        </table>
    </body>
    </html>
    """
    return html


# Download QR code
@app.route("/qr/<int:item_id>")
def download_qr(item_id):
    qr_path = os.path.join("static", "qr_codes", f"item_{item_id}.png")
    if os.path.exists(qr_path):
        return send_file(qr_path, as_attachment=True)
    else:
        print(f"QR Code not found at: {qr_path}")  # Debug print
        return "QR Code not found", 404


# View item details publicly
@app.route("/item/<int:item_id>")
def view_item(item_id):
    conn = sqlite3.connect("items.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items WHERE id=?", (item_id,))
    item = cursor.fetchone()
    conn.close()

    if item:
        html = f"""
        <!doctype html>
        <html>
        <head>
            <title>{item[1]}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
            </style>
        </head>
        <body>
            <h1>{item[1]}</h1>
            <p>{item[2]}</p>
            <p>Price: ₹{item[3]:,.2f}</p>
        </body>
        </html>
        """
        return html
    else:
        return "Item not found", 404


# Delete item
@app.route("/delete/<int:item_id>")
def delete_item(item_id):
    conn = sqlite3.connect("items.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM items WHERE id=?", (item_id,))
    conn.commit()
    conn.close()

    qr_path = os.path.join("static", "qr_codes", f"item_{item_id}.png")
    if os.path.exists(qr_path):
        os.remove(qr_path)

    return redirect("/")


# Initialize database and run app
if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="0.0.0.0")
