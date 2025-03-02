from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from sqlalchemy.exc import IntegrityError

Base = declarative_base()


class Book(Base):
    __tablename__ = 'books'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, unique=True, nullable=False)
    author = Column(String, nullable=False)
    year_published = Column(Integer, nullable=False)
    available = Column(Boolean, default=True)


class Reader(Base):
    __tablename__ = 'readers'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)


class BorrowedBook(Base):
    __tablename__ = 'borrowed_books'
    id = Column(Integer, primary_key=True, autoincrement=True)
    book_id = Column(Integer, ForeignKey('books.id'), nullable=False)
    reader_id = Column(Integer, ForeignKey('readers.id'), nullable=False)
    borrowed_at = Column(DateTime, default=datetime.utcnow)
    return_due_date = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(days=14))

    book = relationship("Book", backref="borrowed_books")
    reader = relationship("Reader", backref="borrowed_books")


engine = create_engine("sqlite:///library.db")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()


def add_book(title, author, year):
    book = Book(title=title, author=author, year_published=year)
    session.add(book)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        print("Knyga su tokiu pavadinimu jau egzistuoja.")


def add_reader(name, email):
    reader = Reader(name=name, email=email)
    session.add(reader)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        print("Skaitytojas su tokiu elektroniniu paštu jau egzistuoja.")


def borrow_book(book_id, reader_id):
    book = session.query(Book).filter_by(id=book_id, available=True).first()
    if book:
        book.available = False
        borrowed = BorrowedBook(book_id=book_id, reader_id=reader_id)
        session.add(borrowed)
        session.commit()
        print(f"Knyga '{book.title}' paskolinta skaitytojui.")
    else:
        print("Knyga nepasiekiama.")


def update_book(book_id, new_title=None, new_author=None):
    book = session.query(Book).filter_by(id=book_id).first()
    if book:
        if new_title:
            book.title = new_title
        if new_author:
            book.author = new_author
        session.commit()
        print(f"Knygos '{book.id}' informacija atnaujinta.")
    else:
        print("Knyga nerasta.")


def delete_book(book_id):
    book = session.query(Book).filter_by(id=book_id).first()
    if book:
        borrowed_books = session.query(BorrowedBook).filter_by(book_id=book_id).all()
        for borrowed in borrowed_books:
            session.delete(borrowed)
        session.delete(book)
        session.commit()
        print(f"Knyga '{book.title}' pašalinta.")
    else:
        print("Knyga nerasta.")


def delete_reader(reader_id):
    reader = session.query(Reader).filter_by(id=reader_id).first()
    if reader:
        borrowed_books = session.query(BorrowedBook).filter_by(reader_id=reader_id).all()
        for borrowed in borrowed_books:
            session.delete(borrowed)
        session.delete(reader)
        session.commit()
        print(f"Skaitytojas '{reader.name}' pašalintas.")
    else:
        print("Skaitytojas nerastas.")


def list_books():
    books = session.query(Book).all()
    if not books:
        print("Nėra knygų bibliotekoje.")
    for book in books:
        print(f'{book.id}. {book.title} - {"Laisva" if book.available else "Paskolinta"}')


def list_borrowed_books():
    borrowed_books = session.query(BorrowedBook).all()
    for record in borrowed_books:
        print(
            f'Knyga ID {record.book_id} paskolinta skaitytojui ID {record.reader_id}, grąžinimo data: {record.return_due_date}')


def book_loan_duration(book_id):
    borrowed = session.query(BorrowedBook).filter_by(book_id=book_id).first()
    if borrowed:
        duration = datetime.utcnow() - borrowed.borrowed_at
        print(f"Knyga paskolinta {duration.days} dienas.")
    else:
        print("Knyga nebuvo paskolinta.")


def reader_borrow_history(reader_id):
    borrowed_books = session.query(BorrowedBook).filter_by(reader_id=reader_id).all()
    if borrowed_books:
        for record in borrowed_books:
            print(
                f'Knyga ID {record.book_id} paskolinta {record.borrowed_at}, grąžinimo data: {record.return_due_date}')
    else:
        print("Šis skaitytojas neturi paskolintų knygų.")


books = [
    ("Altorių šešėly", "Vincas Mykolaitis-Putinas", 1933),
    ("Balta drobulė", "Antanas Škėma", 1958),
    ("Dievų miškas", "Balys Sruoga", 1957),
    ("Sodybų tuštėjimo metas", "Juozas Aputis", 1970),
    ("Žemės duona", "Jonas Avyžius", 1951),
    ("Mėnulio vaikai", "Vytautė Žilinskaitė", 1988),
    ("Dienoraštis be datų", "Julius Sasnauskas", 2003),
    ("Duobė", "Herbjørg Wassmo", 2002),
    ("Baltaragio malūnas", "Kazys Boruta", 1945),
    ("Kryžkelė", "Alfonsas Bieliauskas", 1980),
    ("Šventųjų gyvūnų miestas", "Rūta Šepetys", 2017),
    ("Raudonasis trejetas", "Ričardas Gavelis", 2002),
    ("Įgimta meilė", "Ieva Simonaitytė", 1980),
    ("Nepriklausomybės akto signatarai", "Vaidotas Beniušis", 2019),
    ("Užburtas miestas", "Jūratė Svetikaitė", 2015),
    ("Po šiaurės vėju", "Vaidotas Verikas", 2007),
    ("Meilės ir karščio dienos", "Kristina Sabaliauskaitė", 2009),
    ("Lūžis", "Lina Ever", 2010),
    ("Atvirkščiai", "Kestutis Kasparavičius", 2013)
]

for title, author, year in books:
    add_book(title, author, year)


def main():
    while True:
        print("\nPasirinkite veiksmą:")
        print("1. Pridėti knygą")
        print("2. Pridėti skaitytoją")
        print("3. Paskolinti knygą")
        print("4. Atnaujinti knygos informaciją")
        print("5. Pašalinti knygą")
        print("6. Pašalinti skaitytoją")
        print("7. Rodyti visų knygų sąrašą")
        print("8. Rodyti visų paskolintų knygų sąrašą")
        print("9. Rodyti knygos paskolinimo trukmę")
        print("10. Rodyti skaitytojo paskolintų knygų istoriją")
        print("11. Išeiti")

        choice = input("Pasirinkimas: ")

        if choice == '1':
            title = input("Knygos pavadinimas: ")
            author = input("Autorius: ")
            year = int(input("Metai: "))
            add_book(title, author, year)
        elif choice == '2':
            name = input("Skaitytojo vardas: ")
            email = input("Skaitytojo el. paštas: ")
            add_reader(name, email)
        elif choice == '3':
            book_id = int(input("Knygos ID: "))
            reader_id = int(input("Skaitytojo ID: "))
            borrow_book(book_id, reader_id)
        elif choice == '4':
            book_id = int(input("Knygos ID: "))
            new_title = input("Naujas pavadinimas (palikite tuščią, jei nesikeičia): ")
            new_author = input("Naujas autorius (palikite tuščią, jei nesikeičia): ")
            update_book(book_id, new_title or None, new_author or None)
        elif choice == '5':
            book_id = int(input("Knygos ID: "))
            delete_book(book_id)
        elif choice == '6':
            reader_id = int(input("Skaitytojo ID: "))
            delete_reader(reader_id)
        elif choice == '7':
            list_books()
        elif choice == '8':
            list_borrowed_books()
        elif choice == '9':
            book_id = int(input("Knygos ID: "))
            book_loan_duration(book_id)
        elif choice == '10':
            reader_id = int(input("Skaitytojo ID: "))
            reader_borrow_history(reader_id)
        elif choice == '11':
            break
        else:
            print("Neteisingas pasirinkimas!")


if __name__ == '__main__':
    main()
