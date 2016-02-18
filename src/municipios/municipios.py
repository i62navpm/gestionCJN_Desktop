#! /usr/bin/env python
# -*- coding: utf-8 -*-
import pygtk
pygtk.require('2.0')
import gtk
import gtk.glade
import sys
import MySQLdb
import string
from provincias.provincias import Provincia
from datetime import datetime

class Municipio():
    def __init__(self, entry=None, statusbar=None, panel=None):
        self.widgets = gtk.glade.XML('../municipios/municipios.glade')
        self.widgets.signal_autoconnect(self)

        self.caja = self.widgets.get_widget('vbox1')
        self.window = self.widgets.get_widget('window1')
      
        self.window.connect("destroy", self.destroy)

        button = self.widgets.get_widget('messagedialog2').add_button('Aceptar', 1)
        button.connect("clicked", self.acceptDeleteMunicipio)
        
        button = self.widgets.get_widget('messagedialog3').add_button('Aceptar', 1)
        button.connect("clicked", self.acceptModifyMunicipio)
        
        #Ventana de diálogo para guardar antes de salir
        """        
        button = self.widgets.get_widget('messagedialog4').add_button('Cerrar sin guardar', 0)
        button = self.widgets.get_widget('messagedialog4').add_button('Cancelar', 1)
        button = self.widgets.get_widget('messagedialog4').add_button('Guardar', 2)
        """
        
        self.liststore = None
        self.cursor = self.conectar()
        self.insertColumn()

        self.cursor.execute('select m.id, m.municipio, p.nombre from municipios m, provincias_nueva p where m.provincia = p.id order by m.id')
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
        
        self.widgets.get_widget('statusbar1').push(1,'Busque un municipio')
        self.statusbar.push(1,'Busque un municipio')
        self.insertPanel('INFO','Abierta tabla de municipios')
    
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
        
        tvcolumn = gtk.TreeViewColumn('Provincia')
        treeview.append_column(tvcolumn)
        tvcolumn.pack_start(cell, True)
        tvcolumn.add_attribute(cell, 'text', 2)
        tvcolumn.set_sort_column_id(2)

        treeview.set_search_column(1)
        
        self.liststore = gtk.ListStore(int,str, str)
        treeview.set_model(self.liststore)
        
    def fillData(self, tuplas):
        self.liststore.clear()
        for fila in tuplas:
            fila = list(fila)
            fila[2] = unicode(fila[2], 'iso8859-15')
            self.liststore.append(fila)

    def search(self, data=None):
        searchById = self.widgets.get_widget('radiobutton1')
        searchByName = self.widgets.get_widget('radiobutton2')
        if (not self.filtrado):
            self.cursor.execute('select m.id, m.municipio, p.nombre from municipios m, provincias_nueva p where m.provincia = p.id order by m.id')        
        else:
            self.cursor.execute('select m.id, m.municipio, p.nombre from municipios m, provincias_nueva p where m.provincia = p.id and p.nombre = %s order by m.id', unicode(self.widgets.get_widget('entry8').get_text(), 'utf 8'))

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

    def clickInsertMunicipio(self, data=None):
        self.widgets.get_widget('window2').show()
        self.widgets.get_widget('statusbar1').push(4,'Insertando municipio...')
        self.statusbar.push(4,'Insertando municipio...')
        self.cursor.execute('select max(id)+1 from municipios')
        num = self.cursor.fetchone()
        self.widgets.get_widget('entry1').set_text('')
        self.widgets.get_widget('entry2').set_text(str(num[0]))
        self.widgets.get_widget('entry3').set_text('')
        self.widgets.get_widget('entry6').set_text('')

    def clickDeleteMunicipio(self, data=None):
        self.widgets.get_widget('statusbar1').push(5,'Eliminando municipio...')
        self.statusbar.push(5,'Eliminando municipio...')
        value = self.getSelection('borrar')

        if value:
            self.cursor.execute('select m.id, m.municipio, p.nombre from municipios m, provincias_nueva p where m.provincia = p.id and m.id = %s', value)
            tupla = self.cursor.fetchone()
            ident = str(tupla[0])
            nombre = str(tupla[1])
            provincia = str(tupla[2])
            dialog = self.widgets.get_widget('messagedialog2')
            dialog.format_secondary_text('Desea eliminar ('+ident+', '+nombre+', '+provincia+')')
            dialog.show()

    def clickModifyMunicipio(self, data=None):
        self.widgets.get_widget('statusbar1').push(6,'Modificando municipio...')
        self.statusbar.push(6,'Modificando municipio...')
        value = self.getSelection('modificar')
        if value:
            self.cursor.execute('select m.id, m.municipio, p.nombre from municipios m, provincias_nueva p where m.provincia = p.id and m.id = %s', (value,))
            tupla = self.cursor.fetchone()
            ident = str(tupla[0])
            nombre = unicode(str(tupla[1]),'iso8859-15')
            provincia = unicode(str(tupla[2]), 'iso8859-15')
            
            self.widgets.get_widget('entry4').set_text(ident)
            self.widgets.get_widget('entry5').set_text(nombre)
            self.widgets.get_widget('entry7').set_text(provincia)
            self.widgets.get_widget('window3').show()

    def dialogModifyMunicipio(self, data=None):
        ident = self.widgets.get_widget('entry4').get_text()
        nombre = self.widgets.get_widget('entry5').get_text()
        provincia = self.widgets.get_widget('entry7').get_text()
        dialog = self.widgets.get_widget('messagedialog3')
        dialog.format_secondary_text('¿Son correctos los cambios? ('+ident+', '+nombre+', '+provincia+')')
        dialog.show()
    
    def acceptModifyMunicipio(self, data=None):
        ident = self.widgets.get_widget('entry4').get_text()
        nombre = self.widgets.get_widget('entry5').get_text()
        provincia = self.widgets.get_widget('entry7').get_text()
        try:
            int(ident)
            if((nombre == '') or (provincia == '')):
                raise ValueError
            try:
                self.cursor.execute("select id from provincias_nueva where lower(nombre) = %s", unicode(string.lower(provincia), 'utf 8'))
                idprovincia = self.cursor.fetchone()
                idprovincia = int(idprovincia[0])

                self.cursor.execute("update municipios set municipio = %s, provincia = %s  where id = %s", (unicode(nombre, 'utf 8'), idprovincia, ident))
                if(not self.filtrado):
                    self.cursor.execute('select m.id, m.municipio, p.nombre from municipios m, provincias_nueva p where m.provincia = p.id order by m.id')
                else:
                    self.cursor.execute('select m.id, m.municipio, p.nombre from municipios m, provincias_nueva p where m.provincia = p.id and p.nombre = %s order by m.id', unicode(self.widgets.get_widget('entry8').get_text(), 'utf 8'))
                
                tuplas = self.cursor.fetchall()
                tuplas = self.normalizar(tuplas)
                self.fillData(tuplas)
                self.widgets.get_widget('window3').hide()
                self.insertPanel('OK','Modificación de municipio realizado correctamente')
            except MySQLdb.Error, e:
                self.error(e)
        except ValueError:
            self.error('El identificador debe de ser un número,\n o los campos provincia, nombre están vacíos')
        
    def acceptDeleteMunicipio(self, data=None):
        value = self.getSelection('')
        if value:
            self.cursor.execute("delete from municipios where id = %s", value)
            if (not self.filtrado):
                self.cursor.execute('select m.id, m.municipio, p.nombre from municipios m, provincias_nueva p where m.provincia = p.id order by m.id')
            else:
                self.cursor.execute('select m.id, m.municipio, p.nombre from municipios m, provincias_nueva p where m.provincia = p.id and p.nombre = %s order by m.id', unicode(self.widgets.get_widget('entry8').get_text(), 'utf 8'))
                
            tuplas = self.cursor.fetchall()
            tuplas = self.normalizar(tuplas)
            self.fillData(tuplas)
            self.insertPanel('OK','Municipio eliminado correctamente')
            
    def acceptNewMunicipio(self, data=None):
        identificador = self.widgets.get_widget('entry2').get_text()
        nombre = self.widgets.get_widget('entry3').get_text()
        provincia = self.widgets.get_widget('entry6').get_text()
        try:
            int(identificador)
            if((nombre == '') or (provincia == '')):
                raise ValueError
            aux = [identificador, nombre, provincia]
            try:
                self.cursor.execute('select id from provincias_nueva where lower(nombre) = %s', unicode(string.lower(provincia), 'utf 8'))
                tupla = self.cursor.fetchone()
                idprovincia = int(tupla[0])
                aux = [int(identificador), unicode(nombre, 'utf 8'), idprovincia]
                self.cursor.execute('insert into municipios(id, municipio, provincia) values (%s, %s, %s)', aux)
                if (not self.filtrado):
                    self.cursor.execute('select m.id, m.municipio, p.nombre from municipios m, provincias_nueva p where m.provincia = p.id order by m.id')
                else:
                    self.cursor.execute('select m.id, m.municipio, p.nombre from municipios m, provincias_nueva p where m.provincia = p.id and p.nombre = %s order by m.id', unicode(self.widgets.get_widget('entry8').get_text(), 'utf 8'))
        
                tuplas = self.cursor.fetchall()
                tuplas = self.normalizar(tuplas)
                self.fillData(tuplas)
                self.hideWindow2()
                self.insertPanel('OK','Nuevo municipio creado correctamente')
            except MySQLdb.Error, e:
                self.error(e)
        except ValueError:
            self.error('El identificador debe de ser un número,\n o los campos provincia, nombre están vacíos')

    def getSelection(self, msg):
        treeview = self.widgets.get_widget('treeview1')
        treeselection = treeview.get_selection()
        (model, iteration) = treeselection.get_selected()
        try:
            value = self.liststore.get_value(iteration, 0)
            return value
        except TypeError:
            self.error('Seleccione el municipio que desea '+msg)
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

    def showProvincia(self, widget=None, event=None, data=None):
        if (event==0):
            widget.set_text('')
        else:
            if (widget.get_name() == 'entry8'):
                self.widgets.get_widget('statusbar1').push(7,'Filtrando municipio por provincia...')
                self.statusbar.push(7,'Filtrando municipio por provincia...')
            aux = Provincia(widget)
            aux.window.set_modal(True)
            aux.window.present()

    def changeEntry(self, data=None, color=None):
        self.widgets.get_widget('statusbar1').pop(7)
        self.statusbar.pop(7)
        
        provincia = data.get_text()

        if (provincia == ' '):
            self.clearEntry(data, None)
        else:
            #cambiar color de fondo de entry
            if (color == None):
                color = "#FFFF00"
            data.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse(color))
            
            if (provincia == ''):
                self.cursor.execute('select m.id, m.municipio, p.nombre from municipios m, provincias_nueva p where m.provincia = p.id order by m.id')
                self.filtrado = False
            else:
                self.cursor.execute('select m.id, m.municipio, p.nombre from municipios m, provincias_nueva p where m.provincia = p.id and p.nombre = %s order by m.id', unicode(data.get_text(), 'utf 8'))
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
        self.cursor.execute('select municipio from municipios where id = %s', self.getSelection('insertar'))
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
    Municipio()
    gtk.gdk.threads_init()
    gtk.gdk.threads_enter()
    gtk.main()
    gtk.gdk.threads_leave()

if __name__ == "__main__":
    sys.exit(main())
