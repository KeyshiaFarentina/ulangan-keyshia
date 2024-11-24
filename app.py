from flask import Flask, render_template, request, redirect, session, flash, url_for
import mysql.connector

app = Flask(__name__)
app.secret_key = "supersecretkey"

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="data_pempek"
    )

# Tambahkan route lainnya seperti login, dashboard, add_pempek, edit_pempek, dan delete_pempek


@app.route('/')
def home():
    if 'user' in session:
        return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['user'] = user['username']
            return redirect('/dashboard')
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM pempek")
    pempek_list = cursor.fetchall()
    conn.close()
    return render_template('dashboard.html', pempek_list=pempek_list)

@app.route('/add_pempek', methods=['GET', 'POST'])
def add_pempek():
    if 'user' not in session:
        return redirect('/login')

    if request.method == 'POST':
        nama = request.form['nama']
        harga = request.form['harga']
        deskripsi = request.form['deskripsi']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO pempek (nama, harga, deskripsi) VALUES (%s, %s, %s)",
            (nama, harga, deskripsi)
        )
        conn.commit()
        conn.close()
        flash('Data pempek berhasil ditambahkan!', 'success')
        return redirect('/dashboard')

    return render_template('add_pempek.html')

@app.route('/edit_pempek/<int:id>', methods=['GET', 'POST'])
def edit_pempek(id):
    if 'user' not in session:
        return redirect('/login')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Ambil data pempek berdasarkan ID
    cursor.execute("SELECT * FROM pempek WHERE id=%s", (id,))
    pempek = cursor.fetchone()

    if not pempek:
        flash("Pempek tidak ditemukan.", "danger")
        conn.close()
        return redirect('/dashboard')

    if request.method == 'POST':
        # Ambil data dari form
        nama = request.form['nama']
        harga = request.form['harga']
        deskripsi = request.form['deskripsi']

        # Perbarui data di database
        cursor.execute(
            "UPDATE pempek SET nama=%s, harga=%s, deskripsi=%s WHERE id=%s",
            (nama, harga, deskripsi, id)
        )
        conn.commit()
        conn.close()

        flash("Data pempek berhasil diperbarui!", "success")
        return redirect('/dashboard')

    conn.close()
    # Tampilkan halaman edit dengan data pempek
    return render_template(
        'add_pempek.html',  # Menggunakan template yang sama dengan tambah
        title="Edit Pempek",
        action_url=url_for('edit_pempek', id=id),
        pempek=pempek
    )



@app.route('/delete_pempek/<int:id>', methods=['GET'])
def delete_pempek(id):
    if 'user' not in session:
        return redirect('/login')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM pempek WHERE id=%s", (id,))
    conn.commit()
    conn.close()
    flash('Data pempek berhasil dihapus!', 'success')
    return redirect('/dashboard')

if __name__ == '__main__':
    app.run(debug=True)
