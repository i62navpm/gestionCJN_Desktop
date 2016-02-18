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

class Costalero():
    def __init__(self, entry=None, statusbar=None, panel=None):
        self.widgets = gtk.glade.XML('../costaleros/costaleros.glade')
        self.widgets.signal_autoconnect(self)

        self.caja = self.widgets.get_widget('vbox1')
        self.window = self.widgets.get_widget('window1')
        
        self.widgets.get_widget('notebook1').set_current_page(0)
        
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
        self.widgets.get_widget('statusbar1').push(1,'Busque al costalero')
        self.statusbar.push(1,'Busque al costalero')
        self.insertPanel('INFO','Abierta tabla de los coltaleros')
        
        button = self.widgets.get_widget('messagedialog2').add_button('Aceptar', 1)
        button.connect("clicked", self.acceptDeleteCostalero)
        
        button = self.widgets.get_widget('messagedialog3').add_button('Aceptar', 1)
        button.connect("clicked", self.acceptModifyCostalero)

        button = self.widgets.get_widget('messagedialog5').add_button('Aceptar', 1)
        button.connect("clicked", self.acceptDeleteAspirante)
        
        button = self.widgets.get_widget('messagedialog6').add_button('Aceptar', 1)
        button.connect("clicked", self.acceptModifyAspirante)
        
        button = self.widgets.get_widget('messagedialog7').add_button('Aceptar', 1)
        button.connect("clicked", self.acceptNewCostaleroFromAsp)
        
        self.liststore = None
        self.liststore2 = None
        self.cursor = self.conectar()
        self.insertColumn()
        self.insertColumn2()
        
        self.reservado = None
        
        self.cursor.execute('select s.sitio, c.nombre, c.apellido1, c.apellido2, s.fecha_titular, s.talla from costaleros_nueva s left join cofrades_datospersonales c on s.n_orden=c.n_orden where s.estado="Titular" order by s.sitio')
        tuplas = self.cursor.fetchall()
        tuplas = self.normalizar(tuplas)
        self.fillData(tuplas)

    def normalizar(self, tuplas):
        lista = list()
        for tupla in tuplas:
            tupla = list(tupla)
            lista.append(tupla)
        
        for aux in lista:
            
            try:
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
            except TypeError:
                aux[1] = ''
                aux[2] = ''
                aux[3] = ''
                
        return lista  


    def changePage(self, widget=None, event=None, data=None):
        num = widget.get_current_page()
        if num==1:
            self.widgets.get_widget('radiobutton1').set_property('sensitive', True)
            self.widgets.get_widget('entry1').set_text('')
            self.widgets.get_widget('entry1').connect('changed', self.search)
            self.cursor.execute('select s.sitio, c.nombre, c.apellido1, c.apellido2, s.fecha_titular, s.talla from costaleros_nueva s left join cofrades_datospersonales c on s.n_orden=c.n_orden where s.estado="Titular" order by s.sitio')
            tuplas = self.cursor.fetchall()
            tuplas = self.normalizar(tuplas)
            self.fillData(tuplas)
        else:
            self.widgets.get_widget('radiobutton1').set_property('sensitive', False)
            self.widgets.get_widget('entry1').connect('changed', self.search2)
            self.widgets.get_widget('entry1').set_text('')
            self.cursor.execute('select s.n_orden, c.nombre, c.apellido1, c.apellido2, s.fecha_aspirante, s.talla from costaleros_nueva s, cofrades_datospersonales c where s.n_orden=c.n_orden and s.estado="Aspirante" order by s.fecha_aspirante')
            tuplas = self.cursor.fetchall()
            tuplas = self.normalizar(tuplas)
            self.fillData2(tuplas)

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
        
        tvcolumn = gtk.TreeViewColumn('Sitio')
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

        tvcolumn = gtk.TreeViewColumn('Talla')
        treeview.append_column(tvcolumn)
        tvcolumn.pack_start(cell, True)
        tvcolumn.add_attribute(cell, 'text', 3)
        tvcolumn.set_sort_column_id(3)
        
        treeview.set_search_column(1)
        
        self.liststore = gtk.ListStore(str,str,str, str)
        treeview.set_model(self.liststore)

    def insertColumn2(self):
        treeview = self.widgets.get_widget('treeview2')
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

        tvcolumn = gtk.TreeViewColumn('Talla')
        treeview.append_column(tvcolumn)
        tvcolumn.pack_start(cell, True)
        tvcolumn.add_attribute(cell, 'text', 3)
        tvcolumn.set_sort_column_id(3)
        
        treeview.set_search_column(0)
        
        self.liststore2 = gtk.ListStore(int, str, str, str)
        treeview.set_model(self.liststore2)

    def fillData(self, tuplas):
        self.liststore.clear()
        for fila in tuplas:
            ident = fila[0]
            try:
                nombre = fila[1]+' '+fila[2]+' '+fila[3]
            except TypeError:
                nombre = ''
            posicion = fila[4]               
            if fila[4]:
                fecha = self.normalizarFecha(str(fila[4]))
            else:
                fecha = None
            
            if fila[5]:
                talla = fila[5]
            else:
                talla = None

            self.liststore.append([ident,nombre, fecha, talla])

    def fillData2(self, tuplas):
        self.liststore2.clear()
        for fila in tuplas:
            ident = fila[0]
            try:
                nombre = fila[1]+' '+fila[2]+' '+fila[3]
            except TypeError:
                nombre = ''
            posicion = fila[4]               
            if fila[4]:
                fecha = self.normalizarFecha(str(fila[4]))
            else:
                fecha = None
            
            if fila[5]:
                talla = fila[5]
            else:
                talla = None

            self.liststore2.append([ident, nombre, fecha, talla])

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

        self.cursor.execute('select s.sitio, c.nombre, c.apellido1, c.apellido2, s.fecha_titular, s.talla from costaleros_nueva s left join cofrades_datospersonales c on s.n_orden=c.n_orden where s.estado="Titular" order by s.sitio')
      
        tuplas = self.cursor.fetchall()

        if (data.get_text()==''):
            tuplas = self.normalizar(tuplas)
            self.fillData(tuplas)
        else:
            if (searchById.get_active() == True):
                lista = list()
                for tupla in tuplas:
                    texto = string.lower(data.get_text())
                    if (string.lower(tupla[0]).find(texto) == 0):
                        lista.append(tupla)
                self.fillData(lista)
            if (searchByName.get_active() == True):
                lista = list()
                tuplas = self.normalizar(tuplas)
                for tupla in tuplas:
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

    def search2(self, data=None):
        searchByName = self.widgets.get_widget('radiobutton2')

        self.cursor.execute('select s.n_orden, c.nombre, c.apellido1, c.apellido2, s.fecha_aspirante, s.talla from costaleros_nueva s, cofrades_datospersonales c where s.n_orden=c.n_orden and s.estado="Aspirante" order by s.fecha_aspirante')
      
        tuplas = self.cursor.fetchall()

        if (data.get_text()==''):
            tuplas = self.normalizar(tuplas)
            self.fillData2(tuplas)
        else:
            if (searchByName.get_active() == True):
                lista = list()
                tuplas = self.normalizar(tuplas)
                for tupla in tuplas:
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
                self.fillData2(lista)
            
    def clean(self, widget=None, event=None, data=None):
        self.widgets.get_widget('entry1').set_text('')
        
    def enterToogleId(self, widget, data=None):
        self.widgets.get_widget('statusbar1').push(2,'Buscar por sitio...')
        self.statusbar.push(2,'Buscar por sitio...')

    def leaveToogleId(self, widget, data=None):
        self.widgets.get_widget('statusbar1').pop(2)
        self.statusbar.pop(2)

    def enterToogleName(self, widget, data=None):
        self.widgets.get_widget('statusbar1').push(3,'Buscar por nombre del costalero...')
        self.statusbar.push(3,'Buscar por nombre deL costalero...')

    def leaveToogleName(self, widget, data=None):
        self.widgets.get_widget('statusbar1').pop(3)
        self.statusbar.pop(3)

    def clickInsertCostalero(self, data=None):
        self.widgets.get_widget('statusbar1').push(4,'Insertando costalero...')
        self.statusbar.push(4,'Insertando costalero...')

        self.cursor.execute('select count(*) from costaleros_nueva where n_orden is null and estado="Titular"')
        num = self.cursor.fetchone()
        num = int(num[0])
    
        if num!=0:
            self.widgets.get_widget('window2').show()
            combo = self.widgets.get_widget('combobox1')
            combo.set_active(-1)
            model = combo.get_model()
            model.clear()
                        
            self.cursor.execute('select sitio from costaleros_nueva where n_orden is null and estado="Titular"')
            tuplas = self.cursor.fetchall()
            for tupla in tuplas:
                combo.append_text(str(tupla[0]))
                
            self.widgets.get_widget('entry1').set_text('')
            self.widgets.get_widget('entry2').set_text('')
            self.widgets.get_widget('entry3').set_text('')
            self.widgets.get_widget('entry10').set_text('')
            data = datetime.today().strftime("%d/%m/%Y")
            self.widgets.get_widget('entry6').set_text(data)
            
        else:
            self.error('En este momento no existe ninguna sitio libre para añadir a un costalero.')
            return False

    def clickInsertAspirante(self, data=None):
        self.widgets.get_widget('statusbar1').push(4,'Insertando aspirante...')
        self.statusbar.push(4,'Insertando aspirante...')

        self.widgets.get_widget('window4').show()
                    
        self.widgets.get_widget('entry11').set_text('')
        self.widgets.get_widget('entry12').set_text('')
        data = datetime.today().strftime("%d/%m/%Y")
        self.widgets.get_widget('entry13').set_text(data)
        self.widgets.get_widget('entry14').set_text('')
            
    def clickDeleteCostalero(self, data=None):
        self.widgets.get_widget('statusbar1').push(5,'Eliminando costalero del sitio...')
        self.statusbar.push(5,'Eliminando costalero del sitio...')
        value = self.getSelection('borrar')

        if value:
            ident = value
            treeview = self.widgets.get_widget('treeview1')
            treeselection = treeview.get_selection()
            (model, iteration) = treeselection.get_selected()
            n_orden = self.liststore.get_value(iteration, 1)

            dialog = self.widgets.get_widget('messagedialog2')
            dialog.format_secondary_text('Desea eliminar ('+ident+', '+n_orden+')')
            dialog.show()

    def clickDeleteAspirante(self, data=None):
        self.widgets.get_widget('statusbar1').push(5,'Eliminando aspirante...')
        self.statusbar.push(5,'Eliminando aspirante...')
        value = self.getSelection2('borrar')

        if value:
            treeview = self.widgets.get_widget('treeview2')
            treeselection = treeview.get_selection()
            (model, iteration) = treeselection.get_selected()
            value = self.liststore2.get_value(iteration, 1)
            
            treeview = self.widgets.get_widget('treeview2')
            treeselection = treeview.get_selection()
            (model, iteration) = treeselection.get_selected()
            fecha = self.liststore2.get_value(iteration, 2)
            dialog = self.widgets.get_widget('messagedialog5')
            dialog.format_secondary_text('Desea eliminar ('+value+', '+fecha+')')
            dialog.show()

    def clickModifyCostalero(self, data=None):
        self.widgets.get_widget('statusbar1').push(6,'Modificando costalero de sitio...')
        self.statusbar.push(6,'Modificando costalero de sitio...')
        value = self.getSelection('modificar')
        if value:
            self.cursor.execute("select * from costaleros_nueva where sitio = %s", (value,))
            tupla = self.cursor.fetchone()
            sitio = str(tupla[0])
            
            if tupla[1] != None:
                n_orden = tupla[1]
            else:
                n_orden = ''
                
            if tupla[2] != None:
                talla = str(tupla[2])
            else:
                talla = ''
                
            if tupla[3] != None:
                fecha = str(tupla[3])
                fecha = self.normalizarFecha(fecha)
            else:
                fecha = ''
            
            self.widgets.get_widget('entry4').set_text(sitio)
            self.widgets.get_widget('entry9').set_text(str(n_orden))
            self.widgets.get_widget('entry7').set_text(fecha)
            self.widgets.get_widget('entry8').set_text(talla)
            self.widgets.get_widget('window3').show()

    def clickModifyAspirante(self, data=None):
        self.widgets.get_widget('statusbar1').push(6,'Modificando aspirante...')
        self.statusbar.push(6,'Modificando aspirante...')
        value = self.getSelection2('modificar')
        if value:
            self.cursor.execute("select * from costaleros_nueva where n_orden = %s", (value,))
            tupla = self.cursor.fetchone()
            
            if tupla[1] != None:
                n_orden = tupla[1]
            else:
                n_orden = ''
                
            if tupla[2] != None:
                talla = str(tupla[2])
            else:
                talla = ''
                
            if tupla[4] != None:
                fecha = str(tupla[4])
                fecha = self.normalizarFecha(fecha)
            else:
                fecha = ''
            
            self.widgets.get_widget('entry16').set_text(str(n_orden))
            self.widgets.get_widget('entry18').set_text(fecha)
            self.widgets.get_widget('entry19').set_text(talla)
            self.widgets.get_widget('window5').show()

    def dialogModifyCostalero(self, data=None):
        ident = self.widgets.get_widget('entry4').get_text()
        n_orden = self.widgets.get_widget('entry5').get_text()
        fecha = self.widgets.get_widget('entry7').get_text()
        talla = self.widgets.get_widget('entry8').get_text()
        dialog = self.widgets.get_widget('messagedialog3')
        dialog.format_secondary_text('¿Son correctos los cambios? ('+ident+', '+n_orden+', '+fecha+', '+talla+')')
        dialog.show()

    def dialogModifyAspirante(self, data=None):
        ident = self.widgets.get_widget('entry16').get_text()
        n_orden = self.widgets.get_widget('entry17').get_text()
        fecha = self.widgets.get_widget('entry18').get_text()
        talla = self.widgets.get_widget('entry19').get_text()
        dialog = self.widgets.get_widget('messagedialog6')
        dialog.format_secondary_text('¿Son correctos los cambios? ('+ident+', '+n_orden+', '+fecha+', '+talla+')')
        dialog.show()
    
    def acceptModifyCostalero(self, data=None):
        sitio = self.widgets.get_widget('entry4').get_text()
        n_orden = self.widgets.get_widget('entry9').get_text()
        fecha = self.widgets.get_widget('entry7').get_text()
        talla = self.widgets.get_widget('entry8').get_text()
        
        if (str(fecha) == ''):
            self.error('Introduzca una fecha.')
            return False
        else:
            if (not re.match('(0?[1-9]|[12][0-9]|3[01])\/(0?[1-9]|1[012])\/[0-9]{4}', fecha)):
                self.error('Introduzca una fecha en un formato vÃ¡lido (dd/mm/aaaa).')
                return False

        fecha = self.ajustarFecha(fecha)
        
        if talla != '':
            try:
                talla = float(talla)    
            except ValueError:
                self.error('La talla del costalero debe de ser un nÃºmero real (XX.XX).')
                return False
        else:
            talla = None 

        try:
            int(n_orden)
            if(n_orden == ''):
                raise ValueError
            estado = 1
            encontrado = False
            aux = [int(n_orden), talla, fecha, estado, sitio]
            
            self.reservado = aux
            
            self.cursor.execute('select n_orden from costaleros_nueva where estado="Aspirante"')
            tup = self.cursor.fetchall()
            
            for i in range(len(tup)):
                if(int(n_orden)==int(tup[i][0])):
                    encontrado = True
                    dialog = self.widgets.get_widget('messagedialog7')
                    dialog.format_secondary_text('El cofrade '+n_orden+' está en la lista de aspirantes.\n¿Desea eliminarlo de la lista de aspirantes e insertarlo en la de costaleros?')
                    dialog.show()
            if not encontrado:
                try:
                    self.cursor.execute('update costaleros_nueva set n_orden=%s, talla=%s, fecha_titular=%s, estado=%s where sitio = %s', aux)
                    
                    self.cursor.execute('select s.sitio, c.nombre, c.apellido1, c.apellido2, s.fecha_titular, s.talla from costaleros_nueva s left join cofrades_datospersonales c on s.n_orden=c.n_orden where s.estado="Titular" order by s.sitio')
                    tuplas = self.cursor.fetchall()
                    tuplas = self.normalizar(tuplas)
                    self.fillData(tuplas)
                    self.widgets.get_widget('window3').hide()
                    self.insertPanel('OK','Costalero modificado correctamente')
                except MySQLdb.Error, e:
                    self.error(e)
        except ValueError:
            self.error('Elija un cofrade para ocupar el sitio de costalero.')

    def acceptModifyAspirante(self, data=None):
        n_orden = self.widgets.get_widget('entry16').get_text()
        fecha = self.widgets.get_widget('entry18').get_text()
        talla = self.widgets.get_widget('entry19').get_text()
        
        if (str(fecha) == ''):
            self.error('Introduzca una fecha.')
            return False
        else:
            if (not re.match('(0?[1-9]|[12][0-9]|3[01])\/(0?[1-9]|1[012])\/[0-9]{4}', fecha)):
                self.error('Introduzca una fecha en un formato vÃ¡lido (dd/mm/aaaa).')
                return False

        fecha = self.ajustarFecha(fecha)
        
        if talla != '':
            try:
                talla = float(talla)    
            except ValueError:
                self.error('La talla del costalero debe de ser un nÃºmero real (XX.XX).')
                return False
        else:
            talla = None 

        if(n_orden == ''):
            raise ValueError

        estado = 2
        aux = [talla, fecha, estado, int(n_orden)]
        try:
            self.cursor.execute('update costaleros_nueva set talla=%s, fecha_aspirante=%s, estado=%s where n_orden=%s', aux)
            
            self.cursor.execute('select s.n_orden, c.nombre, c.apellido1, c.apellido2, s.fecha_aspirante, s.talla from costaleros_nueva s, cofrades_datospersonales c where s.n_orden=c.n_orden and s.estado="Aspirante" order by s.fecha_aspirante')
            tuplas = self.cursor.fetchall()
            tuplas = self.normalizar(tuplas)
            self.fillData2(tuplas)
            self.widgets.get_widget('window5').hide()
            self.insertPanel('OK','Aspirante modificado correctamente')
        except MySQLdb.Error, e:
            self.error(e)
            
    def acceptDeleteCostalero(self, data=None):
        value = self.getSelection('')
        if value:
            self.cursor.execute("update costaleros_nueva set n_orden=NULL, fecha_titular=NULL, talla=NULL where sitio=%s", value)
            
            self.cursor.execute('select s.sitio, c.nombre, c.apellido1, c.apellido2, s.fecha_titular, s.talla from costaleros_nueva s left join cofrades_datospersonales c on s.n_orden=c.n_orden where s.estado="Titular" order by s.sitio')
            tuplas = self.cursor.fetchall()
            tuplas = self.normalizar(tuplas)
            self.fillData(tuplas)
            self.insertPanel('OK','Eliminado correctamente al cofrade del sitio')

    def acceptDeleteAspirante(self, data=None):
        value = self.getSelection2('')
        print value

        if value:
            self.cursor.execute("delete from costaleros_nueva where n_orden = %s", value)
            
            self.cursor.execute('select s.n_orden, c.nombre, c.apellido1, c.apellido2, s.fecha_aspirante, s.talla from costaleros_nueva s, cofrades_datospersonales c where s.n_orden=c.n_orden and s.estado="Aspirante" order by s.fecha_aspirante')
            tuplas = self.cursor.fetchall()
            tuplas = self.normalizar(tuplas)
            self.fillData2(tuplas)
            
            self.insertPanel('OK','Eliminado correctamente al aspirante')
            
    def acceptNewCostalero(self, data=None):
        sitio = self.widgets.get_widget('combobox1').get_active_text()
        n_orden = self.widgets.get_widget('entry10').get_text()
        talla = self.widgets.get_widget('entry2').get_text()
        fecha = self.widgets.get_widget('entry6').get_text()
        estado = 1
        
        if (str(fecha) == ''):
            self.error('Introduzca una fecha.')
            return False
        else:
            if (not re.match('(0?[1-9]|[12][0-9]|3[01])\/(0?[1-9]|1[012])\/[0-9]{4}', fecha)):
                self.error('Introduzca una fecha en un formato válido (dd/mm/aaaa).')
                return False

        fecha = self.ajustarFecha(fecha)

        if sitio == None:
            self.error('Introduzca el sitio que el costalero debe ocupar.')
            return False

        if talla != '':
            try:
                talla = float(talla)    
            except ValueError:
                self.error('La talla del costalero debe de ser un número real (XX.XX).')
                return False
        else:
            talla = None 
        try:
            int(n_orden)
            if(n_orden == ''):
                raise ValueError
            encontrado = False
            aux = [int(n_orden), talla, fecha, estado, sitio]
            self.reservado = aux
            
            self.cursor.execute('select n_orden from costaleros_nueva where estado="Aspirante"')
            tup = self.cursor.fetchall()
            
            for i in range(len(tup)):
                if(int(n_orden)==int(tup[i][0])):
                    encontrado = True
                    dialog = self.widgets.get_widget('messagedialog7')
                    dialog.format_secondary_text('El cofrade '+n_orden+' está en la lista de aspirantes.\n¿Desea eliminarlo de la lista de aspirantes e insertarlo en la de costaleros?')
                    dialog.show()
            if not encontrado:
                try:
                    self.cursor.execute('update costaleros_nueva set n_orden=%s, talla=%s, fecha_titular=%s, estado=%s where sitio = %s', aux)
                    self.cursor.execute('select s.sitio, c.nombre, c.apellido1, c.apellido2, s.fecha_titular, s.talla from costaleros_nueva s left join cofrades_datospersonales c on s.n_orden=c.n_orden where s.estado="Titular" order by s.sitio')
                    tuplas = self.cursor.fetchall()
                    tuplas = self.normalizar(tuplas)
                    self.fillData(tuplas)
                    self.hideWindow2()
                    self.insertPanel('OK','Costalero creado correctamente')
                except MySQLdb.Error, e:
                    self.error(e)
        except ValueError:
            self.error('Elija un cofrade para ocupar el sitio de costalero.')
    
    def acceptNewCostaleroFromAsp(self, data=None):
        if self.reservado!=None:
            data = datetime.today().strftime("%Y-%m-%d")
            self.reservado[2] = data
            self.reservado[3] = 1
            self.cursor.execute('delete from costaleros_nueva where n_orden = %s', self.reservado[0])
            self.cursor.execute('update costaleros_nueva set n_orden=%s, talla=%s, fecha_titular=%s, estado=%s where sitio = %s', self.reservado)
            
            self.cursor.execute('select s.sitio, c.nombre, c.apellido1, c.apellido2, s.fecha_titular, s.talla from costaleros_nueva s left join cofrades_datospersonales c on s.n_orden=c.n_orden where s.estado="Titular" order by s.sitio')
            tuplas = self.cursor.fetchall()
            tuplas = self.normalizar(tuplas)
            self.fillData(tuplas)
            self.hideWindow2()
            self.widgets.get_widget('window3').hide()
            self.insertPanel('OK','Costalero creado correctamente')
            
    
    def acceptNewAspirante(self, data=None):
        n_orden = self.widgets.get_widget('entry11').get_text()
        talla = self.widgets.get_widget('entry14').get_text()
        fecha = self.widgets.get_widget('entry13').get_text()
        estado = 2
        
        if (str(fecha) == ''):
            self.error('Introduzca una fecha.')
            return False
        else:
            if (not re.match('(0?[1-9]|[12][0-9]|3[01])\/(0?[1-9]|1[012])\/[0-9]{4}', fecha)):
                self.error('Introduzca una fecha en un formato válido (dd/mm/aaaa).')
                return False

        fecha = self.ajustarFecha(fecha)

        if talla != '':
            try:
                talla = float(talla)    
            except ValueError:
                self.error('La talla del costalero debe de ser un número real (XX.XX).')
                return False
        else:
            talla = None 
        try:
            int(n_orden)
            if(n_orden == ''):
                raise ValueError
            
            aux = [int(n_orden), talla, fecha, estado]
            try:
                self.cursor.execute('insert into costaleros_nueva (n_orden, talla, fecha_aspirante, estado) values (%s, %s, %s, %s)', aux)
                
                self.cursor.execute('select s.n_orden, c.nombre, c.apellido1, c.apellido2, s.fecha_aspirante, s.talla from costaleros_nueva s, cofrades_datospersonales c where s.n_orden=c.n_orden and s.estado="Aspirante" order by s.fecha_aspirante')
                tuplas = self.cursor.fetchall()
                tuplas = self.normalizar(tuplas)
                self.fillData2(tuplas)
                self.hideWindow4()
                self.insertPanel('OK','Aspirante creado correctamente')
            except MySQLdb.Error, e:
                self.error(e)
        except ValueError:
            self.error('Elija un cofrade para ocupar el sitio de aspirante.')

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

    def searchAspirante(self, widget=None, event=None, data=None):
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
            
            self.widgets.get_widget('entry12').set_text(nombre_completo)
        else:
            self.widgets.get_widget('entry12').set_text('')

    def searchAspirante2(self, widget=None, event=None, data=None):
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
            
            self.widgets.get_widget('entry17').set_text(nombre_completo)
        else:
            self.widgets.get_widget('entry17').set_text('')

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
            self.error('Seleccione el costaleros que desea '+msg)
            return False

    def getSelection2(self, msg):
        treeview = self.widgets.get_widget('treeview2')
        treeselection = treeview.get_selection()
        (model, iteration) = treeselection.get_selected()
        try:
            value = self.liststore2.get_value(iteration, 0)
            return value
        except TypeError:
            self.error('Seleccione el costaleros que desea '+msg)
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

    def hideWindow4(self, data=None):
        self.widgets.get_widget('window4').hide()
        self.widgets.get_widget('statusbar1').pop(4)
        self.statusbar.pop(4)

    def hideWindow5(self, data=None):
        self.widgets.get_widget('window5').hide()
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
        self.cursor.execute('select n_orden from costaleros_nueva where n_orden = %s', (self.getSelection('insertar'),))
        tupla = self.cursor.fetchone()
        if tupla:
            value = str(tupla[0])
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

    def rightClick2(self, widget, event=None):
        treeview = self.widgets.get_widget('treeview2')
        context_menu = self.widgets.get_widget("menu3")
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
    Costalero()
    gtk.gdk.threads_init()
    gtk.gdk.threads_enter()
    gtk.main()
    gtk.gdk.threads_leave()

if __name__ == "__main__":
    sys.exit(main())
