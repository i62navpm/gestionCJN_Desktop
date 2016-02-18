#! /usr/bin/env python
# -*- coding: utf-8 -*-
import pygtk
pygtk.require('2.0')
import gtk
import gtk.glade
import sys
import MySQLdb
import string
from datetime import datetime

class Provincia():
    def __init__(self, entry=None, statusbar=None, panel=None):
        self.widgets = gtk.glade.XML('../provincias/provincias.glade')
        self.widgets.signal_autoconnect(self)

        self.caja = self.widgets.get_widget('vbox1')
        self.window = self.widgets.get_widget('window1')
        
        if (entry):
            self.entry = entry
        else:
            self.entry = gtk.Entry()    
        if (statusbar):
            self.statusbar = statusbar
        else:
            self.statusbar = gtk.Statusbar()
        if (panel):
            self.panel = panel
        else:
            self.panel = gtk.ListStore(str, str, str)
        
        self.window.connect("destroy", self.destroy)
        self.widgets.get_widget('statusbar1').push(1,'Busque una provincia')
        self.statusbar.push(1,'Busque una provincia')
        self.insertPanel('INFO','Abierta tabla de provincias')
        
        button = self.widgets.get_widget('messagedialog2').add_button('Aceptar', 1)
        button.connect("clicked", self.acceptDeleteProvincia)
        
        button = self.widgets.get_widget('messagedialog3').add_button('Aceptar', 1)
        button.connect("clicked", self.acceptModifyProvincia)
        
        self.liststore = None
        self.cursor = self.conectar()
        self.insertColumn()
        
        self.cursor.execute('select id, nombre from provincias_nueva order by id')
        tuplas = self.cursor.fetchall()
        tuplas = self.normalizar(tuplas)
        self.fillData(tuplas)

    def normalizar(self, tuplas):
        lista = list()
        for tupla in tuplas:
            tupla = list(tupla)
            lista.append(tupla)
        
        for aux in lista:
            aux[1] = unicode(aux[1], 'iso8859-15')
        return lista  

    def insertPanel(self, estado, msg):
        data = datetime.today().strftime("%d/%m/%y %H:%M:%S")
        if (estado == 'INFO'):
            color = 'black'
        if (estado == 'OK'):
            color = '#0B0B61'
        if (estado == 'ERROR'):
            color = '#8A0808'
       
        try:
            if (msg.find('\n') != -1):
                msg = msg.replace('\n','')
            self.panel.append([data, estado + ': ' + str(msg), color])
        except AttributeError, e:
            self.panel.append([data, estado + ': ' + str(msg), color])
        
    def insertColumn(self):
        treeview = self.widgets.get_widget('treeview1')
        cell = gtk.CellRendererText()
        
        tvcolumn = gtk.TreeViewColumn('Id')
        treeview.append_column(tvcolumn)
        tvcolumn.pack_start(cell, True)
        tvcolumn.add_attribute(cell, 'text', 0)
        tvcolumn.set_sort_column_id(0)
        
        tvcolumn = gtk.TreeViewColumn('Nombre')
        treeview.append_column(tvcolumn)
        tvcolumn.pack_start(cell, True)
        tvcolumn.add_attribute(cell, 'text', 1)        
        tvcolumn.set_sort_column_id(1)

        treeview.set_search_column(1)
        
        self.liststore = gtk.ListStore(int,str)
        treeview.set_model(self.liststore)

    def fillData(self, tuplas):
        self.liststore.clear()
        for fila in tuplas:
            fila = list(fila)
            self.liststore.append(fila)

    def search(self, data=None):
        searchById = self.widgets.get_widget('radiobutton1')
        searchByName = self.widgets.get_widget('radiobutton2')

        self.cursor.execute('select id, nombre from provincias_nueva order by id')        
        tuplas = self.cursor.fetchall()

        if (searchById.get_active() == True):
            lista = list()
            for tupla in tuplas:
                if (str(tupla[0]).find(str(data.get_text())) == 0):
                    lista.append(tupla)
            self.fillData(lista)
        else:
            lista = list()
            for tupla in tuplas:
                tupla = list(tupla)
                tupla[1] = unicode(tupla[1], 'iso8859-15')
                texto = str(data.get_text())

                if (string.lower(tupla[1]).find(string.lower(texto)) == 0):
                    lista.append(tupla)

            self.fillData(lista)

    def clean(self, widget=None, event=None, data=None):
        self.widgets.get_widget('entry1').set_text('')
        
    def enterToogleId(self, widget, data=None):
        self.widgets.get_widget('statusbar1').push(2,'Buscar por id...')
        self.statusbar.push(2,'Buscar por id...')

    def leaveToogleId(self, widget, data=None):
        self.widgets.get_widget('statusbar1').pop(2)
        self.statusbar.pop(2)

    def enterToogleName(self, widget, data=None):
        self.widgets.get_widget('statusbar1').push(3,'Buscar por nombre...')
        self.statusbar.push(3,'Buscar por nombre...')

    def leaveToogleName(self, widget, data=None):
        self.widgets.get_widget('statusbar1').pop(3)
        self.statusbar.pop(3)
    def clickInsertProvincia(self, data=None):
        self.widgets.get_widget('window2').show()
        self.widgets.get_widget('statusbar1').push(4,'Insertando provincia...')
        self.statusbar.push(4,'Insertando provincia...')
        self.cursor.execute('select max(id)+1 from provincias_nueva')
        num = self.cursor.fetchone()
        self.widgets.get_widget('entry1').set_text('')
        self.widgets.get_widget('entry2').set_text(str(num[0]))
        self.widgets.get_widget('entry3').set_text('')

    def clickDeleteProvincia(self, data=None):
        self.widgets.get_widget('statusbar1').push(5,'Eliminando provincia...')
        self.statusbar.push(5,'Eliminando provincia...')
        value = self.getSelection('borrar')

        if value:
            self.cursor.execute("select * from provincias_nueva where id = %s", value)
            tupla = self.cursor.fetchone()
            ident = str(tupla[0])
            nombre = str(tupla[1])

            dialog = self.widgets.get_widget('messagedialog2')
            dialog.format_secondary_text('Desea eliminar ('+ident+', '+nombre+')')
            dialog.show()

    def clickModifyProvincia(self, data=None):
        self.widgets.get_widget('statusbar1').push(6,'Modificando provincia...')
        self.statusbar.push(6,'Modificando provincia...')
        value = self.getSelection('modificar')
        if value:
            self.cursor.execute("select * from provincias_nueva where id = %s", (value,))
            tupla = self.cursor.fetchone()
            ident = str(tupla[0])
            nombre = unicode (str(tupla[1]), 'iso8859-15')
            
            self.widgets.get_widget('entry4').set_text(ident)
            self.widgets.get_widget('entry5').set_text(nombre)
            self.widgets.get_widget('window3').show()

    def dialogModifyProvincia(self, data=None):
        ident = self.widgets.get_widget('entry4').get_text()
        nombre = self.widgets.get_widget('entry5').get_text()
        
        dialog = self.widgets.get_widget('messagedialog3')
        dialog.format_secondary_text('¿Son correctos los cambios? ('+ident+', '+nombre+')')
        dialog.show()
    
    def acceptModifyProvincia(self, data=None):
        ident = self.widgets.get_widget('entry4').get_text()
        nombre = unicode(self.widgets.get_widget('entry5').get_text(), 'utf 8')
        try:
            self.cursor.execute("update provincias_nueva set nombre = %s where id = %s", (nombre, ident))
            self.cursor.execute("select * from provincias_nueva order by id")
            tuplas = self.cursor.fetchall()
            tuplas = self.normalizar(tuplas)
            self.fillData(tuplas)
            self.widgets.get_widget('window3').hide()
            self.insertPanel('OK','Modificación de provincia realizada correctamente')
        except MySQLdb.Error, e:
            self.error(e)
        
    def acceptDeleteProvincia(self, data=None):
        value = self.getSelection('')
        if value:
            self.cursor.execute("delete from provincias_nueva where id = %s", value)
            self.cursor.execute("select * from provincias_nueva order by id")
            tuplas = self.cursor.fetchall()
            tuplas = self.normalizar(tuplas)
            self.fillData(tuplas)
            self.insertPanel('OK','Provincia eliminada correctamente')
            
    def acceptNewProvincia(self, data=None):
        identificador = self.widgets.get_widget('entry2').get_text()
        nombre = unicode (self.widgets.get_widget('entry3').get_text(), 'utf 8')
        try:
            int(identificador)
            if(nombre == ''):
                raise ValueError
            aux = [long(identificador), nombre]
            try:
                self.cursor.execute('insert into provincias_nueva(id, nombre) values (%s, %s)', aux)
                self.cursor.execute('select * from provincias_nueva order by id')
                tuplas = self.cursor.fetchall()
                tuplas = self.normalizar(tuplas)
                self.fillData(tuplas)
                self.hideWindow2()
                self.insertPanel('OK','Nueva provincia creada correctamente')
            except MySQLdb.Error, e:
                self.error(e)
        except ValueError:
            self.error('El identificador debe de ser un número,\n o el nombre está vacío')

    def getSelection(self, msg):
        treeview = self.widgets.get_widget('treeview1')
        treeselection = treeview.get_selection()
        (model, iteration) = treeselection.get_selected()
        try:
            value = self.liststore.get_value(iteration, 0)
            return value
        except TypeError:
            self.error('Seleccione la provincia que desea '+msg)
            return False

    def error(self, msg):
        self.insertPanel('ERROR', msg)
        dialog = self.widgets.get_widget('messagedialog1')
        dialog.format_secondary_text(str(msg))
        dialog.show()

    def hideWindow1(self, data=None):
        self.window.hide()
        
    def hideWindow2(self, data=None):
        self.widgets.get_widget('window2').hide()
        self.widgets.get_widget('statusbar1').pop(4)
        self.statusbar.pop(4)

    def hideWindow3(self, data=None):
        self.widgets.get_widget('window3').hide()
        self.widgets.get_widget('statusbar1').pop(6)
        self.statusbar.pop(6)

    def deleteWindow(self, widget, data=None):
        widget.hide()
        self.widgets.get_widget('statusbar1').pop(4)
        self.statusbar.pop(4)
        self.widgets.get_widget('statusbar1').pop(5)
        self.statusbar.pop(5)
        self.widgets.get_widget('statusbar1').pop(6)
        self.statusbar.pop(6)
        return True

    def conectar(self):
        self.db = MySQLdb.connect(user="root", passwd="admin", db='proyecto')
        return self.db.cursor()

    def desconectar(self):
        self.db.close()

    def destroy(self, widget, data=None):
        if (widget != None):
            self.entry.set_text('')
        self.desconectar()
        self.window.hide()

    def doubleClick(self, widget, ident=None, data=None):
        self.cursor.execute('select nombre from provincias_nueva where id = %s', self.getSelection('insertar'))
        tupla = self.cursor.fetchone()
        if tupla:
            value = str(tupla[0])
            value = unicode(value, 'iso8859-15')
            self.entry.set_text(value)
            self.destroy(None)
        
    def rightClick(self, widget, event=None):
        treeview = self.widgets.get_widget('treeview1')
        context_menu = self.widgets.get_widget("menu2")
        path = widget.get_path_at_pos(int(event.x), int(event.y))
        if (path == None):
            """If we didn't get apath then we don't want anything
		    to be selected."""
            selection = widget.get_selection()
            selection.unselect_all()
        if (event.button == 3):
            #This is a right-click
            context_menu.popup( None, None, None, event.button, event.time)

        
def main():
    Provincia()
    gtk.gdk.threads_init()
    gtk.gdk.threads_enter()
    gtk.main()
    gtk.gdk.threads_leave()

if __name__ == "__main__":
    sys.exit(main())
