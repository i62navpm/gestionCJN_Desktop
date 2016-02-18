#! /usr/bin/env python
# -*- coding: utf-8 -*-
import pygtk
pygtk.require('2.0')
import gtk
import gtk.glade
import sys
import MySQLdb
import string
import re
from datetime import datetime
from cofrades.cofrades import Cofrade

class PapeletaSitio():
    def __init__(self, entry=None, statusbar=None, panel=None):
        self.widgets = gtk.glade.XML('../papeletasitio/papeletasitio.glade')
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
        
        f = open('../inicio/anio.txt', 'r')
        anio = f.read()
        f.close()
        
        self.tabla = 'cofrades_papeletassitio_'+anio
        
        self.window.connect("destroy", self.destroy)
        self.widgets.get_widget('statusbar1').push(1,'Busque la papeleta de sitio')
        self.statusbar.push(1,'Busque la papeleta de sitio')
        self.insertPanel('INFO','Abierta tabla de las Papeletas Sitios')
        
        button = self.widgets.get_widget('messagedialog2').add_button('Aceptar', 1)
        button.connect("clicked", self.acceptDeletePapeletaSitio)
        
        button = self.widgets.get_widget('messagedialog3').add_button('Aceptar', 1)
        button.connect("clicked", self.acceptModifyPapeletaSitio)
        
        self.liststore = None
        self.cursor = self.conectar()
        self.insertColumn()
        try:
            self.cursor.execute('select s.n_orden, c.nombre, c.apellido1, c.apellido2, s.fecha from '+ self.tabla +' s, cofrades_datospersonales c where s.n_orden=c.n_orden order by s.n_orden asc')
            tuplas = self.cursor.fetchall()
            tuplas = self.normalizar(tuplas)
            self.fillData(tuplas)
        except MySQLdb.Error:
            msg = 'La tabla del año '+anio+' no existe'
            self.error(msg)

    def normalizar(self, tuplas):
        lista = list()
        for tupla in tuplas:
            tupla = list(tupla)
            lista.append(tupla)
        
        for aux in lista:
            nombre = unicode(str.capitalize(aux[1]), 'iso8859_15')
            aux2 = nombre.split(' ')
            for i in range(len(aux2)):
                aux2[i] = str.capitalize(str(aux2[i]))
            nombre= ' '.join(aux2)
            apellido1 = unicode(str.capitalize(aux[2]), 'iso8859_15')
            apellido2 = unicode(str.capitalize(aux[3]), 'iso8859_15')
            nombre = nombre.replace('Á','á')
            nombre = nombre.replace('É','é')
            nombre = nombre.replace('Í','í')
            nombre = nombre.replace('Ó','ó')
            nombre = nombre.replace('Ú','ú')
            nombre = nombre.replace('Ñ','ñ')
            apellido1 = apellido1.replace('Á','á')
            apellido1 = apellido1.replace('É','é')
            apellido1 = apellido1.replace('Í','í')
            apellido1 = apellido1.replace('Ó','ó')
            apellido1 = apellido1.replace('Ú','ú')
            apellido1 = apellido1.replace('Ñ','ñ')
            apellido2 = apellido2.replace('Á','á')
            apellido2 = apellido2.replace('É','é')
            apellido2 = apellido2.replace('Í','í')
            apellido2 = apellido2.replace('Ó','ó')
            apellido2 = apellido2.replace('Ú','ú')
            apellido2 = apellido2.replace('Ñ','ñ')

            aux[1] = nombre
            aux[2] = apellido1
            aux[3] = apellido2
        
            aux[4] = self.normalizarFecha(str(aux[4]))
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
        except AttributeError:
            self.panel.append([data, estado + ': ' + str(msg), color])
        
    def insertColumn(self):
        treeview = self.widgets.get_widget('treeview1')
        cell = gtk.CellRendererText()
        
        tvcolumn = gtk.TreeViewColumn('N. Orden')
        treeview.append_column(tvcolumn)
        tvcolumn.pack_start(cell, True)
        tvcolumn.add_attribute(cell, 'text', 0)
        tvcolumn.set_sort_column_id(0)
        
        tvcolumn = gtk.TreeViewColumn('Nombre')
        treeview.append_column(tvcolumn)
        tvcolumn.pack_start(cell, True)
        tvcolumn.add_attribute(cell, 'text', 1)
        tvcolumn.set_sort_column_id(1)
        
        tvcolumn = gtk.TreeViewColumn('Fecha')
        treeview.append_column(tvcolumn)
        tvcolumn.pack_start(cell, True)
        tvcolumn.add_attribute(cell, 'text', 2)
        tvcolumn.set_sort_column_id(2)
        
        treeview.set_search_column(1)
        
        self.liststore = gtk.ListStore(int,str,str)
        treeview.set_model(self.liststore)

    def fillData(self, tuplas):
        self.liststore.clear()
        for fila in tuplas:
            ident = fila[0]
            nombre = fila[1]+' '+fila[2]+' '+fila[3]
            fecha = fila[4]
      
            self.liststore.append([ident,nombre,fecha])

    def normalizarFecha(self, fecha):
        if fecha:
            year, month, day = fecha.split('-')
            fecha = str(day)+'/'+str(month)+'/'+str(year)
            return fecha
        else:
            return ''

    def search(self, data=None):
        searchById = self.widgets.get_widget('radiobutton1')
        searchByName = self.widgets.get_widget('radiobutton2')

        self.cursor.execute('select s.n_orden, c.nombre, c.apellido1, c.apellido2, s.fecha from '+ self.tabla +' s, cofrades_datospersonales c where s.n_orden=c.n_orden order by s.n_orden asc')
      
        tuplas = self.cursor.fetchall()

        if (data.get_text()==''):
            tuplas = self.normalizar(tuplas)
            self.fillData(tuplas)
        else:
            if (searchById.get_active() == True):
                lista = list()
                for tupla in tuplas:
                    if (str(tupla[0]).find(str(data.get_text())) == 0):
                        lista.append(tupla)
                self.fillData(lista)
            if (searchByName.get_active() == True):
                lista = list()
                tuplas = self.normalizar(tuplas)
                for tupla in tuplas:
                    tupla = list(tupla)
                    #tupla[1] = unicode(tupla[1], 'iso8859_15')
                    #tupla[2] = unicode(tupla[2], 'iso8859_15')
                    #tupla[3] = unicode(tupla[3], 'iso8859_15')
                    texto = string.lower(data.get_text())
                    nombre = texto.split(' ')
                    try:
                        hola = tupla[1].split(' ')
                        if (len(nombre) == 1):
                            if (string.lower(tupla[1]).find(nombre[0]) == 0):
                                lista.append(tupla)
                        if (len(hola) < 2):
                            if (len(nombre) > 1 and len(nombre)<3):
                                if ((string.lower(tupla[1]).find(nombre[0]) == 0)and(string.lower(tupla[2]).find(nombre[1]) == 0)):
                                    lista.append(tupla)
                            if (len(nombre) == 3):
                                if ((string.lower(tupla[1]).find(nombre[0]) == 0)and(string.lower(tupla[2]).find(nombre[1]) == 0)and (string.lower(tupla[3]).find(nombre[2]) == 0)):
                                    lista.append(tupla)
                        else:
                            if (len(nombre) > 1 and len(nombre)<3):
                                if ((string.lower(hola[0]).find(string.lower(nombre[0])) == 0)and(string.lower(hola[1]).find(string.lower(nombre[1])) == 0)):
                                    lista.append(tupla)
                            
                            if (len(nombre) == 3):
                                if ((string.lower(hola[0]).find(string.lower(nombre[0])) == 0)and(string.lower(hola[1]).find(string.lower(nombre[1])) == 0)and (string.lower(tupla[2]).find(nombre[2]) == 0)):
                                    lista.append(tupla)
                            if (len(nombre) == 4):
                                if ((string.lower(hola[0]).find(string.lower(nombre[0])) == 0)and(string.lower(hola[1]).find(string.lower(nombre[1])) == 0)and (string.lower(tupla[2]).find(nombre[2]) == 0)and(string.lower(tupla[3]).find(nombre[3]) == 0)):
                                    lista.append(tupla)
                    except AttributeError:
                        pass
            
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
        self.widgets.get_widget('statusbar1').push(3,'Buscar por nombre del papeletasitio...')
        self.statusbar.push(3,'Buscar por nombre del papeletasitio...')

    def leaveToogleName(self, widget, data=None):
        self.widgets.get_widget('statusbar1').pop(3)
        self.statusbar.pop(3)

    def clickInsertPapeletaSitio(self, data=None):
        self.widgets.get_widget('window2').show()
        self.widgets.get_widget('statusbar1').push(4,'Insertando papeleta de sitio de un cofrade...')
        self.statusbar.push(4,'Insertando papeleta de sitio de un cofrade...')
        self.cursor.execute('select max(id)+1 from '+ self.tabla +'')
        num = self.cursor.fetchone()
        num = list(num)
        if num[0] == None:
            num[0] = 1
        self.widgets.get_widget('entry1').set_text('')
        self.widgets.get_widget('entry2').set_text(str(num[0]))
        self.widgets.get_widget('entry3').set_text('')
        self.widgets.get_widget('entry10').set_text('')
        data = datetime.today().strftime("%d/%m/%Y")
        self.widgets.get_widget('entry6').set_text(data)
        
    def clickDeletePapeletaSitio(self, data=None):
        self.widgets.get_widget('statusbar1').push(5,'Eliminando papeleta de sitio de un cofrade...')
        self.statusbar.push(5,'Eliminando papeleta de sitio de un cofrade...')
        value = self.getSelection('borrar')

        if value:
            self.cursor.execute("select * from "+ self.tabla +" where n_orden = %s", value)
            tupla = self.cursor.fetchone()

            ident = str(tupla[1])
            treeview = self.widgets.get_widget('treeview1')
            treeselection = treeview.get_selection()
            (model, iteration) = treeselection.get_selected()
            n_orden = self.liststore.get_value(iteration, 1)

            dialog = self.widgets.get_widget('messagedialog2')
            dialog.format_secondary_text('Desea eliminar ('+ident+', '+n_orden+')')
            dialog.show()

    def clickModifyPapeletaSitio(self, data=None):
        self.widgets.get_widget('statusbar1').push(6,'Modificando papeleta de sitio de un cofrade...')
        self.statusbar.push(6,'Modificando papeleta de sitio de un cofrade...')
        value = self.getSelection('modificar')
        if value:
            self.cursor.execute("select * from "+ self.tabla +" where n_orden = %s", (value,))
            tupla = self.cursor.fetchone()
            ident = str(tupla[0])
            n_orden = str(tupla[3])
            fecha = str(tupla[2])

            fecha = self.normalizarFecha(fecha)

            self.widgets.get_widget('entry4').set_text(ident)
            self.widgets.get_widget('entry9').set_text(n_orden)
            self.widgets.get_widget('entry7').set_text(fecha)
           
            self.widgets.get_widget('window3').show()

    def dialogModifyPapeletaSitio(self, data=None):
        ident = self.widgets.get_widget('entry4').get_text()
        n_orden = self.widgets.get_widget('entry5').get_text()
        fecha = self.widgets.get_widget('entry7').get_text()
        dialog = self.widgets.get_widget('messagedialog3')
        dialog.format_secondary_text('¿Son correctos los cambios? ('+ident+', '+n_orden+', '+fecha+')')
        dialog.show()
    
    def acceptModifyPapeletaSitio(self, data=None):
        ident = self.widgets.get_widget('entry4').get_text()
        n_orden = self.widgets.get_widget('entry9').get_text()
        fecha = self.widgets.get_widget('entry7').get_text()
        
        if (str(fecha) == ''):
            self.error('Introduzca una fecha.')
            return False
        else:
            if (not re.match('(0?[1-9]|[12][0-9]|3[01])\/(0?[1-9]|1[012])\/[0-9]{4}', fecha)):
                self.error('Introduzca una fecha en un formato válido (dd/mm/aaaa).')
                return False

        fecha = self.ajustarFecha(fecha)
        
        if (n_orden!=''):
            try:
                self.cursor.execute("update "+ self.tabla +" set n_orden = %s, fecha = %s where id = %s", (n_orden, fecha, ident))
                self.actualizarId()
                self.cursor.execute('select s.n_orden, c.nombre, c.apellido1, c.apellido2, s.fecha from '+ self.tabla +' s, cofrades_datospersonales c where s.n_orden=c.n_orden order by s.n_orden asc')
                tuplas = self.cursor.fetchall()
                tuplas = self.normalizar(tuplas)
                self.fillData(tuplas)
                self.widgets.get_widget('window3').hide()
                self.insertPanel('OK','Modificación de la papeleta de sitio realizada correctamente')
            except MySQLdb.Error, e:
                self.error(e)
        else:
            self.error('El identificador debe de ser un número, o el n_orden está vacío.')
            
    def acceptDeletePapeletaSitio(self, data=None):
        value = self.getSelection('')
        if value:
            self.cursor.execute("delete from "+ self.tabla +" where n_orden = %s", value)
            self.actualizarId()
            self.cursor.execute('select s.n_orden, c.nombre, c.apellido1, c.apellido2, s.fecha from '+ self.tabla +' s, cofrades_datospersonales c where s.n_orden=c.n_orden order by s.n_orden asc')
            tuplas = self.cursor.fetchall()
            tuplas = self.normalizar(tuplas)
            self.fillData(tuplas)
            self.insertPanel('OK','Papeleta de Sitio de cofrade eliminada correctamente')
            
    def acceptNewPapeletaSitio(self, data=None):
        identificador = self.widgets.get_widget('entry2').get_text()
        n_orden = self.widgets.get_widget('entry10').get_text()
        fecha = self.widgets.get_widget('entry6').get_text()
        
        if (str(fecha) == ''):
            self.error('Introduzca una fecha.')
            return False
        else:
            if (not re.match('(0?[1-9]|[12][0-9]|3[01])\/(0?[1-9]|1[012])\/[0-9]{4}', fecha)):
                self.error('Introduzca una fecha en un formato vÃ¡lido (dd/mm/aaaa).')
                return False

        fecha = self.ajustarFecha(fecha)
        try:
            int(identificador)
            if(n_orden == ''):
                raise ValueError
            aux = [int(identificador), n_orden, fecha]
            try:
                
                self.cursor.execute('insert into '+ self.tabla +'(id, n_orden, fecha) values (%s, %s, %s)', aux)
                
                self.actualizarId()
                
                self.cursor.execute('select s.n_orden, c.nombre, c.apellido1, c.apellido2, s.fecha from '+ self.tabla +' s, cofrades_datospersonales c where s.n_orden=c.n_orden order by s.n_orden asc')
                tuplas = self.cursor.fetchall()
                tuplas = self.normalizar(tuplas)
                self.fillData(tuplas)
                self.hideWindow2()
                self.insertPanel('OK','Nueva Papeleta de Sitio creada correctamente')
            except MySQLdb.Error, e:
                self.error(e)
        except ValueError:
            self.error('El identificador debe de ser un número, o el n_orden está vacío.')

    def actualizarId(self):
        self.cursor.execute('select n_orden from '+ self.tabla + ' order by n_orden asc')
        tuplaux = self.cursor.fetchall()
        i = 1
        for tup in tuplaux:
            self.cursor.execute("update "+ self.tabla +" set id_cofrade = %s where n_orden = %s", (i, int(tup[0])))
            i+=1
                    
    def showCofrade(self, widget=None, event=None, data=None):
        if (event==1):
            aux = Cofrade(widget)
            aux.window.set_modal(True)
            aux.window.present()
        if (event==0):
            widget.set_text('')

    def ajustarFecha(self, fecha):
        day, month, year = fecha.split('/')

        fecha = year+'-'+month+'-'+day
        return fecha
            
    def searchCofrade(self, widget=None, event=None, data=None):
        n_orden = widget.get_text()
        self.cursor.execute('select nombre, apellido1, apellido2 from cofrades_datospersonales where n_orden=%s', (n_orden,))
        tupla = self.cursor.fetchone()
        if tupla:
            
            nombre = unicode(str.capitalize(tupla[0]), 'iso8859_15')
            aux = nombre.split(' ')
            for i in range(len(aux)):
                aux[i] = str.capitalize(str(aux[i]))
            nombre= ' '.join(aux)
            apellido1 = unicode(str.capitalize(tupla[1]), 'iso8859_15')
            apellido2 = unicode(str.capitalize(tupla[2]), 'iso8859_15')
            nombre = nombre.replace('Á','á')
            nombre = nombre.replace('É','é')
            nombre = nombre.replace('Í','í')
            nombre = nombre.replace('Ó','ó')
            nombre = nombre.replace('Ú','ú')
            nombre = nombre.replace('Ñ','ñ')
            apellido1 = apellido1.replace('Á','á')
            apellido1 = apellido1.replace('É','é')
            apellido1 = apellido1.replace('Í','í')
            apellido1 = apellido1.replace('Ó','ó')
            apellido1 = apellido1.replace('Ú','ú')
            apellido1 = apellido1.replace('Ñ','ñ')
            apellido2 = apellido2.replace('Á','á')
            apellido2 = apellido2.replace('É','é')
            apellido2 = apellido2.replace('Í','í')
            apellido2 = apellido2.replace('Ó','ó')
            apellido2 = apellido2.replace('Ú','ú')
            apellido2 = apellido2.replace('Ñ','ñ')
            nombre_completo = nombre+' '+apellido1+' '+apellido2
            
            self.widgets.get_widget('entry5').set_text(nombre_completo)
        else:
            self.widgets.get_widget('entry5').set_text('')

    def searchCofrade2(self, widget=None, event=None, data=None):
        n_orden = widget.get_text()
        self.cursor.execute('select nombre, apellido1, apellido2 from cofrades_datospersonales where n_orden=%s', n_orden)
        tupla = self.cursor.fetchone()
        if tupla:
            nombre = unicode(str.capitalize(tupla[0]), 'iso8859_15')
            aux = nombre.split(' ')
            for i in range(len(aux)):
                aux[i] = str.capitalize(str(aux[i]))
            nombre= ' '.join(aux)
            apellido1 = unicode(str.capitalize(tupla[1]), 'iso8859_15')
            apellido2 = unicode(str.capitalize(tupla[2]), 'iso8859_15')
            nombre = nombre.replace('Á','á')
            nombre = nombre.replace('É','é')
            nombre = nombre.replace('Í','í')
            nombre = nombre.replace('Ó','ó')
            nombre = nombre.replace('Ú','ú')
            nombre = nombre.replace('Ñ','ñ')
            apellido1 = apellido1.replace('Á','á')
            apellido1 = apellido1.replace('É','é')
            apellido1 = apellido1.replace('Í','í')
            apellido1 = apellido1.replace('Ó','ó')
            apellido1 = apellido1.replace('Ú','ú')
            apellido1 = apellido1.replace('Ñ','ñ')
            apellido2 = apellido2.replace('Á','á')
            apellido2 = apellido2.replace('É','é')
            apellido2 = apellido2.replace('Í','í')
            apellido2 = apellido2.replace('Ó','ó')
            apellido2 = apellido2.replace('Ú','ú')
            apellido2 = apellido2.replace('Ñ','ñ')
            nombre_completo = nombre+' '+apellido1+' '+apellido2
            
            self.widgets.get_widget('entry3').set_text(nombre_completo)
        else:
            self.widgets.get_widget('entry3').set_text('')

    def showCalendar(self, widget=None, event=None, data=None):
        if (event==0):
            widget.set_text('')
        else:
            fecha = datetime.today().strftime("%d/%m/%Y")
            day, month, year = fecha.split('/')
            self.widgets.get_widget('calendar1').select_month(int(month)-1, int(year))
            self.widgets.get_widget('calendar1').select_day(int(day))
            self.widgets.get_widget('dialog1').show()
            self.entryCalendar = widget

    def fillDate(self, data=None):
        self.hideCalendar(None)
        year, month, day = self.widgets.get_widget('calendar1').get_date()
        entry = self.entryCalendar
        month = month + 1
        if (len(str(month)) == 1):
            month = '0'+str(month)
        fecha = str(day)+'/'+str(month)+'/'+str(year)
        entry.set_text(fecha)

    def hideCalendar(self, widget, data=None): 
        self.widgets.get_widget('dialog1').hide()
        return True
            
    def getSelection(self, msg):
        treeview = self.widgets.get_widget('treeview1')
        treeselection = treeview.get_selection()
        (model, iteration) = treeselection.get_selected()
        try:
            value = self.liststore.get_value(iteration, 0)
            return value
        except TypeError:
            self.error('Seleccione el papeletasitio que desea '+msg)
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
        self.widgets.get_widget('statusbar1').pop(8)
        self.statusbar.pop(8)
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
        self.window.destroy()

    def color_row(self, column, cell, model, itera):
        cell.set_property("foreground",model.get_value(itera, 1))
       
    def doubleClick(self, widget, ident=None, data=None):
        self.cursor.execute('select n_orden from '+ self.tabla +' where id = %s', self.getSelection('insertar'))
        tupla = self.cursor.fetchone()
        if tupla:
            value = str(tupla[0])
            self.entry.set_text(value)
            self.destroy(None)
        
    def rightClick(self, widget, event=None):
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
    PapeletaSitio()
    gtk.gdk.threads_init()
    gtk.gdk.threads_enter()
    gtk.main()
    gtk.gdk.threads_leave()

if __name__ == "__main__":
    sys.exit(main())
