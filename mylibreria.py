from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtWidgets import *
import sqlite3

# Capa de datos
db = 'myDataBase.db'
"""
CREATE TABLE "libro" (
    `id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    `ISBN`	text,
    `titulo`	text,
    `autor`	text,
    `editorial`	text
)
"""

# Helper para operaciones SQL inser, update y delete
def execute_query(query):
    global db
    con = sqlite3.connect(db)
    cursor = con.cursor()
    cursor.execute(query)
    con.commit()
    print(query)
    cursor.close()
    con.close()

# CRUD = Create Read Update Delete
def create_book(isbn, title, author, editorial):
    query = """INSERT INTO libro(isbn,titulo,autor,editorial) 
        VALUES ('{}','{}','{}','{}')""".format(isbn,title,author,editorial)
    execute_query(query)

def update_book(id, isbn, title, author, editorial):
    query = """update libro 
        set isbn='{}', titulo='{}', autor='{}', editorial='{}' 
        where id = {}""".format(isbn,title,author,editorial,id)
    execute_query(query)

def delete_book(id):
    query = "delete from libro where id = {}".format(id)
    execute_query(query)

def read_books(keyword=''):
    global db
    query = "select * from libro" + ("" if keyword is None else """  
        where isbn like '%{0}%' or titulo like '%{0}%' or 
        autor like '%{0}%' or editorial like '%{0}%' """.format(keyword))  
    con = sqlite3.connect(db)
    cursor = con.cursor()
    result = list(cursor.execute(query))
    cursor.close()
    con.close()
    return enumerate (result)

# funciones para control de vista
def show_book_list(keyword=''):
    global dlg
    for num_row, books in read_books(keyword):
        dlg.lista.insertRow(num_row)
        for num_col, data in enumerate(books):
            cell = QtWidgets.QTableWidgetItem(str(data))
            cell.setTextAlignment(QtCore.Qt.AlignCenter)
            dlg.lista.setItem(num_row, num_col, cell)

def refresh_book_list(keyword=''):
    global dlg
    dlg.lista.setRowCount(0)
    show_book_list(keyword)

# acciones para asociar a eventos
def add_book():
    global dlg
    isbn, title, author, editorial = dlg.isbnLineEdit.text().strip(), \
        dlg.tituloLineEdit.text().strip(), \
        dlg.autorLineEdit.text().strip(), \
        dlg.editorialLineEdit.text().strip()
    create_book(isbn, title, author, editorial)
    refresh_book_list()
    QMessageBox.information(dlg, "Información", \
                                    "Libro {} añadido.".format(title))

def search_book_by_keyword():
    global dlg
    keyword = dlg.busquedaLineEdit.text()
    refresh_book_list() if len(keyword) < 3 else refresh_book_list(keyword)

def remove_book(id):
    delete_book(id)
    refresh_book_list()

def manage_book():
    # inner func to pythonize user question
    
    def user_quest(message):
        global dlg
        return QMessageBox.question(dlg, 'Atento', message, \
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No) 
    
    global dlg
    index = dlg.lista.currentRow()
    id, isbn, title, author, editorial =  \
        dlg.lista.item(index,0).text(), \
        dlg.lista.item(index,1).text(), \
        dlg.lista.item(index,2).text(), \
        dlg.lista.item(index,3).text(), \
        dlg.lista.item(index,4).text()
    message = "¿Quieres borrar el libro {}?".format(title)
    if user_quest(message) == QMessageBox.Yes:
        remove_book(id)
    else:
        message = "¿Quieres modificar el libro {}?".format(title)
        if user_quest(message) == QMessageBox.Yes:
            edit_book(id, isbn, title, author, editorial)

def edit_book(id, isbn, title, author, editorial):
    
    def user_prompt(message, value):
        global dlg
        return QInputDialog.getText(dlg, "Edition dialog", message, QLineEdit.Normal, value)
    
    # dialog hell
    new_isbn, okPressed = user_prompt("Nuevo Isbn:", isbn)
    if okPressed and new_isbn is not None:
        isbn = new_isbn
    new_title, okPressed = user_prompt("Nuevo titulo:", title)
    if okPressed and new_title is not None:
        title = new_title
    new_author, okPressed = user_prompt("Nuevo autor:",  author)
    if okPressed and new_author is not None:
        author = new_author
    new_editorial, okPressed = user_prompt("Nuevo editorial:", editorial)
    if okPressed and new_editorial is not None:
        editorial = new_editorial
    update_book(id, isbn, title, author, editorial)
    refresh_book_list()

app = QtWidgets.QApplication([])
dlg = uic.loadUi('crud.ui')

# Asociación funciones a eventos
dlg.aniadirButton.clicked.connect(add_book)
dlg.busquedaLineEdit.textChanged.connect(search_book_by_keyword)
dlg.lista.clicked.connect(manage_book)

show_book_list()
dlg.show()
app.exec()