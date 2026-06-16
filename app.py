from flask import Flask, render_template, request, redirect, url_for
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

def get_db_connection():
    conn = psycopg2.connect(
        dbname="library_db",     
        user="postgres",         
        password="Aitu2025@", 
        host="localhost",
        port="5432"
    )
    return conn

@app.route('/')
def index():
    search_query = request.args.get('search', '')
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    if search_query:
        cur.execute("SELECT * FROM books WHERE title ILIKE %s OR author ILIKE %s ORDER BY book_id DESC", 
                    (f'%{search_query}%', f'%{search_query}%'))
    else:
        cur.execute("SELECT * FROM books ORDER BY book_id DESC")
        
    books = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('index.html', books=books, search_query=search_query)

@app.route('/add', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        genre = request.form['genre']
        published_year = request.form['published_year']
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO books (title, author, genre, published_year) VALUES (%s, %s, %s, %s)",
                    (title, author, genre, published_year))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('index'))
        
    return render_template('add.html')

@app.route('/edit/<int:book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        genre = request.form['genre']
        published_year = request.form['published_year']
        is_available = 'is_available' in request.form
        
        cur.execute("""
            UPDATE books 
            SET title = %s, author = %s, genre = %s, published_year = %s, is_available = %s 
            WHERE book_id = %s
        """, (title, author, genre, published_year, is_available, book_id))
        
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('index'))
        
    cur.execute("SELECT * FROM books WHERE book_id = %s", (book_id,))
    book = cur.fetchone()
    cur.close()
    conn.close()
    return render_template('edit.html', book=book)

@app.route('/delete/<int:book_id>', methods=['POST'])
def delete_book(book_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM books WHERE book_id = %s", (book_id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)