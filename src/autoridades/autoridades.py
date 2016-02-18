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
from provincias.provincias import Provincia
from municipios.municipios import Municipio
from calles.calles import Calle
from bancos.bancos import Banco

class Autoridad():
    def __init__(self, entry=None, statusbar=None, panel=None):
        self.widgets = gtk.glade.XML('../autoridades/autoridades.glade')
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
        self.widgets.get_widget('statusbar1').push(1,'Busque una autoridad')
        self.statusbar.push(1,'Busque una autoridad')
        self.insertPanel('INFO','Abierta tabla de autoridades')
        
        button = self.widgets.get_widget('messagedialog2').add_button('Aceptar', 1)
        button.connect("clicked", self.clickConfimDelete)
        
        button = self.widgets.get_widget('messagedialog3').add_button('Aceptar', 1)
        button.connect("clicked", self.acceptModifyAutoridad)
        
        
        self.liststore = None
        
        self.cursor = self.conectar()
        self.insertColumn()
        
        self.cursor.execute('select id, nombre, apellido1, apellido2 from autoridades order by id')
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
        
        tvcolumn = gtk.TreeViewColumn('Ident.')
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
        
        self.liststore = gtk.ListStore(int, str)
        treeview.set_model(self.liststore)

    def fillData(self, tuplas):
        self.liststore.clear()
        for fila in tuplas:
            id = fila[0]
            n_cofrade = fila[1]
            try:
                nombre_completo = fila[1]+' '+fila[2]+' '+fila[3]
            except TypeError:
                nombre_completo = ' '
            self.liststore.append([id, nombre_completo])

    
    def search(self, data=None):
        searchByNAutoridad = self.widgets.get_widget('radiobutton4')
        searchByName = self.widgets.get_widget('radiobutton2')

        self.cursor.execute('select id, nombre, apellido1, apellido2 from autoridades order by id')
        tuplas = self.cursor.fetchall()
        tuplas = self.normalizar(tuplas)


        if (data.get_text()==''):
            
            self.fillData(tuplas)
        else:
            if (searchByNAutoridad.get_active() == True):
                lista = list()

                for tupla in tuplas:
                    if (str(tupla[0]).find(str(data.get_text())) == 0):
                        lista.append(tupla)
                
                self.fillData(lista)
            
            if (searchByName.get_active() == True):
                lista = list()
                for tupla in tuplas:
                    texto = string.lower(data.get_text())
                    nombre_completo = string.lower(tupla[1])+' '+string.lower(tupla[2])+' '+string.lower(tupla[3])
                    if nombre_completo.find(texto)==0:
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
    
    def clickInsertAutoridad(self, data=None):
        self.widgets.get_widget('window2').show()
        self.widgets.get_widget('statusbar1').push(4,'Insertando autoridad...')
        self.statusbar.push(4,'Insertando autoridad...')
        self.cursor.execute('select max(id)+1 from autoridades')
        num = self.cursor.fetchone()
        self.widgets.get_widget('entry1').set_text('')
        self.widgets.get_widget('entry3').set_text('')
        self.widgets.get_widget('entry8').set_text('')
        self.widgets.get_widget('entry9').set_text('')
        self.widgets.get_widget('entry10').set_text('')
        self.widgets.get_widget('entry11').set_text('')
        self.widgets.get_widget('entry12').set_text('')
        self.widgets.get_widget('entry13').set_text('')
        self.widgets.get_widget('entry14').set_text('')
        self.widgets.get_widget('entry15').set_text('')
        self.widgets.get_widget('entry16').set_text('')

        self.widgets.get_widget('entry19').set_text('')
        self.widgets.get_widget('entry20').set_text('')
        bufferaux = self.widgets.get_widget('textview1').get_buffer()
        bufferaux.set_text('')
        
        self.widgets.get_widget('entry2').set_text(str(num[0]))
        
        
    def clickDeleteAutoridad(self, data=None):
        self.widgets.get_widget('statusbar1').push(5,'Eliminando autoridad...')
        self.statusbar.push(5,'Eliminando autoridad...')
        value = self.getSelection('borrar')

        if value:
            self.cursor.execute("select id, nombre, apellido1, apellido2 from autoridades where id = %s", value)
            tupla = self.cursor.fetchone()
            ident = str(tupla[0])
            nombre = str.capitalize(tupla[1])+' '+str.capitalize(tupla[2])+' '+str.capitalize(tupla[3])

            dialog = self.widgets.get_widget('messagedialog2')
            dialog.format_secondary_text('Desea eliminar a la autoridad ('+ident+', '+unicode(nombre,'iso8859_15')+')')
            dialog.show()

    def clickModifyAutoridad(self, data=None):
        self.widgets.get_widget('statusbar1').push(6,'Modificando autoridad...')
        self.statusbar.push(6,'Modificando autoridad...')
        value = self.getSelection('modificar')

        if value:
            self.cursor.execute("select * from autoridades where id = %s", (value,))
            tupla = self.cursor.fetchone()
           
            tupla = list(tupla)
            
            for i in range(len(tupla)):
                if (tupla[i] == None):
                    tupla[i] = ''
            self.widgets.get_widget('entry4').set_text(str(tupla[0]))
            self.widgets.get_widget('entry25').set_text(str(tupla[1]))
            
            nombre = unicode(str.capitalize(tupla[2]), 'iso8859_15')
            aux = nombre.split(' ')
            for i in range(len(aux)):
                aux[i] = str.capitalize(str(aux[i]))
            nombre= ' '.join(aux)

            apellido1 = unicode(str.capitalize(tupla[3]), 'iso8859_15')
            apellido2 = unicode(str.capitalize(tupla[4]), 'iso8859_15')
            
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
            
            self.widgets.get_widget('entry22').set_text(nombre)
            self.widgets.get_widget('entry23').set_text(apellido1)
            self.widgets.get_widget('entry24').set_text(apellido2)
            
            self.widgets.get_widget('entry29').set_text(str(tupla[6]))
            self.widgets.get_widget('entry30').set_text(str(tupla[7]))
            self.widgets.get_widget('entry31').set_text(str(tupla[8]))
                            

            bufferaux = self.widgets.get_widget('textview2').get_buffer()
            
            bufferaux.set_text(str.capitalize(str(unicode(tupla[9], 'iso8859_15'))))
            self.widgets.get_widget('entry34').set_text(str(tupla[10]))
            self.widgets.get_widget('entry35').set_text(str(tupla[11]))
            self.widgets.get_widget('window3').show()
            self.cursor.execute('select p.nombre, m.municipio, c.nombre from provincias_nueva p, municipios m, calles_nueva c where c.poblacion=m.id and m.provincia=p.id and c.id=%s', (str(tupla[5]),))
            tupla = self.cursor.fetchone()
            self.widgets.get_widget('entry26').set_text(str(unicode(tupla[0], 'iso8859_15')))
            self.widgets.get_widget('entry27').set_text(str(unicode(tupla[1], 'iso8859_15')))
            self.widgets.get_widget('entry28').set_text(unicode(str.capitalize(tupla[2]), 'iso8859_15'))

            
            
    def clickShowAutoridad(self, data=None):
        self.widgets.get_widget('statusbar1').push(7,'Visualizando los datos de una autoridad...')
        self.statusbar.push(7,'Visualizando los datos de una autoridad...')
       
        value = self.getSelection('visualizar')
        self.cursor.execute("select * from autoridades where id = %s", (value,))
        tupla = self.cursor.fetchone()

        tupla = list(tupla)
        for i in range(len(tupla)):
            if (tupla[i] == None):
                tupla[i] = ''
        
        self.verDatosPersonales(tupla)

        self.cursor.execute('select * from cofrades_datosfinancieros where id=%s', (value,))
        tupla = self.cursor.fetchone()

    def verDatosPersonales(self, tupla):
        self.widgets.get_widget('entry56').set_text(str(tupla[0]))
        self.widgets.get_widget('entry62').set_text(str(tupla[1]))
        
        nombre = str(tupla[2])
        aux = nombre.split(' ')
        for i in range(len(aux)):
            aux[i] = str.capitalize(aux[i])
        nombre= ' '.join(aux)
        
        nombre = unicode(nombre,'iso8859_15')
        apellido1 = unicode(str.capitalize(tupla[3]),'iso8859_15')
        apellido2 = unicode(str.capitalize(tupla[4]),'iso8859_15')
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
        self.widgets.get_widget('entry59').set_text(nombre)
        self.widgets.get_widget('entry60').set_text(apellido1)
        self.widgets.get_widget('entry61').set_text(apellido2)
        
        self.widgets.get_widget('entry66').set_text(str(tupla[6]))
        self.widgets.get_widget('entry67').set_text(str(tupla[7]))
        self.widgets.get_widget('entry68').set_text(str(tupla[8]))

        bufferaux = self.widgets.get_widget('textview3').get_buffer()
        bufferaux.set_text(str.capitalize(str(unicode(tupla[9], 'iso8859_15'))))
        self.widgets.get_widget('entry71').set_text(str(tupla[10]))
        self.widgets.get_widget('entry72').set_text(unicode(str(tupla[11]), 'iso8859_15'))
                    
        self.cursor.execute('select p.nombre, m.municipio, c.nombre from provincias_nueva p, municipios m, calles_nueva c where c.poblacion=m.id and m.provincia=p.id and c.id=%s', str(tupla[5]))
        tupla = self.cursor.fetchone()
        self.widgets.get_widget('entry63').set_text(unicode(str(tupla[0]), 'iso8859_15'))
        self.widgets.get_widget('entry64').set_text(unicode(str(tupla[1]), 'iso8859_15'))
        self.widgets.get_widget('entry65').set_text(unicode(str.capitalize(tupla[2]), 'iso8859_15'))
        
        self.widgets.get_widget('window4').show()
            
    def dialogModifyAutoridad(self, data=None):
        dialog = self.widgets.get_widget('messagedialog3')
        dialog.format_secondary_text('¿Está seguro que desea modificar los datos dla autoridad?')
        dialog.show()
    
    def acceptModifyAutoridad(self, data=None):
        aux = self.verifyDataEntries2()

        if aux:
            try:
                self.cursor.execute("update autoridades set dni=%s, nombre=%s, apellido1=%s, apellido2=%s, id_direccion=%s, numero=%s, planta=%s, piso=%s, nota=%s, telefono=%s, email=%s where id=%s", aux)

                self.cursor.execute('select id, nombre, apellido1, apellido2 from autoridades order by id')
                tuplas = self.cursor.fetchall()
                tuplas = self.normalizar(tuplas)
                
                self.fillData(tuplas)
                self.widgets.get_widget('window3').hide()
                self.insertPanel('OK','Modificación de autoridad realizada correctamente')
            except MySQLdb.Error, e:
                self.error(e)

    def verifyDataEntries2(self):
        ident = self.widgets.get_widget('entry4').get_text()

        nombre = unicode(self.widgets.get_widget('entry22').get_text(), 'utf 8')
        apellido1 = unicode(self.widgets.get_widget('entry23').get_text(), 'utf 8')
        apellido2 = unicode(self.widgets.get_widget('entry24').get_text(), 'utf 8')
        dni = self.widgets.get_widget('entry25').get_text()

        calle = unicode(self.widgets.get_widget('entry28').get_text(), 'utf 8')
        numero = unicode(self.widgets.get_widget('entry29').get_text(), 'utf 8')
        planta = unicode(self.widgets.get_widget('entry30').get_text(), 'utf 8')
        piso = unicode(self.widgets.get_widget('entry31').get_text(), 'utf 8')
        telefono = self.widgets.get_widget('entry34').get_text()
        email = unicode(self.widgets.get_widget('entry35').get_text(), 'utf 8')
        bufferaux = self.widgets.get_widget('textview2').get_buffer()
        nota = unicode(bufferaux.get_text(bufferaux.get_start_iter(),bufferaux.get_end_iter()), 'utf 8')
        
        try:
            int(ident)
        except ValueError:
            self.error('El campo Identificador debe de ser un número entero.')
            return False
        
        if (str(nombre) == ''):
            self.error('El campo nombre no puede estar vacío')
            return False

        
        if (str(dni) == ''):
            dni = None
        else:
            if (not re.match('\d{8}-[a-zA-Z]', dni)):
                self.error('Introduzca el dni en un formato válido (XXXXXXXX-X).')
                return False
            
        if (str(calle) == ''):
            self.error('El campo calle no puede estar vacío')
            return False
        
        if (str(numero) == ''):
            numero = None
        if (str(planta) == ''):
            planta = None
        if (str(piso) == ''):
            piso = None
        
        if (str(telefono) == ''):
            telefono = None
        else:
            if (not re.match('^[69]{1}[0-9]{8}', telefono)):
                self.error('Introduzca un número de teléfono válido.')
                return False
        
        if (str(email) == ''):
            email = None
        else:
            if (not re.match('[\w-]{3,}@([\w-]{2,}.)*([\w-]{2,}.)[\w-]{2,4}', email)):
                self.error('Introduzca una dirección de correo válida.')
                return False
        
        if (str(nota) == ''):
            nota = None
        
        self.cursor.execute('select id from calles_nueva where nombre=%s', unicode(str.lower(str(calle)),'utf 8'))
        
        tupla = self.cursor.fetchone()
        calle = int(tupla[0])
        lista = [dni, nombre, apellido1, apellido2, calle, numero, planta, piso, nota, telefono, email, ident]
        return lista
        
    def clickConfimDelete(self, data=None):
        value = self.getSelection('')
        if value:
            self.cursor.execute("delete from autoridades where id = %s", value)
            self.cursor.execute('select id, nombre, apellido1, apellido2 from autoridades order by id')
            tuplas = self.cursor.fetchall()
            tuplas = self.normalizar(tuplas)
                
            self.fillData(tuplas)


        self.insertPanel('OK','Autoridad eliminado correctamente')

    def acceptNewAutoridad(self, data=None):
        aux = self.verifyDataEntries()

        if aux:
            try:
                self.cursor.execute('insert into autoridades values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', aux)
                
                self.cursor.execute('select id, nombre, apellido1, apellido2 from autoridades order by id')
                tuplas = self.cursor.fetchall()
                tuplas = self.normalizar(tuplas)
            
                
                self.fillData(tuplas)
                self.hideWindow2()
                self.widgets.get_widget('window2').hide()
                self.insertPanel('OK','Nuevo autoridad creada correctamente')
            except MySQLdb.Error, e:
                self.error(e)
    

    
    def allEntriesEmtpy(self):
        for aux in range(36,42):
            name = 'entry'+str(aux)
            if (self.widgets.get_widget(name).get_text() != ''):
                return False

        if (self.widgets.get_widget('entry88').get_text() != ''):
                return False
        if (self.widgets.get_widget('checkbutton13').get_active() == True):
            return False        
        if (self.widgets.get_widget('checkbutton1').get_active() == True):
            return 'no'
        return True

    def verifyDataEntries(self):
        ident = self.widgets.get_widget('entry2').get_text()

        nombre = unicode(self.widgets.get_widget('entry3').get_text(), 'utf 8')
        apellido1 = unicode(self.widgets.get_widget('entry8').get_text(), 'utf 8')
        apellido2 = unicode(self.widgets.get_widget('entry9').get_text(), 'utf 8')
        dni = self.widgets.get_widget('entry10').get_text()

        calle = unicode(self.widgets.get_widget('entry13').get_text(), 'utf 8')
        numero = unicode(self.widgets.get_widget('entry14').get_text(), 'utf 8')
        planta = unicode(self.widgets.get_widget('entry15').get_text(), 'utf 8')
        piso = unicode(self.widgets.get_widget('entry16').get_text(), 'utf 8')
        telefono = self.widgets.get_widget('entry19').get_text()
        email = unicode(self.widgets.get_widget('entry20').get_text(), 'utf 8')
        bufferaux = self.widgets.get_widget('textview1').get_buffer()
        nota = unicode(bufferaux.get_text(bufferaux.get_start_iter(),bufferaux.get_end_iter()), 'utf 8')
        
        try:
            int(ident)
        except ValueError:
            self.error('El campo Identificador debe de ser un número entero.')
            return False
        
        if (str(nombre) == ''):
            self.error('El campo nombre no puede estar vacío')
            return False
        
        if (str(dni) == ''):
            dni = None
        else:
            if (not re.match('\d{8}-[a-zA-Z]', dni)):
                self.error('Introduzca el dni en un formato válido (XXXXXXXX-X).')
                return False
        if (str(calle) == ''):
            self.error('El campo calle no puede estar vacío')
            return False
        
        if (str(numero) == ''):
            numero = None
        if (str(planta) == ''):
            planta = None
        if (str(piso) == ''):
            piso = None
        
        if (str(telefono) == ''):
            telefono = None
        else:
            if (not re.match('^[69]{1}[0-9]{8}', telefono)):
                self.error('Introduzca un número de teléfono válido.')
                return False
        
        if (str(email) == ''):
            email = None
        else:
            if (not re.match('[\w-]{3,}@([\w-]{2,}.)*([\w-]{2,}.)[\w-]{2,4}', email)):
                self.error('Introduzca una dirección de correo válida.')
                return False
        
        if (str(nota) == ''):
            nota = None
        
        self.cursor.execute('select id from calles_nueva where nombre=%s', unicode(str.lower(str(calle)),'utf 8'))

        tupla = self.cursor.fetchone()
        calle = int(tupla[0])
        lista = [ident, dni, nombre, apellido1, apellido2, calle, numero, planta, piso, nota, telefono, email]
        return lista

    def showProvincia(self, widget, event, data):
        if (event==0):
            widget.set_text('')
        else:
            aux = Provincia(widget)
            aux.window.set_modal(True)
            aux.window.present()
                
    def showMunicipio(self, widget, event, data):
        if (event==0):
            widget.set_text('')
        else:
            if (widget.get_name()=='entry12'):
                widget.set_text(self.widgets.get_widget('entry11').get_text())
            else:
                widget.set_text(self.widgets.get_widget('entry26').get_text())
            aux = Municipio(widget)
            aux.window.set_modal(True)
            aux.window.present()

    def showCalle(self, widget, event, data):
        if (event==0):
            widget.set_text('')
        else:
            if (widget.get_name()=='entry13'):
                widget.set_text(self.widgets.get_widget('entry12').get_text())
            else:
                widget.set_text(self.widgets.get_widget('entry27').get_text())
            aux = Calle(widget)
            aux.window.set_modal(True)
            aux.window.present()
    
    def getSelection(self, msg):
        treeview = self.widgets.get_widget('treeview1')
        treeselection = treeview.get_selection()
        (model, iteration) = treeselection.get_selected()
        try:
            value = self.liststore.get_value(iteration, 0)
            return value
        except TypeError:
            self.error('Seleccione la autoridad que desea '+msg)
            return False

    def error(self, msg):
        self.insertPanel('ERROR', msg)
        dialog = self.widgets.get_widget('messagedialog1')
        dialog.format_secondary_text(str(msg))
        dialog.show_all()

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
        self.widgets.get_widget('statusbar1').pop(7)
        self.statusbar.pop(7)

    def hideWindow5(self, data=None):
        self.widgets.get_widget('window5').hide()

    def hideWindow6(self, data=None):
        self.widgets.get_widget('window6').hide()

    def deleteWindow(self, widget, data=None):
        widget.hide()
        self.widgets.get_widget('statusbar1').pop(4)
        self.statusbar.pop(4)
        self.widgets.get_widget('statusbar1').pop(5)
        self.statusbar.pop(5)
        self.widgets.get_widget('statusbar1').pop(6)
        self.statusbar.pop(6)
        self.widgets.get_widget('statusbar1').pop(7)
        self.statusbar.pop(7)
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
        self.window.hide()

    def doubleClick(self, widget, ident=None, data=None):
        self.cursor.execute('select id from autoridades where id = %s', (self.getSelection('insertar'),))
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

    def rightClick2(self, widget, event=None):
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
    Autoridad()
    gtk.gdk.threads_init()
    gtk.gdk.threads_enter()
    gtk.main()
    gtk.gdk.threads_leave()

if __name__ == "__main__":
    sys.exit(main())
