#! /usr/bin/env python
# -*- coding: utf-8 -*-
import pygtk
pygtk.require('2.0')
import gtk
import gtk.glade
import sys
import MySQLdb
import string
from municipios.municipios import Municipio
from datetime import datetime

class Calle():
    def __init__(self, entry=None, statusbar=None, panel=None):
        self.widgets = gtk.glade.XML('../calles/calles.glade')
        self.widgets.signal_autoconnect(self)

        self.caja = self.widgets.get_widget('vbox1')
        self.window = self.widgets.get_widget('window1')

        self.window.connect("destroy", self.destroy)
        
        button = self.widgets.get_widget('messagedialog2').add_button('Aceptar', 1)
        button.connect("clicked", self.acceptDeleteCalle)
        
        button = self.widgets.get_widget('messagedialog3').add_button('Aceptar', 1)
        button.connect("clicked", self.acceptModifyCalle)
        
        self.liststore = None
        self.cursor = self.conectar()
        self.insertColumn()

        self.cursor.execute('select c.id, c.nombre, m.municipio, c.cp, c.id_sector from calles_nueva c, municipios m where c.poblacion = m.id order by c.id')
        tuplas = self.cursor.fetchall()
        tuplas = self.normalizar(tuplas)
        self.fillData(tuplas)

        self.filtrado = False

        if (statusbar):
            self.statusbar = statusbar
        else:
            self.statusbar = gtk.Statusbar()
        if (panel):
            self.panel = panel
        else:
            self.panel = gtk.ListStore(str, str, str)
        if (entry):
            self.entry = entry
            if (self.entry != ''):
                data = self.widgets.get_widget('entry8')
                data.set_text(self.entry.get_text())
        else:
            self.entry = gtk.Entry()

        self.widgets.get_widget('statusbar1').push(1,'Busque una calle')
        self.statusbar.push(1,'Busque una calle')
        self.insertPanel('INFO','Abierta tabla de calles')

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
        
        tvcolumn = gtk.TreeViewColumn('Población')
        treeview.append_column(tvcolumn)
        tvcolumn.pack_start(cell, True)
        tvcolumn.add_attribute(cell, 'text', 2)
        tvcolumn.set_sort_column_id(2)
        
        tvcolumn = gtk.TreeViewColumn('Código P.')
        treeview.append_column(tvcolumn)
        tvcolumn.pack_start(cell, True)
        tvcolumn.add_attribute(cell, 'text', 3)
        tvcolumn.set_sort_column_id(3)
        
        tvcolumn = gtk.TreeViewColumn('Id. Sector')
        treeview.append_column(tvcolumn)
        tvcolumn.pack_start(cell, True)
        tvcolumn.add_attribute(cell, 'text', 4)
        tvcolumn.set_sort_column_id(4)
        
        treeview.set_search_column(1)
        
        self.liststore = gtk.ListStore(int,str, str, int, int)
        treeview.set_model(self.liststore)
        
    def fillData(self, tuplas):
        self.liststore.clear()
        for fila in tuplas:
            fila = list(fila)
            fila[1] = str(fila[1])
            fila[1] = str.capitalize(fila[1])
            fila[2] = unicode(fila[2], 'iso8859-15')
            self.liststore.append([fila[0],fila[1],fila[2],fila[3],fila[4]])

    def search(self, data=None):
        searchById = self.widgets.get_widget('radiobutton1')
        searchByName = self.widgets.get_widget('radiobutton2')
        if (not self.filtrado):
            self.cursor.execute('select c.id, c.nombre, m.municipio, c.cp, c.id_sector from calles_nueva c, municipios m where c.poblacion = m.id order by c.id')
        else:
            self.cursor.execute('select c.id, c.nombre, m.municipio, c.cp, c.id_sector from calles_nueva c, municipios m where c.poblacion = m.id and m.municipio = %s order by c.id', unicode(self.widgets.get_widget('entry8').get_text(),'utf 8'))

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

    def clickInsertCalle(self, data=None):
        self.widgets.get_widget('window2').show()
        self.widgets.get_widget('statusbar1').push(4,'Insertando calle...')
        self.statusbar.push(4,'Insertando calle...')
        self.cursor.execute('select max(id)+1 from calles_nueva')
        num = self.cursor.fetchone()
        self.widgets.get_widget('entry1').set_text('')
        self.widgets.get_widget('entry2').set_text(str(num[0]))
        self.widgets.get_widget('entry3').set_text('')
        self.widgets.get_widget('entry6').set_text('')
        self.widgets.get_widget('entry9').set_text('')
        self.widgets.get_widget('entry10').set_text('')
        
    def clickDeleteCalle(self, data=None):
        self.widgets.get_widget('statusbar1').push(5,'Eliminando calle...')
        self.statusbar.push(5,'Eliminando calle...')
        value = self.getSelection('borrar')

        if value:
            self.cursor.execute('select c.id, c.nombre, m.municipio, c.cp, c.id_sector from calles_nueva c, municipios m where c.poblacion = m.id and c.id = %s', value)
            
            tupla = self.cursor.fetchone()
            ident = str(tupla[0])
            nombre = str(tupla[1])
            municipio = str(tupla[2])
            cp = str(tupla[3])
            id_sector = str(tupla[4])
            dialog = self.widgets.get_widget('messagedialog2')
            dialog.format_secondary_text('Desea eliminar ('+ident+', '+nombre+', '+municipio+', '+cp+', '+id_sector+')')
            dialog.show()

    def clickModifyCalle(self, data=None):
        self.widgets.get_widget('statusbar1').push(6,'Modificando calle...')
        self.statusbar.push(6,'Modificando calle...')
        value = self.getSelection('modificar')
        if value:
            self.cursor.execute('select c.id, c.nombre, m.municipio, c.cp, c.id_sector from calles_nueva c, municipios m where c.poblacion = m.id and c.id = %s', (value,))
            tupla = self.cursor.fetchone()

            ident = unicode(str(tupla[0]), 'iso8859-15')
            nombre = unicode(str(tupla[1]), 'iso8859-15')
            municipio = unicode(str(tupla[2]), 'iso8859-15')
            cp = unicode(str(tupla[3]), 'iso8859-15')
            id_sector = unicode(str(tupla[4]), 'iso8859-15')
                        
            self.widgets.get_widget('entry4').set_text(ident)
            self.widgets.get_widget('entry5').set_text(nombre)
            self.widgets.get_widget('entry7').set_text(municipio)
            self.widgets.get_widget('entry11').set_text(cp)
            self.widgets.get_widget('entry12').set_text(id_sector)
            self.widgets.get_widget('window3').show()

    def dialogModifyCalle(self, data=None):
        ident = self.widgets.get_widget('entry4').get_text()
        nombre = self.widgets.get_widget('entry5').get_text()
        municipio = self.widgets.get_widget('entry7').get_text()
        cp = self.widgets.get_widget('entry11').get_text()
        id_sector = self.widgets.get_widget('entry12').get_text()
        
        dialog = self.widgets.get_widget('messagedialog3')
        dialog.format_secondary_text('¿Son correctos los cambios?\n('+ident+', '+nombre+', '+municipio+', '+cp+', '+id_sector+')')
        dialog.show()
    
    def acceptModifyCalle(self, data=None):
        ident = self.widgets.get_widget('entry4').get_text()
        nombre = self.widgets.get_widget('entry5').get_text()
        municipio = self.widgets.get_widget('entry7').get_text()

        try:
            cp = int(self.widgets.get_widget('entry11').get_text())
            id_sector = int(self.widgets.get_widget('entry12').get_text())
            if((nombre == '') or (municipio == '')):
                raise ValueError
            try:
                self.cursor.execute("select id from municipios where lower(municipio) = %s", unicode(string.lower(municipio), 'utf 8'))
                idmunicipio = self.cursor.fetchone()
                idmunicipio = int(idmunicipio[0])
                
                self.cursor.execute("update calles_nueva set nombre = %s, poblacion = %s, id_sector = %s, cp = %s  where id = %s", (unicode(nombre, 'utf 8'), idmunicipio, id_sector, cp, ident))
                if(not self.filtrado):
                    self.cursor.execute('select c.id, c.nombre, m.municipio, c.cp, c.id_sector from calles_nueva c, municipios m where c.poblacion = m.id order by c.id')
                else:
                    self.cursor.execute('select c.id, c.nombre, m.municipio, c.cp, c.id_sector from calles_nueva c, municipios m where c.poblacion = m.id and m.municipio = %s order by c.id', unicode(self.widgets.get_widget('entry8').get_text(),'utf 8'))
                
                tuplas = self.cursor.fetchall()
                tuplas = self.normalizar(tuplas)
                self.fillData(tuplas)
                self.widgets.get_widget('window3').hide()
                self.insertPanel('OK','Modificación de calle realizada correctamente')
            except MySQLdb.Error, e:
                self.error(e)
        except ValueError:
            self.error('Los campos código postal e identificador del sector debe den ser un número entero o los campos nombre, municipio están vacíos.')
            
    def acceptDeleteCalle(self, data=None):
        value = self.getSelection('')
        if value:
            self.cursor.execute("delete from calles_nueva where id = %s", value)
            if (not self.filtrado):
                self.cursor.execute('select c.id, c.nombre, m.municipio, c.cp, c.id_sector from calles_nueva c, municipios m where c.poblacion = m.id order by c.id')
            else:
                self.cursor.execute('select c.id, c.nombre, m.municipio, c.cp, c.id_sector from calles_nueva c, municipios m where c.poblacion = m.id and m.municipio = %s order by c.id', unicode(self.widgets.get_widget('entry8').get_text(),'utf 8'))
                
            tuplas = self.cursor.fetchall()
            tuplas = self.normalizar(tuplas)
            self.fillData(tuplas)
            self.insertPanel('OK','Calle eliminada correctamente')
            
    def acceptNewCalle(self, data=None):
        identificador = self.widgets.get_widget('entry2').get_text()
        nombre = unicode(self.widgets.get_widget('entry3').get_text(), 'utf 8')
        municipio = self.widgets.get_widget('entry6').get_text()
        codigopostal = self.widgets.get_widget('entry9').get_text()
        idsector = self.widgets.get_widget('entry10').get_text()
        try:
            int(identificador)
            int(codigopostal)
            int(idsector)
            if((nombre == '') or (municipio == '')):
                raise ValueError
            try:
                municipio = unicode(string.lower(municipio), 'utf 8')

                self.cursor.execute('select id from municipios where lower(municipio) = %s', municipio)
                tupla = self.cursor.fetchone()
                idmunicipio = int(tupla[0])
                aux = [int(identificador), nombre, idmunicipio, int(codigopostal), int(idsector)]
                self.cursor.execute('insert into calles_nueva(id, nombre, poblacion, cp, id_sector) values (%s, %s, %s, %s, %s)', aux)
                if (not self.filtrado):
                    self.cursor.execute('select c.id, c.nombre, m.municipio, c.cp, c.id_sector from calles_nueva c, municipios m where c.poblacion = m.id order by c.id')
                else:
                    self.cursor.execute('select c.id, c.nombre, m.municipio, c.cp, c.id_sector from calles_nueva c, municipios m where c.poblacion = m.id and m.municipio = %s order by c.id', unicode(self.widgets.get_widget('entry8').get_text(),'utf 8'))
        
                tuplas = self.cursor.fetchall()
                tuplas = self.normalizar(tuplas)
                self.fillData(tuplas)
                self.hideWindow2()
                self.insertPanel('OK','Nueva calle creada correctamente')
            except MySQLdb.Error, e:
                self.error(e)
        except ValueError:
            self.error('Los campos identificador, codigo postal e identificador\ndel sector deben de ser un números, o los campos\npoblación, nombre están vacíos')

    def getSelection(self, msg):
        treeview = self.widgets.get_widget('treeview1')
        treeselection = treeview.get_selection()
        (model, iteration) = treeselection.get_selected()
        try:
            value = self.liststore.get_value(iteration, 0)
            return value
        except TypeError:
            self.error('Seleccione la calle que desea '+ str(msg))
            return False

    def error(self, msg):
        self.insertPanel('ERROR', msg)
        dialog = self.widgets.get_widget('messagedialog1')
        dialog.format_secondary_text(str(msg))
        dialog.show()
    
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

    def showMunicipio(self, widget=None, event=None, data=None):
        if (event==0):
            widget.set_text('')
        else:
            if (widget.get_name() == 'entry8'):
                self.widgets.get_widget('statusbar1').push(7,'Filtrando calles por municipio...')
                self.statusbar.push(7,'Filtrando calles por municipio...')
            aux = Municipio(widget)
            aux.window.set_modal(True)
            aux.window.present()

    def changeEntry(self, data=None, color=None):
        self.widgets.get_widget('statusbar1').pop(7)
        self.statusbar.pop(7)
        
        municipio = unicode(data.get_text(), 'utf 8')

        if (municipio == ' '):
            self.clearEntry(data, None)
        else:
            #cambiar color de fondo de entry
            if (color == None):
                color = "#FFFF00"
            data.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse(color))
            if (municipio == ''):
                self.cursor.execute('select c.id, c.nombre, m.municipio, c.cp, c.id_sector from calles_nueva c, municipios m where c.poblacion = m.id order by c.id')
                self.filtrado = False
            else:
                self.cursor.execute('select c.id, c.nombre, m.municipio, c.cp, c.id_sector from calles_nueva c, municipios m where c.poblacion = m.id and m.municipio = %s order by c.id', (municipio,))
                self.filtrado = True
            tuplas = self.cursor.fetchall()
            tuplas = self.normalizar(tuplas)
            self.fillData(tuplas)

    def clearEntry(self, widget, event, data=None):
        widget.set_text('')
        self.changeEntry(widget, '#FFFFFF')
        
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
        self.cursor.execute('select nombre from calles_nueva where id = %s', self.getSelection('insertar'))
        tupla = self.cursor.fetchone()
        if tupla:
            value = str.capitalize(tupla[0])
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
    Calle()
    gtk.gdk.threads_init()
    gtk.gdk.threads_enter()
    gtk.main()
    gtk.gdk.threads_leave()

if __name__ == "__main__":
    sys.exit(main())
