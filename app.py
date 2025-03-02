from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(150), unique=True, nullable=False)
    author = db.Column(db.String(100), nullable=False)
    year_published = db.Column(db.Integer, nullable=False)
    available = db.Column(db.Boolean, default=True)

class Reader(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

class BorrowedBook(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    reader_id = db.Column(db.Integer, db.ForeignKey('reader.id'), nullable=False)
    borrowed_at = db.Column(db.DateTime, default=datetime.utcnow)
    return_due_date = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(days=14))

    book = db.relationship('Book', backref=db.backref('borrowed_books', lazy=True))
    reader = db.relationship('Reader', backref=db.backref('borrowed_books', lazy=True))



with app.app_context():
    db.create_all()



@app.route('/')
def index():
    books = Book.query.all()
    return render_template('index.html', books=books)



@app.route('/view_borrowed_books')
def view_borrowed_books():
    borrowed_books = BorrowedBook.query.all()
    return render_template('viewbooks.html', borrowed_books=borrowed_books)



@app.route('/borrow_book', methods=['GET', 'POST'])
def borrow_book():
    if request.method == 'POST':
        book_id = request.form['book_id']
        reader_id = request.form['reader_id']
        book = Book.query.get(book_id)
        reader = Reader.query.get(reader_id)
        if book and reader and book.available:
            borrowed_book = BorrowedBook(book_id=book_id, reader_id=reader_id)
            book.available = False
            db.session.add(borrowed_book)
            db.session.commit()
            return redirect(url_for('view_borrowed_books'))
    books = Book.query.filter_by(available=True).all()
    readers = Reader.query.all()
    return render_template('borrowbook.html', books=books, readers=readers)



@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        year_published = request.form['year_published']
        new_book = Book(title=title, author=author, year_published=year_published)
        db.session.add(new_book)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('addbook.html')



if __name__ == "__main__":
    app.run(debug=True)