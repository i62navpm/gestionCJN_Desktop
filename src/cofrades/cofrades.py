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


class Cofrade():
    def __init__(self, entry=None, statusbar=None, panel=None):
        self.widgets = gtk.glade.XML('../cofrades/cofrades.glade')
        self.widgets.signal_autoconnect(self)

        self.caja = self.widgets.get_widget('vbox1')
        self.window = self.widgets.get_widget('window1')

        self.widgets.get_widget('notebook4').set_current_page(0)
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

        self.filtrado = False
        self.filtrado2 = False
        f = open('../inicio/anio.txt', 'r')
        self.anio = f.read()
        f.close()

        self.window.connect("destroy", self.destroy)
        self.widgets.get_widget('statusbar1').push(1, 'Busque un cofrade')
        self.statusbar.push(1, 'Busque un cofrade')
        self.insertPanel('INFO', 'Abierta tabla de cofrades')

        button = self.widgets.get_widget('messagedialog2').add_button('Aceptar', 1)
        button.connect("clicked", self.clickConfimDelete)

        button = self.widgets.get_widget('messagedialog3').add_button('Aceptar', 1)
        button.connect("clicked", self.acceptModifyCofrade)

        self.dictbajas = {1: 'Voluntaria', 2: 'Fallecimiento', 3: 'Duplicidad', 4: 'Falta pago de 2 años'}

        self.liststore = None
        self.liststore2 = None

        treeview = self.widgets.get_widget('treeview3')
        treeview.set_model(gtk.ListStore(str))
        cell = gtk.CellRendererText()
        tvcolumn = gtk.TreeViewColumn('Deuda')
        treeview.append_column(tvcolumn)
        tvcolumn.pack_start(cell, True)
        tvcolumn.add_attribute(cell, 'text', 0)
        treeview.set_property('headers-visible', False)

        treeview = self.widgets.get_widget('treeview4')
        treeview.set_model(gtk.ListStore(str))
        cell = gtk.CellRendererText()
        tvcolumn = gtk.TreeViewColumn('Deuda')
        treeview.append_column(tvcolumn)
        tvcolumn.pack_start(cell, True)
        tvcolumn.add_attribute(cell, 'text', 0)
        treeview.set_property('headers-visible', False)

        self.cursor = self.conectar()
        self.insertColumn()
        self.insertColumn2()

        self.cursor.execute(
            'select n_orden,n_cofrade, nombre, apellido1, apellido2 from cofrades_datospersonales order by n_orden')
        tuplas = self.cursor.fetchall()
        tuplas = self.normalizar(tuplas)
        self.fillData(tuplas)

    def clickShowGasto(self, data=None):
        self.cursor.execute('select precio from gasto_domiciliar where id=0')
        tupla = self.cursor.fetchone()
        self.widgets.get_widget('entry98').set_text(str(tupla[0]))
        self.widgets.get_widget('window7').show_all()

    def clickShowGastoPostal(self, data=None):
        self.cursor.execute('select precio from gasto_enviopostal where id=0')
        tupla = self.cursor.fetchone()
        self.widgets.get_widget('entry99').set_text(str(tupla[0]))
        self.widgets.get_widget('window8').show_all()

    def cambia_loteriaNinio(self, data=None):
        spin1 = self.widgets.get_widget('spinbutton2').get_value()
        spin2 = self.widgets.get_widget('spinbutton4').get_value()
        if (spin1 != 0) or (spin2 != 0):
            self.widgets.get_widget('checkbutton17').set_active(False)
        if (spin1 == 0) and (spin2 == 0):
            self.widgets.get_widget('checkbutton17').set_active(True)

    def cambia_loteriaNavidad(self, data=None):
        spin1 = self.widgets.get_widget('spinbutton1').get_value()
        spin2 = self.widgets.get_widget('spinbutton3').get_value()
        if (spin1 != 0) or (spin2 != 0):
            self.widgets.get_widget('checkbutton16').set_active(False)
        if (spin1 == 0) and (spin2 == 0):
            self.widgets.get_widget('checkbutton16').set_active(True)

    def cambia_loteriaNinio2(self, data=None):
        spin1 = self.widgets.get_widget('spinbutton6').get_value()
        spin2 = self.widgets.get_widget('spinbutton8').get_value()
        if (spin1 != 0) or (spin2 != 0):
            self.widgets.get_widget('checkbutton21').set_active(False)
        if (spin1 == 0) and (spin2 == 0):
            self.widgets.get_widget('checkbutton21').set_active(True)

    def cambia_loteriaNavidad2(self, data=None):
        spin1 = self.widgets.get_widget('spinbutton5').get_value()
        spin2 = self.widgets.get_widget('spinbutton7').get_value()
        if (spin1 != 0) or (spin2 != 0):
            self.widgets.get_widget('checkbutton20').set_active(False)
        if (spin1 == 0) and (spin2 == 0):
            self.widgets.get_widget('checkbutton20').set_active(True)

    def normalizar(self, tuplas):
        lista = list()
        for tupla in tuplas:
            tupla = list(tupla)
            lista.append(tupla)

        for aux in lista:

            try:
                nombre = unicode(str.capitalize(aux[2]), 'iso8859_15')
                aux2 = nombre.split(' ')
                for i in range(len(aux2)):
                    aux2[i] = str.capitalize(str(aux2[i]))
                nombre = ' '.join(aux2)
                apellido1 = unicode(str.capitalize(aux[3]), 'iso8859_15')
                apellido2 = unicode(str.capitalize(aux[4]), 'iso8859_15')
                nombre = nombre.replace('Á', 'á')
                nombre = nombre.replace('É', 'é')
                nombre = nombre.replace('Í', 'í')
                nombre = nombre.replace('Ó', 'ó')
                nombre = nombre.replace('Ú', 'ú')
                nombre = nombre.replace('Ñ', 'ñ')
                apellido1 = apellido1.replace('Á', 'á')
                apellido1 = apellido1.replace('É', 'é')
                apellido1 = apellido1.replace('Í', 'í')
                apellido1 = apellido1.replace('Ó', 'ó')
                apellido1 = apellido1.replace('Ú', 'ú')
                apellido1 = apellido1.replace('Ñ', 'ñ')
                apellido2 = apellido2.replace('Á', 'á')
                apellido2 = apellido2.replace('É', 'é')
                apellido2 = apellido2.replace('Í', 'í')
                apellido2 = apellido2.replace('Ó', 'ó')
                apellido2 = apellido2.replace('Ú', 'ú')
                apellido2 = apellido2.replace('Ñ', 'ñ')

                aux[2] = nombre
                aux[3] = apellido1
                aux[4] = apellido2
            except TypeError:
                aux[2] = ''
                aux[3] = ''
                aux[4] = ''

        return lista

    def changePage(self, widget=None, event=None, data=None):
        num = widget.get_current_page()
        if num == 1:
            self.filtrado = False
            self.clearEntry(self.widgets.get_widget('entry94'), None)
            self.widgets.get_widget('entry1').set_text('')
            self.widgets.get_widget('entry1').connect('changed', self.search)
            self.widgets.get_widget('radiobutton1').set_property('sensitive', True)
            self.cursor.execute(
                'select n_orden,n_cofrade, nombre, apellido1, apellido2 from cofrades_datospersonales order by n_orden')
            tuplas = self.cursor.fetchall()
            tuplas = self.normalizar(tuplas)
            self.fillData(tuplas)
        else:
            self.filtrado2 = False
            self.clearEntry(self.widgets.get_widget('entry97'), None)
            self.widgets.get_widget('entry1').connect('changed', self.search2)
            self.widgets.get_widget('entry1').set_text('')
            self.widgets.get_widget('radiobutton1').set_property('sensitive', False)
            self.cursor.execute(
                'select n_orden, n_orden, nombre, apellido1, apellido2, motivo from cofrades_datospersonales_bajas order by n_orden')
            tuplas = self.cursor.fetchall()

            tuplas = self.normalizar(tuplas)

            self.fillData2(tuplas)

    def showRestaurar(self, data=None):
        self.widgets.get_widget('statusbar1').push(8, 'Restaurar un cofrade a la tabla de altas...')
        self.statusbar.push(8, 'Restaurar un cofrade a la tabla de altas...')
        value = self.getSelection2('restaurar')
        if value:
            self.widgets.get_widget('messagedialog4').show()

    def clickRestaurar(self, widget=None, data=None):
        self.widgets.get_widget('statusbar1').pop(8)
        self.statusbar.pop(8)
        if data == -6:
            self.deleteWindow(widget)
        else:
            self.restaurarCofrade()

    def restaurarCofrade(self):
        value = self.getSelection2(None)
        self.widgets.get_widget('messagedialog4').hide()

        self.cursor.execute('select * from cofrades_datospersonales_bajas where n_orden = %s', (value,))
        tupla = self.cursor.fetchone()
        tupla = list(tupla)
        tupla.pop()
        tupla.pop()

        self.cursor.execute('select max(id)+1, min(n_cofrade) from cofrades_datospersonales where n_orden>%s', (value,))
        tupla2 = self.cursor.fetchone()
        tupla[0] = int(tupla2[0])
        ncofrade = int(tupla2[1])

        tupla.insert(2, ncofrade)

        self.cursor.execute('update cofrades_datospersonales set n_cofrade=n_cofrade+1 where n_cofrade >= %s',
                            tupla2[1])
        self.cursor.execute('update cofrades_datosfinancieros set id_cofrade=id_cofrade+1 where id_cofrade >= %s',
                            tupla2[1])
        self.cursor.execute('update cofrades_loteria set id_cofrade=id_cofrade+1 where id_cofrade >= %s', tupla2[1])

        self.cursor.execute('update cofrades_loteria set id_cofrade = %s where n_orden = %s', (tupla[0], tupla[1]))
        self.cursor.execute('update cofrades_datosfinancieros set id_cofrade = %s where n_orden = %s',
                            (tupla[0], tupla[1]))
        self.cursor.execute(
            'insert into cofrades_datospersonales values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', tupla)
        self.cursor.execute('delete from cofrades_datospersonales_bajas where n_orden = %s', (value,))

        if not self.filtrado2:
            self.cursor.execute(
                'select n_orden, n_orden, nombre, apellido1, apellido2, motivo from cofrades_datospersonales_bajas order by n_orden')
            tuplas = self.cursor.fetchall()
            tuplas = self.normalizar(tuplas)
        else:
            tuplas = self.changeEntry2(self.widgets.get_widget('entry97'), None)

        self.fillData2(tuplas)

    def showFiltrado(self, data=None):
        self.widgets.get_widget('checkbutton2').set_active(False)
        self.widgets.get_widget('checkbutton4').set_active(False)
        self.widgets.get_widget('entry95').set_text('')
        self.widgets.get_widget('entry96').set_text('')
        self.widgets.get_widget('window6').show()

    def setEntry(self, data=None):
        if data.get_name() == 'entry95':
            check = self.widgets.get_widget('checkbutton2')
            self.cursor.execute('select distinct apellido1 from cofrades_datospersonales')
            tuplas = self.cursor.fetchall()
        else:
            check = self.widgets.get_widget('checkbutton4')
            self.cursor.execute('select distinct apellido2 from cofrades_datospersonales')
            tuplas = self.cursor.fetchall()

        if (check.get_active()):
            data.set_property('sensitive', True)
        else:
            data.set_property('sensitive', False)

        completion = gtk.EntryCompletion()
        liststore = gtk.ListStore(str)

        for tupla in tuplas:
            apellido = unicode(str.capitalize(tupla[0]), 'iso8859_15')
            apellido = apellido.replace('Á', 'á')
            apellido = apellido.replace('É', 'é')
            apellido = apellido.replace('Í', 'í')
            apellido = apellido.replace('Ó', 'ó')
            apellido = apellido.replace('Ú', 'ú')
            apellido = apellido.replace('Ñ', 'ñ')
            liststore.append([apellido])
        completion.set_model(liststore)
        data.set_completion(completion)
        completion.set_text_column(0)

    def acceptFilter(self, data=None):
        num = self.widgets.get_widget('notebook4').get_current_page()

        entry1 = self.widgets.get_widget('entry95')
        entry2 = self.widgets.get_widget('entry96')
        if num == 0:
            entry3 = self.widgets.get_widget('entry94')
        else:
            entry3 = self.widgets.get_widget('entry97')

        if entry1.get_property('sensitive'):
            apellido1 = entry1.get_text()
        else:
            apellido1 = ' '
        if entry2.get_property('sensitive'):
            apellido2 = entry2.get_text()
        else:
            apellido2 = ' '

        cadena = apellido1 + ' - ' + apellido2

        if cadena != '':
            entry3.set_text(cadena)
        else:
            self.clearEntry(entry3, None)

    def changeEntry(self, data=None, color=None):
        self.widgets.get_widget('statusbar1').pop(7)
        self.statusbar.pop(7)

        texto = data.get_text()
        apellidos = texto.split(' - ')

        # cambiar color de fondo de entry
        if (color == None):
            color = "#FFFF00"
        data.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse(color))

        for i in range(len(apellidos)):
            apellidos[i] = unicode(string.upper(apellidos[i]), 'utf 8')

        if (apellidos == ['']):
            self.cursor.execute(
                'select n_orden,n_cofrade, nombre, apellido1, apellido2 from cofrades_datospersonales order by n_orden')
            self.filtrado = False
        else:

            if apellidos[1] == ' ':
                self.cursor.execute(
                    'select n_orden, n_cofrade,nombre, apellido1, apellido2 from cofrades_datospersonales where apellido1 = %s order by n_orden',
                    (apellidos[0],))
            if apellidos[0] == ' ':
                self.cursor.execute(
                    'select n_orden, n_cofrade,nombre, apellido1, apellido2 from cofrades_datospersonales where apellido2 = %s order by n_orden',
                    (apellidos[1],))
            if apellidos[0] != ' ' and apellidos[1] != ' ':
                self.cursor.execute(
                    'select n_orden, n_cofrade,nombre, apellido1, apellido2 from cofrades_datospersonales where apellido1 = %s and apellido2 = %s order by n_orden',
                    apellidos)
            self.filtrado = True

        tuplas = self.cursor.fetchall()
        tuplas = self.normalizar(tuplas)
        self.fillData(tuplas)

        return tuplas

    def changeEntry2(self, data=None, color=None):
        self.widgets.get_widget('statusbar1').pop(7)
        self.statusbar.pop(7)

        texto = data.get_text()
        apellidos = texto.split(' - ')

        # cambiar color de fondo de entry
        if (color == None):
            color = "#FFFF00"
        data.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse(color))

        for i in range(len(apellidos)):
            apellidos[i] = unicode(string.upper(apellidos[i]), 'utf 8')

        if (apellidos == ['']):
            self.cursor.execute(
                'select n_orden, n_orden, nombre, apellido1, apellido2, motivo from cofrades_datospersonales_bajas order by n_orden')
            self.filtrado2 = False
        else:
            if apellidos[1] == ' ':
                self.cursor.execute(
                    'select n_orden,n_orden, nombre, apellido1, apellido2, motivo from cofrades_datospersonales_bajas where apellido1 = %s order by n_orden',
                    apellidos[0])
            if apellidos[0] == ' ':
                self.cursor.execute(
                    'select n_orden,n_orden, nombre, apellido1, apellido2, motivo from cofrades_datospersonales_bajas where apellido2 = %s order by n_orden',
                    apellidos[1])
            if apellidos[0] != ' ' and apellidos[1] != ' ':
                self.cursor.execute(
                    'select n_orden,n_orden, nombre, apellido1, apellido2, motivo from cofrades_datospersonales_bajas where apellido1 = %s and apellido2 = %s order by n_orden',
                    apellidos)
            self.filtrado2 = True

        tuplas = self.cursor.fetchall()
        tuplas = self.normalizar(tuplas)
        self.fillData2(tuplas)

        return tuplas

    def clearEntry(self, widget, event, data=None):
        widget.set_text('')
        self.changeEntry(widget, '#FFFFFF')

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
                msg = msg.replace('\n', '')
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

        tvcolumn = gtk.TreeViewColumn('N. Cofrade')
        treeview.append_column(tvcolumn)
        tvcolumn.pack_start(cell, True)
        tvcolumn.add_attribute(cell, 'text', 1)
        tvcolumn.set_sort_column_id(1)

        tvcolumn = gtk.TreeViewColumn('Nombre')
        treeview.append_column(tvcolumn)
        tvcolumn.pack_start(cell, True)
        tvcolumn.add_attribute(cell, 'text', 2)
        tvcolumn.set_sort_column_id(2)
        treeview.set_search_column(2)

        self.liststore = gtk.ListStore(int, int, str)
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

        tvcolumn = gtk.TreeViewColumn('Motivo Baja')
        treeview.append_column(tvcolumn)
        tvcolumn.pack_start(cell, True)
        tvcolumn.add_attribute(cell, 'text', 2)
        tvcolumn.set_sort_column_id(2)

        treeview.set_search_column(1)

        self.liststore2 = gtk.ListStore(int, str, str)
        treeview.set_model(self.liststore2)

    def fillData(self, tuplas):
        self.liststore.clear()
        for fila in tuplas:
            n_orden = fila[0]
            n_cofrade = fila[1]
            try:
                nombre_completo = fila[2] + ' ' + fila[3] + ' ' + fila[4]
            except TypeError:
                nombre_completo = ' '
            self.liststore.append([n_orden, n_cofrade, nombre_completo])

    def fillData2(self, tuplas):
        self.liststore2.clear()

        for fila in tuplas:
            n_orden = fila[0]
            motivo = fila[5]
            try:
                nombre_completo = fila[2] + ' ' + fila[3] + ' ' + fila[4]
            except TypeError:
                nombre_completo = ' '
            self.liststore2.append([n_orden, nombre_completo, self.dictbajas[motivo]])

    def search(self, data=None):
        searchByNOrden = self.widgets.get_widget('radiobutton4')
        searchByNCofrade = self.widgets.get_widget('radiobutton1')
        searchByName = self.widgets.get_widget('radiobutton2')
        if not self.filtrado:
            self.cursor.execute(
                'select n_orden,n_cofrade, nombre, apellido1, apellido2 from cofrades_datospersonales order by n_orden')
            tuplas = self.cursor.fetchall()
            tuplas = self.normalizar(tuplas)
        else:
            tuplas = self.changeEntry(self.widgets.get_widget('entry94'), None)

        if (data.get_text() == ''):

            self.fillData(tuplas)
        else:
            if (searchByNOrden.get_active() == True):
                lista = list()

                for tupla in tuplas:
                    if (str(tupla[0]).find(str(data.get_text())) == 0):
                        lista.append(tupla)

                self.fillData(lista)

            if (searchByNCofrade.get_active() == True):
                lista = list()

                for tupla in tuplas:
                    if (str(tupla[1]).find(str(data.get_text())) == 0):
                        lista.append(tupla)

                self.fillData(lista)

            if (searchByName.get_active() == True):
                lista = list()
                for tupla in tuplas:
                    texto = string.lower(data.get_text())
                    nombre_completo = string.lower(tupla[2]) + ' ' + string.lower(tupla[3]) + ' ' + string.lower(
                        tupla[4])
                    if nombre_completo.find(texto) == 0:
                        lista.append(tupla)
                self.fillData(lista)

    def search2(self, data=None):
        searchByNOrden = self.widgets.get_widget('radiobutton4')
        searchByName = self.widgets.get_widget('radiobutton2')

        if not self.filtrado2:
            self.cursor.execute(
                'select n_orden, n_orden, nombre, apellido1, apellido2, motivo from cofrades_datospersonales_bajas order by n_orden')
            tuplas = self.cursor.fetchall()
            tuplas = self.normalizar(tuplas)
        else:
            tuplas = self.changeEntry2(self.widgets.get_widget('entry97'), None)

        if (data.get_text() == ''):
            self.fillData2(tuplas)
        else:
            if (searchByNOrden.get_active() == True):
                lista = list()
                for tupla in tuplas:
                    if (str(tupla[0]).find(str(data.get_text())) == 0):
                        lista.append(tupla)
                self.fillData2(lista)

            if (searchByName.get_active() == True):
                lista = list()
                for tupla in tuplas:
                    texto = string.lower(data.get_text())
                    nombre_completo = string.lower(tupla[2]) + ' ' + string.lower(tupla[3]) + ' ' + string.lower(
                        tupla[4])
                    if nombre_completo.find(texto) == 0:
                        lista.append(tupla)
                self.fillData2(lista)

    def clean(self, widget=None, event=None, data=None):
        self.widgets.get_widget('entry1').set_text('')

    def enterToogleId(self, widget, data=None):
        self.widgets.get_widget('statusbar1').push(2, 'Buscar por id...')
        self.statusbar.push(2, 'Buscar por id...')

    def leaveToogleId(self, widget, data=None):
        self.widgets.get_widget('statusbar1').pop(2)
        self.statusbar.pop(2)

    def enterToogleName(self, widget, data=None):
        self.widgets.get_widget('statusbar1').push(3, 'Buscar por nombre...')
        self.statusbar.push(3, 'Buscar por nombre...')

    def leaveToogleName(self, widget, data=None):
        self.widgets.get_widget('statusbar1').pop(3)
        self.statusbar.pop(3)

    def clickInsertCofrade(self, data=None):
        self.widgets.get_widget('window2').show()
        self.widgets.get_widget('statusbar1').push(4, 'Insertando cofrade...')
        self.statusbar.push(4, 'Insertando cofrade...')
        self.cursor.execute('select max(id)+1, max(n_orden)+1, max(n_cofrade)+1 from cofrades_datospersonales')
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
        self.widgets.get_widget('entry17').set_text('')
        data = datetime.today().strftime("%d/%m/%Y")
        self.widgets.get_widget('entry18').set_text(data)
        self.widgets.get_widget('entry19').set_text('')
        self.widgets.get_widget('entry20').set_text('')
        bufferaux = self.widgets.get_widget('textview1').get_buffer()
        bufferaux.set_text('')

        self.widgets.get_widget('entry2').set_text(str(num[0]))
        self.widgets.get_widget('entry6').set_text(str(num[1]))
        self.widgets.get_widget('entry7').set_text(str(num[2]))

        self.widgets.get_widget('entry36').set_text('')
        self.widgets.get_widget('entry37').set_text('')
        self.widgets.get_widget('entry38').set_text('')
        self.widgets.get_widget('entry39').set_text('')
        self.widgets.get_widget('entry40').set_text('')
        self.widgets.get_widget('entry41').set_text('')
        self.widgets.get_widget('checkbutton1').set_active(False)

        self.widgets.get_widget('spinbutton1').set_value(0)
        self.widgets.get_widget('spinbutton2').set_value(0)
        self.widgets.get_widget('spinbutton3').set_value(0)
        self.widgets.get_widget('spinbutton4').set_value(0)

        self.widgets.get_widget('entry88').set_text('')
        self.widgets.get_widget('checkbutton13').set_active(False)

        self.widgets.get_widget('checkbutton10').set_active(False)
        self.widgets.get_widget('checkbutton16').set_active(True)
        self.widgets.get_widget('checkbutton17').set_active(True)

        self.widgets.get_widget('notebook1').set_current_page(0)

    def showCalendar(self, widget=None, event=None, data=None):
        if (event == 0):
            widget.set_text('')
        else:
            fecha = datetime.today().strftime("%d/%m/%Y")
            day, month, year = fecha.split('/')
            self.widgets.get_widget('calendar1').select_month(int(month) - 1, int(year))
            self.widgets.get_widget('calendar1').select_day(int(day))
            self.widgets.get_widget('dialog1').present()
            self.entryCalendar = widget

    def fillDate(self, data=None):
        self.hideCalendar(None)
        year, month, day = self.widgets.get_widget('calendar1').get_date()
        entry = self.entryCalendar
        month = month + 1
        if (len(str(month)) == 1):
            month = '0' + str(month)
        fecha = str(day) + '/' + str(month) + '/' + str(year)
        entry.set_text(fecha)

    def clickDeleteCofrade(self, data=None):
        self.widgets.get_widget('statusbar1').push(5, 'Eliminando cofrade...')
        self.statusbar.push(5, 'Eliminando cofrade...')
        value = self.getSelection('borrar')

        if value:
            self.cursor.execute(
                "select id, nombre, apellido1, apellido2 from cofrades_datospersonales where n_orden = %s", (value,))
            tupla = self.cursor.fetchone()
            ident = str(tupla[0])
            nombre = str.capitalize(tupla[1]) + ' ' + str.capitalize(tupla[2]) + ' ' + str.capitalize(tupla[3])

            dialog = self.widgets.get_widget('messagedialog2')
            dialog.format_secondary_text(
                'Desea eliminar al cofrade (' + ident + ', ' + unicode(nombre, 'iso8859_15') + ')')
            dialog.show()

    def clickModifyCofrade(self, data=None):
        self.widgets.get_widget('statusbar1').push(6, 'Modificando cofrade...')
        self.statusbar.push(6, 'Modificando cofrade...')
        value = self.getSelection('modificar')
        self.widgets.get_widget('notebook2').set_current_page(0)
        if value:
            self.cursor.execute("select * from cofrades_datospersonales where n_orden = %s", (value,))
            tupla = self.cursor.fetchone()

            tupla = list(tupla)

            for i in range(len(tupla)):
                if (tupla[i] == None):
                    tupla[i] = ''
            n_orden = int(tupla[1])
            self.widgets.get_widget('entry4').set_text(str(tupla[0]))
            self.widgets.get_widget('entry5').set_text(str(tupla[1]))
            self.widgets.get_widget('entry21').set_text(str(tupla[2]))
            self.widgets.get_widget('entry25').set_text(str(tupla[3]))

            nombre = unicode(str.capitalize(tupla[4]), 'iso8859_15')
            aux = nombre.split(' ')
            for i in range(len(aux)):
                aux[i] = str.capitalize(str(aux[i]))
            nombre = ' '.join(aux)

            apellido1 = unicode(str.capitalize(tupla[5]), 'iso8859_15')
            apellido2 = unicode(str.capitalize(tupla[6]), 'iso8859_15')

            nombre = nombre.replace('Á', 'á')
            nombre = nombre.replace('É', 'é')
            nombre = nombre.replace('Í', 'í')
            nombre = nombre.replace('Ó', 'ó')
            nombre = nombre.replace('Ú', 'ú')
            nombre = nombre.replace('Ñ', 'ñ')
            apellido1 = apellido1.replace('Á', 'á')
            apellido1 = apellido1.replace('É', 'é')
            apellido1 = apellido1.replace('Í', 'í')
            apellido1 = apellido1.replace('Ó', 'ó')
            apellido1 = apellido1.replace('Ú', 'ú')
            apellido1 = apellido1.replace('Ñ', 'ñ')
            apellido2 = apellido2.replace('Á', 'á')
            apellido2 = apellido2.replace('É', 'é')
            apellido2 = apellido2.replace('Í', 'í')
            apellido2 = apellido2.replace('Ó', 'ó')
            apellido2 = apellido2.replace('Ú', 'ú')
            apellido2 = apellido2.replace('Ñ', 'ñ')

            self.widgets.get_widget('entry22').set_text(nombre)
            self.widgets.get_widget('entry23').set_text(apellido1)
            self.widgets.get_widget('entry24').set_text(apellido2)
            if (str.lower(tupla[7]) == 'hombre'):
                self.widgets.get_widget('radiobutton8').set_active(True)
            else:
                self.widgets.get_widget('radiobutton9').set_active(True)

            self.widgets.get_widget('entry29').set_text(unicode(str(tupla[9]), 'iso8859_15'))
            self.widgets.get_widget('entry30').set_text(unicode(str(tupla[10]), 'iso8859_15'))
            self.widgets.get_widget('entry31').set_text(unicode(str(tupla[11]), 'iso8859_15'))

            fecha = self.normalizarFecha(str(tupla[12]))
            self.widgets.get_widget('entry32').set_text(fecha)
            fecha = self.normalizarFecha(str(tupla[13]))
            self.widgets.get_widget('entry33').set_text(fecha)
            bufferaux = self.widgets.get_widget('textview2').get_buffer()

            bufferaux.set_text(str.capitalize(str(unicode(tupla[14], 'iso8859_15'))))
            self.widgets.get_widget('entry34').set_text(str(tupla[15]))
            self.widgets.get_widget('entry35').set_text(str(tupla[16]))
            self.widgets.get_widget('window3').show()
            self.cursor.execute(
                'select p.nombre, m.municipio, c.nombre from provincias_nueva p, municipios m, calles_nueva c where c.poblacion=m.id and m.provincia=p.id and c.id=%s',
                (str(tupla[8]),))
            tupla = self.cursor.fetchone()
            self.widgets.get_widget('entry26').set_text(str(unicode(tupla[0], 'iso8859_15')))
            self.widgets.get_widget('entry27').set_text(str(unicode(tupla[1], 'iso8859_15')))
            self.widgets.get_widget('entry28').set_text(unicode(str.capitalize(tupla[2]), 'iso8859_15'))

            self.cursor.execute('select * from cofrades_datosfinancieros where n_orden=%s', (value,))
            tupla = self.cursor.fetchone()

            self.cursor.execute('select * from morosos where n_orden = %s and anio=%s', (n_orden, self.anio));
            aux = self.cursor.fetchone()
            if aux:
                self.widgets.get_widget('checkbutton3').set_active(True)
            else:
                self.widgets.get_widget('checkbutton3').set_active(False)

            if tupla:

                if (tupla[2] == None):
                    self.widgets.get_widget('entry42').set_text('')
                else:
                    self.widgets.get_widget('entry42').set_text(str(tupla[2]).zfill(4))
                if (tupla[3] == None):
                    self.widgets.get_widget('entry43').set_text('')
                else:
                    self.widgets.get_widget('entry43').set_text(str(tupla[3]).zfill(4))
                if (tupla[4] == None):
                    self.widgets.get_widget('entry44').set_text('')
                else:
                    self.widgets.get_widget('entry44').set_text(str(tupla[4]).zfill(2))
                if (tupla[5] == None):
                    self.widgets.get_widget('entry45').set_text('')
                else:
                    self.widgets.get_widget('entry45').set_text(str(tupla[5]).zfill(10))
                if (tupla[6] == None):
                    self.widgets.get_widget('entry47').set_text('')
                else:
                    self.cursor.execute('select nombre from bancos where id=%s', (int(tupla[6]),))
                    tupla2 = self.cursor.fetchone()
                    self.widgets.get_widget('entry47').set_text(unicode(str(tupla2[0]), 'iso8859-15'))
                if (tupla[7] == None):
                    self.widgets.get_widget('entry46').set_text('')
                else:
                    self.widgets.get_widget('entry46').set_text(str(tupla[7]))

                if (tupla[8] == None):
                    self.widgets.get_widget('entry89').set_text('')
                else:
                    self.widgets.get_widget('entry89').set_text(str(tupla[8]))
                if (tupla[9] == 'True'):
                    self.widgets.get_widget('checkbutton14').set_active(True)
                else:
                    self.widgets.get_widget('checkbutton14').set_active(False)
            else:
                self.widgets.get_widget('entry42').set_text('')
                self.widgets.get_widget('entry43').set_text('')
                self.widgets.get_widget('entry44').set_text('')
                self.widgets.get_widget('entry45').set_text('')
                self.widgets.get_widget('entry46').set_text('')
                self.widgets.get_widget('entry47').set_text('')
                self.widgets.get_widget('entry89').set_text('')
                self.widgets.get_widget('checkbutton14').set_active(False)

            self.cursor.execute('select anio from morosos where n_orden=%s order by anio desc', (n_orden,))
            tupla = self.cursor.fetchall()
            liststore = self.widgets.get_widget('treeview3').get_model()
            liststore.clear()

            if len(tupla) > 0:
                for aux in tupla:
                    cadena = 'Debe la cuota: ' + str(aux[0])
                    liststore.append([cadena])
            else:
                liststore.append(['Este cofrade no tiene cuotas impagadas'])

            self.cursor.execute('select * from cofrades_loteria where n_orden=%s', (value,))
            tupla = self.cursor.fetchone()

            self.widgets.get_widget('spinbutton5').set_value(tupla[2])
            self.widgets.get_widget('spinbutton6').set_value(tupla[3])
            self.widgets.get_widget('spinbutton7').set_value(tupla[4])
            self.widgets.get_widget('spinbutton8').set_value(tupla[5])

            self.widgets.get_widget('checkbutton18').set_active(tupla[8])
            self.widgets.get_widget('checkbutton20').set_active(tupla[9])
            self.widgets.get_widget('checkbutton21').set_active(tupla[10])

    def clickShowCofrade(self, data=None):
        self.widgets.get_widget('statusbar1').push(7, 'Visualizando los datos de un cofrade...')
        self.statusbar.push(7, 'Visualizando los datos de un cofrade...')
        self.widgets.get_widget('checkbutton9').set_property('sensitive', False)
        self.widgets.get_widget('checkbutton15').set_property('sensitive', False)
        self.widgets.get_widget('checkbutton19').set_property('sensitive', False)
        self.widgets.get_widget('checkbutton22').set_property('sensitive', False)
        self.widgets.get_widget('checkbutton23').set_property('sensitive', False)
        self.widgets.get_widget('notebook3').set_current_page(0)
        self.widgets.get_widget('vbox26').hide_all()
        self.widgets.get_widget('label112').modify_fg(0, gtk.gdk.color_parse("red"))
        self.widgets.get_widget('label115').modify_fg(0, gtk.gdk.color_parse("red"))

        auxiliar = data.get_name()

        if (auxiliar == 'toolbutton5' or auxiliar == 'menuitem11'):

            self.widgets.get_widget('entry58').set_property('sensitive', True)

            value = self.getSelection('visualizar')
            self.cursor.execute("select * from cofrades_datospersonales where n_orden = %s", (value,))
            tupla = self.cursor.fetchone()

            tupla = list(tupla)
            for i in range(len(tupla)):
                if (tupla[i] == None):
                    tupla[i] = ''

            self.verDatosPersonales(tupla)

            self.cursor.execute('select * from cofrades_datosfinancieros where n_orden=%s', (value,))
            tupla = self.cursor.fetchone()

            self.verDatosFinancieros(tupla)

            self.cursor.execute('select * from cofrades_loteria where n_orden=%s', (value,))
            tupla = self.cursor.fetchone()

            self.verLoteria(tupla)

        else:
            self.widgets.get_widget('entry58').set_property('sensitive', False)
            self.widgets.get_widget('vbox26').show_all()
            value = self.getSelection2('visualizar')
            self.cursor.execute("select * from cofrades_datospersonales_bajas where n_orden = %s", (value,))
            tupla = self.cursor.fetchone()
            tupla = list(tupla)
            tupla.insert(2, None)

            for i in range(len(tupla)):
                if (tupla[i] == None):
                    tupla[i] = ''

            self.verDatosPersonales(tupla)

            self.cursor.execute('select * from cofrades_datosfinancieros where n_orden=%s', (value,))
            tupla = self.cursor.fetchone()

            self.verDatosFinancieros(tupla)

            self.cursor.execute('select * from cofrades_loteria where n_orden=%s', (value,))
            tupla = self.cursor.fetchone()

            self.verLoteria(tupla)

        self.cursor.execute('select anio from morosos where n_orden=%s order by anio desc', (value,))
        tupla = self.cursor.fetchall()
        self.verMorosos(tupla)

    def verMorosos(self, tupla):
        liststore = self.widgets.get_widget('treeview4').get_model()
        liststore.clear()

        if len(tupla) > 0:
            for aux in tupla:
                cadena = 'Debe la cuota: ' + str(aux[0])
                liststore.append([cadena])
        else:
            liststore.append(['Este cofrade no tiene cuotas impagadas'])

    def verDatosPersonales(self, tupla):
        self.widgets.get_widget('entry56').set_text(str(tupla[0]))
        self.widgets.get_widget('entry57').set_text(str(tupla[1]))
        self.widgets.get_widget('entry58').set_text(str(tupla[2]))
        self.widgets.get_widget('entry62').set_text(str(tupla[3]))

        nombre = str(tupla[4])
        aux = nombre.split(' ')
        for i in range(len(aux)):
            aux[i] = str.capitalize(aux[i])
        nombre = ' '.join(aux)

        nombre = unicode(nombre, 'iso8859_15')
        apellido1 = unicode(str.capitalize(tupla[5]), 'iso8859_15')
        apellido2 = unicode(str.capitalize(tupla[6]), 'iso8859_15')
        nombre = nombre.replace('Á', 'á')
        nombre = nombre.replace('É', 'é')
        nombre = nombre.replace('Í', 'í')
        nombre = nombre.replace('Ó', 'ó')
        nombre = nombre.replace('Ú', 'ú')
        nombre = nombre.replace('Ñ', 'ñ')
        apellido1 = apellido1.replace('Á', 'á')
        apellido1 = apellido1.replace('É', 'é')
        apellido1 = apellido1.replace('Í', 'í')
        apellido1 = apellido1.replace('Ó', 'ó')
        apellido1 = apellido1.replace('Ú', 'ú')
        apellido1 = apellido1.replace('Ñ', 'ñ')
        apellido2 = apellido2.replace('Á', 'á')
        apellido2 = apellido2.replace('É', 'é')
        apellido2 = apellido2.replace('Í', 'í')
        apellido2 = apellido2.replace('Ó', 'ó')
        apellido2 = apellido2.replace('Ú', 'ú')
        apellido2 = apellido2.replace('Ñ', 'ñ')
        self.widgets.get_widget('entry59').set_text(nombre)
        self.widgets.get_widget('entry60').set_text(apellido1)
        self.widgets.get_widget('entry61').set_text(apellido2)
        self.widgets.get_widget('entry83').set_text(str.capitalize(tupla[7]))

        self.widgets.get_widget('entry66').set_text(unicode(str(tupla[9]), 'iso8859_15'))
        self.widgets.get_widget('entry67').set_text(unicode(str(tupla[10]), 'iso8859_15'))
        self.widgets.get_widget('entry68').set_text(unicode(str(tupla[11]), 'iso8859_15'))

        fecha = self.normalizarFecha(str(tupla[12]))
        self.widgets.get_widget('entry69').set_text(fecha)
        fecha = self.normalizarFecha(str(tupla[13]))
        self.widgets.get_widget('entry70').set_text(fecha)
        bufferaux = self.widgets.get_widget('textview3').get_buffer()
        bufferaux.set_text(str.capitalize(str(unicode(tupla[14], 'iso8859_15'))))
        self.widgets.get_widget('entry71').set_text(str(tupla[15]))
        self.widgets.get_widget('entry72').set_text(unicode(str(tupla[16]), 'iso8859_15'))
        if (len(tupla) == 19):
            fecha = self.normalizarFecha(str(tupla[18]))
            self.widgets.get_widget('entry92').set_text(fecha)

            self.widgets.get_widget('entry91').set_text(str(self.dictbajas[tupla[17]]))

        self.cursor.execute(
            'select p.nombre, m.municipio, c.nombre from provincias_nueva p, municipios m, calles_nueva c where c.poblacion=m.id and m.provincia=p.id and c.id=%s',
            (str(tupla[8]),))
        tupla = self.cursor.fetchone()
        self.widgets.get_widget('entry63').set_text(unicode(str(tupla[0]), 'iso8859_15'))
        self.widgets.get_widget('entry64').set_text(unicode(str(tupla[1]), 'iso8859_15'))
        self.widgets.get_widget('entry65').set_text(unicode(str.capitalize(tupla[2]), 'iso8859_15'))

        self.widgets.get_widget('window4').show()

    def verDatosFinancieros(self, tupla):
        n_orden = int(self.widgets.get_widget('entry57').get_text())

        self.cursor.execute('select * from morosos where n_orden=%s and anio=%s', (n_orden, self.anio))
        tuplaux = self.cursor.fetchone()
        if (tuplaux):
            self.widgets.get_widget('checkbutton9').set_active(True)
        else:
            self.widgets.get_widget('checkbutton9').set_active(False)

        if tupla:
            if (tupla[2] == None):
                self.widgets.get_widget('entry73').set_text('')
            else:
                self.widgets.get_widget('entry73').set_text(str(tupla[2]).zfill(4))
            if (tupla[3] == None):
                self.widgets.get_widget('entry74').set_text('')
            else:
                self.widgets.get_widget('entry74').set_text(str(tupla[3]).zfill(4))
            if (tupla[4] == None):
                self.widgets.get_widget('entry75').set_text('')
            else:
                self.widgets.get_widget('entry75').set_text(str(tupla[4]).zfill(2))
            if (tupla[5] == None):
                self.widgets.get_widget('entry76').set_text('')
            else:
                self.widgets.get_widget('entry76').set_text(str(tupla[5]).zfill(10))
            if (tupla[6] == None):
                self.widgets.get_widget('entry77').set_text('')
            else:
                self.cursor.execute('select nombre from bancos where id=%s', (int(tupla[6]),))
                tupla2 = self.cursor.fetchone()
                self.widgets.get_widget('entry78').set_text(unicode(str(tupla2[0]), 'iso8859-15'))
            if (tupla[7] == None):
                self.widgets.get_widget('entry77').set_text('')
            else:
                self.widgets.get_widget('entry77').set_text(str(tupla[7]))

            if (tupla[8] == None):
                self.widgets.get_widget('entry90').set_text('')
            else:
                self.widgets.get_widget('entry90').set_text(str(tupla[8]))
            if (tupla[9] == 'True'):
                self.widgets.get_widget('checkbutton15').set_active(True)
            else:
                self.widgets.get_widget('checkbutton15').set_active(False)
        else:
            self.widgets.get_widget('entry73').set_text('')
            self.widgets.get_widget('entry74').set_text('')
            self.widgets.get_widget('entry75').set_text('')
            self.widgets.get_widget('entry76').set_text('')
            self.widgets.get_widget('entry77').set_text('')
            self.widgets.get_widget('entry78').set_text('')
            self.widgets.get_widget('entry90').set_text('')
            self.widgets.get_widget('checkbutton15').set_active(False)

    def verLoteria(self, tupla):
        self.widgets.get_widget('entry84').set_text(str(tupla[2]))
        self.widgets.get_widget('entry85').set_text(str(tupla[3]))
        self.widgets.get_widget('entry86').set_text(str(tupla[4]))
        self.widgets.get_widget('entry87').set_text(str(tupla[5]))
        self.widgets.get_widget('checkbutton19').set_active(tupla[8])
        self.widgets.get_widget('checkbutton22').set_active(tupla[9])
        self.widgets.get_widget('checkbutton23').set_active(tupla[10])

    def normalizarFecha(self, fecha):
        if fecha:
            year, month, day = fecha.split('-')
            fecha = str(day) + '/' + str(month) + '/' + str(year)
            return fecha
        else:
            return ''

    def dialogModifyCofrade(self, data=None):
        domiciliar = self.widgets.get_widget('checkbutton14').get_active()
        domiciliarl = self.widgets.get_widget('checkbutton18').get_active()
        aux2 = self.verifyEconomicEntries2()
        print aux2
        print aux2[0]
        if aux2[0] == None:
            print 'yoja'
        if (aux2 != 'vacio'):
            if (aux2[0] != None):
                if (not domiciliar) and (not domiciliarl):
                    self.error('Si no va a domiciliar ningún pago, por favor elimine el número de cuenta.')
                    return False

        dialog = self.widgets.get_widget('messagedialog3')
        dialog.format_secondary_text('¿Está seguro que desea modificar los datos del cofrade?')
        dialog.show()

    def acceptModifyCofrade(self, data=None):
        aux = self.verifyDataEntries2()
        aux2 = self.verifyEconomicEntries2()

        if aux and aux2:
            try:
                self.cursor.execute(
                    "update cofrades_datospersonales set dni=%s, nombre=%s, apellido1=%s, apellido2=%s, sexo=%s, id_direccion=%s, numero=%s, planta=%s, piso=%s, fecha_nacimiento=%s, fecha_inscripcion=%s, nota=%s, telefono=%s, email=%s where n_orden=%s",
                    aux)
                n_orden = int(self.widgets.get_widget('entry5').get_text())

                if (aux2 == 'vacio'):
                    self.cursor.execute('delete from cofrades_datosfinancieros where n_orden=%s', aux[14])
                    self.cursor.execute('delete from morosos where n_orden=%s and anio=%s', (n_orden, self.anio))
                else:
                    self.cursor.execute('select * from cofrades_datosfinancieros where n_orden=%s', aux[14])
                    tupla = self.cursor.fetchone()
                    aux2 = list(aux2)
                    if (tupla != None):
                        faltapago = aux2[6]
                        aux2[6] = 'Borrar'
                        aux2.remove('Borrar')

                        self.cursor.execute(
                            'update cofrades_datosfinancieros set entidad=%s, oficina=%s, dc=%s, n_cuenta=%s, id_banco=%s, dir_banco=%s, titular=%s, domiciliar_pagos=%s where n_orden=%s',
                            aux2)

                        self.cursor.execute('select * from morosos where n_orden=%s and anio=%s', (n_orden, self.anio))
                        tupla2 = self.cursor.fetchone()
                        if (tupla2 != None):
                            if (faltapago == 'False'):
                                self.cursor.execute('delete from morosos where n_orden=%s and anio=%s',
                                                    (n_orden, self.anio))
                        else:
                            # 'no existe'
                            if faltapago == 'True':
                                self.cursor.execute('select max(id)+1 from morosos')
                                ident = self.cursor.fetchone()
                                ident = int(ident[0])
                                self.cursor.execute('insert into morosos values (%s, %s, %s)',
                                                    (ident, n_orden, self.anio))

                    else:
                        aux3 = self.verifyEconomicEntries2()
                        if aux3:
                            if (aux3 != 'vacio'):
                                self.cursor.execute('select max(id)+1 from cofrades_datosfinancieros')
                                ident = self.cursor.fetchone()
                                ident = int(ident[0])
                                aux3 = list(aux3)
                                id_cofrade = aux3.pop()
                                aux3.insert(0, id_cofrade)
                                aux3.insert(0, ident)

                                faltapago = aux3[8]
                                aux3[8] = 'Borrar'
                                aux3.remove('Borrar')
                                aux3.insert(len(aux3), n_orden)
                                if aux3[2] != None:
                                    self.cursor.execute(
                                        'insert into cofrades_datosfinancieros values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                                        aux3)
                                if faltapago == 'True':
                                    self.cursor.execute('select max(id)+1 from morosos')
                                    ident = self.cursor.fetchone()
                                    ident = int(ident[0])
                                    self.cursor.execute('insert into morosos values (%s, %s, %s)',
                                                        (ident, n_orden, self.anio))

                ncofrade = int(self.widgets.get_widget('entry5').get_text())

                na1 = int(self.widgets.get_widget('spinbutton5').get_value())
                ni1 = int(self.widgets.get_widget('spinbutton6').get_value())
                na2 = int(self.widgets.get_widget('spinbutton7').get_value())
                ni2 = int(self.widgets.get_widget('spinbutton8').get_value())
                aux3 = [na1, ni1, na2, ni2]

                part_navidad = self.widgets.get_widget('checkbutton20').get_active()
                part_ninio = self.widgets.get_widget('checkbutton21').get_active()
                dom_loteria = self.widgets.get_widget('checkbutton18').get_active()
                if (na1 == 0) and (na2 == 0) and (ni1 == 0) and (ni2 == 0) and (part_ninio == False) and (
                    part_navidad == False):
                    # sin loteria
                    aux3.append(True)
                    aux3.append(dom_loteria)
                    aux3.append(False)
                    aux3.append(False)
                else:
                    aux3.append(False)
                    aux3.append(dom_loteria)
                    aux3.append(part_navidad)
                    aux3.append(part_ninio)

                aux3.append(ncofrade)
                self.cursor.execute(
                    'update cofrades_loteria set n_navidad1=%s, n_ninio1=%s, n_navidad2=%s, n_ninio2=%s, sin_loteria=%s, domiciliar_loteria=%s, participacion_navidad=%s, participacion_ninio = %s where n_orden=%s',
                    aux3)

                if not self.filtrado:
                    self.cursor.execute(
                        'select n_orden,n_cofrade, nombre, apellido1, apellido2 from cofrades_datospersonales order by n_orden')
                    tuplas = self.cursor.fetchall()
                    tuplas = self.normalizar(tuplas)
                else:
                    tuplas = self.changeEntry(self.widgets.get_widget('entry94'), None)

                self.fillData(tuplas)
                self.widgets.get_widget('window3').hide()
                self.insertPanel('OK', 'Modificación de cofrade realizada correctamente')
            except MySQLdb.Error, e:
                self.error(e)

    def clickConfimDelete(self, data=None):
        self.widgets.get_widget('combobox1').set_active(-1)
        data = datetime.today().strftime("%d/%m/%Y")
        self.widgets.get_widget('entry93').set_text(data)
        bufferaux = self.widgets.get_widget('textview4').get_buffer()
        bufferaux.set_text('')

        self.widgets.get_widget('window5').show()

    def acceptDeleteCofrade(self, data=None):
        value = self.getSelection('')
        if value:
            lista = self.verifyDataBaja()

            if lista:
                # inserta en la tabla de bajas
                self.cursor.execute("select max(id)+1 from cofrades_datospersonales_bajas")
                ident = self.cursor.fetchone()
                ident = int(ident[0])
                self.cursor.execute("select * from cofrades_datospersonales where n_orden = %s", (value,))
                tupla = self.cursor.fetchone()
                tupla = list(tupla)

                tupla[0] = ident
                tupla[2] = 'remove'
                tupla.remove('remove')

                if lista[2] == '':
                    tupla[13] = None
                else:
                    tupla[13] = lista[2]

                tupla.append(lista[0])
                tupla.append(lista[1])

                self.cursor.execute(
                    'insert into cofrades_datospersonales_bajas values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                    tupla)

                # Elimina de la tabla de altas
                self.cursor.execute("select n_cofrade from cofrades_datospersonales where n_orden = %s", (value,))
                tupla = self.cursor.fetchone()

                ncofrade = int(tupla[0])

                self.cursor.execute("delete from cofrades_datospersonales where n_orden = %s", (value,))
                self.cursor.execute("update cofrades_datospersonales set n_cofrade=n_cofrade-1 where n_cofrade > %s",
                                    ncofrade)

                """
                self.cursor.execute("delete from cofrades_datosfinancieros where n_orden = %s", (value,))
                self.cursor.execute("delete from cofrades_loteria where n_orden = %s", (value,))
                """
                if not self.filtrado:
                    self.cursor.execute(
                        'select n_orden,n_cofrade, nombre, apellido1, apellido2 from cofrades_datospersonales order by n_orden')
                    tuplas = self.cursor.fetchall()
                    tuplas = self.normalizar(tuplas)
                else:
                    tuplas = self.changeEntry(self.widgets.get_widget('entry94'), None)

                self.fillData(tuplas)

                self.widgets.get_widget('window5').hide()
                self.insertPanel('OK', 'Cofrade eliminado correctamente')

    def acceptNewCofrade(self, data=None):
        aux = self.verifyDataEntries()
        aux2 = self.verifyEconomicEntries()

        if aux and aux2:
            try:
                if (aux2 != 'vacio'):
                    domiciliar = self.widgets.get_widget('checkbutton13').get_active()
                    domiciliarl = self.widgets.get_widget('checkbutton10').get_active()

                    if (not domiciliar) and (not domiciliarl):
                        self.error('Si no va a domiciliar ningún pago, por favor elimine el número de cuenta.')
                        return False

                    self.cursor.execute('select max(id)+1 from cofrades_datosfinancieros')
                    ident = self.cursor.fetchone()
                    ident = int(ident[0])
                    aux2 = list(aux2)
                    aux2.insert(0, ident)
                    aux2.append(aux[1])
                    faltapago = aux2[8]

                    aux2[8] = 'Borrar'
                    aux2.remove('Borrar')

                    self.cursor.execute(
                        'insert into cofrades_datosfinancieros values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                        aux2)

                    if faltapago == 'True':
                        self.cursor.execute('select max(id)+1 from morosos')
                        ident = self.cursor.fetchone()
                        ident = int(ident[0])

                        self.cursor.execute('insert into morosos values (%s, %s, %s)', (ident, aux2[10], self.anio))

                self.cursor.execute(
                    'insert into cofrades_datospersonales values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                    aux)

                self.cursor.execute('select max(id)+1 from cofrades_loteria')
                ident = self.cursor.fetchone()
                ident = int(ident[0])
                ncofrade = aux[0]
                na1 = int(self.widgets.get_widget('spinbutton1').get_value())
                ni1 = int(self.widgets.get_widget('spinbutton2').get_value())
                na2 = int(self.widgets.get_widget('spinbutton3').get_value())
                ni2 = int(self.widgets.get_widget('spinbutton4').get_value())
                aux3 = [ident, ncofrade, na1, ni1, na2, ni2]
                aux3.append(aux[1])
                part_navidad = self.widgets.get_widget('checkbutton16').get_active()
                part_ninio = self.widgets.get_widget('checkbutton17').get_active()
                dom_loteria = self.widgets.get_widget('checkbutton10').get_active()
                if (na1 == 0) and (na2 == 0) and (ni1 == 0) and (ni2 == 0) and (part_ninio == False) and (
                    part_navidad == False):
                    # sin loteria
                    aux3.append(True)
                    aux3.append(dom_loteria)
                    aux3.append(False)
                    aux3.append(False)
                else:
                    aux3.append(False)
                    aux3.append(dom_loteria)
                    aux3.append(part_navidad)
                    aux3.append(part_ninio)

                self.cursor.execute('insert into cofrades_loteria values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                                    aux3)

                if not self.filtrado:
                    self.cursor.execute(
                        'select n_orden,n_cofrade, nombre, apellido1, apellido2 from cofrades_datospersonales order by n_orden')
                    tuplas = self.cursor.fetchall()
                    tuplas = self.normalizar(tuplas)
                else:
                    tuplas = self.changeEntry(self.widgets.get_widget('entry94'), None)

                self.fillData(tuplas)
                self.hideWindow2()
                self.widgets.get_widget('window2').hide()
                self.insertPanel('OK', 'Nuevo cofrade creada correctamente')
            except MySQLdb.Error, e:
                self.error(e)

    def verifyDataBaja(self):
        motivo = self.widgets.get_widget('combobox1').get_active()
        fecha = self.widgets.get_widget('entry93').get_text()
        bufferaux = self.widgets.get_widget('textview4').get_buffer()
        nota = unicode(bufferaux.get_text(bufferaux.get_start_iter(), bufferaux.get_end_iter()), 'utf 8')

        if (motivo == -1):
            self.error('Seleccione un motivo de baja')
            return False

        if (str(fecha) == ''):
            self.error('El campo fecha de baja no puede estar vacío')
            return False
        else:
            if (not re.match('(0?[1-9]|[12][0-9]|3[01])\/(0?[1-9]|1[012])\/[0-9]{4}', fecha)):
                self.error('Introduzca una fecha de baja en un formato válido (dd/mm/aaaa).')
                return False

        fecha = self.ajustarFecha(fecha)
        motivo = motivo + 1

        lista = [motivo, fecha, nota]
        return lista

    def verifyEconomicEntries(self):
        aux = self.allEntriesEmtpy()
        idcofrade = self.widgets.get_widget('entry2').get_text()
        faltapago = self.widgets.get_widget('checkbutton1').get_active()
        titular = str(self.widgets.get_widget('entry88').get_text())
        domiciliar = self.widgets.get_widget('checkbutton13').get_active()

        if (aux == True):
            return 'vacio'
        if (aux == False):
            entidad = self.widgets.get_widget('entry36').get_text()
            oficina = self.widgets.get_widget('entry37').get_text()
            dc = self.widgets.get_widget('entry38').get_text()
            numero = self.widgets.get_widget('entry39').get_text()
            banco = self.widgets.get_widget('entry40').get_text()
            dirbanco = str(self.widgets.get_widget('entry41').get_text())
            if titular == '':
                titular = None
            if dirbanco == '':
                dirbanco = None

            vacio = True
            try:
                if (int(entidad) != ''):
                    vacio = False
                if (int(oficina) != ''):
                    vacio = False
                if (int(dc) != ''):
                    vacio = False
                if (int(numero) != ''):
                    vacio = False
                if not vacio:
                    if (banco == ''):
                        self.error('Intrudzca un banco válido.')
                        return False
            except ValueError:
                self.error('Los campos del número de cuenta deben de ser números enteros.')
                return False

            self.cursor.execute('select id from bancos where nombre=%s', unicode(banco, 'utf 8'))
            tupla = self.cursor.fetchone()
            banco = int(tupla[0])
            return (
            int(idcofrade), int(entidad), int(oficina), int(dc), int(numero), int(banco), dirbanco, str(faltapago),
            titular, str(domiciliar))
        if (aux == 'no'):
            return (int(idcofrade), None, None, None, None, None, None, str(faltapago), None, None)

    def verifyEconomicEntries2(self):
        aux = self.allEntriesEmtpy2()
        idcofrade = self.widgets.get_widget('entry5').get_text()
        faltapago = self.widgets.get_widget('checkbutton3').get_active()
        titular = self.widgets.get_widget('entry89').get_text()
        domiciliar = self.widgets.get_widget('checkbutton14').get_active()
        if (aux == True):
            return 'vacio'
        if (aux == False):
            entidad = self.widgets.get_widget('entry42').get_text()
            oficina = self.widgets.get_widget('entry43').get_text()
            dc = self.widgets.get_widget('entry44').get_text()
            numero = self.widgets.get_widget('entry45').get_text()
            banco = self.widgets.get_widget('entry47').get_text()
            dirbanco = self.widgets.get_widget('entry46').get_text()

            vacio = True
            try:
                if (int(entidad) != ''):
                    vacio = False
                if (int(oficina) != ''):
                    vacio = False
                if (int(dc) != ''):
                    vacio = False
                if (int(numero) != ''):
                    vacio = False
                if not vacio:
                    if (banco == ''):
                        self.error('Intrudzca un banco válido.')
                        return False
            except ValueError:
                self.error('Los campos del número de cuenta deben de ser un números enteros.')
                return False

            self.cursor.execute('select id from bancos where nombre=%s', unicode(banco, 'utf 8'))
            tupla = self.cursor.fetchone()
            banco = int(tupla[0])

            return (
            int(entidad), int(oficina), int(dc), int(numero), int(banco), str(dirbanco), str(faltapago), str(titular),
            str(domiciliar), int(idcofrade))
        if (aux == 'no'):
            return (None, None, None, None, None, None, str(faltapago), None, None, int(idcofrade))

    def allEntriesEmtpy(self):
        for aux in range(36, 42):
            name = 'entry' + str(aux)
            if (self.widgets.get_widget(name).get_text() != ''):
                return False

        if (self.widgets.get_widget('entry88').get_text() != ''):
            return False
        if (self.widgets.get_widget('checkbutton13').get_active() == True):
            return False
        if (self.widgets.get_widget('checkbutton1').get_active() == True):
            return 'no'
        return True

    def allEntriesEmtpy2(self):
        for aux in range(42, 48):
            name = 'entry' + str(aux)
            if (self.widgets.get_widget(name).get_text() != ''):
                return False

        if (self.widgets.get_widget('entry89').get_text() != ''):
            return False
        if (self.widgets.get_widget('checkbutton14').get_active() == True):
            return False
        if (self.widgets.get_widget('checkbutton3').get_active() == True):
            return 'no'
        return True

    def showBanco(self, widget=None, event=None, data=None):
        if (event == 0):
            widget.set_text('')
        else:
            aux = Banco(widget)
            aux.window.set_modal(True)
            aux.window.present()

    def verifyDataEntries(self):
        ident = self.widgets.get_widget('entry2').get_text()
        norden = self.widgets.get_widget('entry6').get_text()
        ncofrade = self.widgets.get_widget('entry7').get_text()

        nombre = unicode(self.widgets.get_widget('entry3').get_text(), 'utf 8')
        apellido1 = unicode(self.widgets.get_widget('entry8').get_text(), 'utf 8')
        apellido2 = unicode(self.widgets.get_widget('entry9').get_text(), 'utf 8')
        dni = self.widgets.get_widget('entry10').get_text()
        if (self.widgets.get_widget('radiobutton6').get_active() == True):
            sexo = 'Hombre'
        else:
            sexo = 'Mujer'

        calle = unicode(self.widgets.get_widget('entry13').get_text(), 'utf 8')
        numero = unicode(self.widgets.get_widget('entry14').get_text(), 'utf 8')
        planta = unicode(self.widgets.get_widget('entry15').get_text(), 'utf 8')
        piso = unicode(self.widgets.get_widget('entry16').get_text(), 'utf 8')
        fechanacimiento = self.widgets.get_widget('entry17').get_text()
        fechainscripcion = self.widgets.get_widget('entry18').get_text()
        telefono = self.widgets.get_widget('entry19').get_text()
        email = unicode(self.widgets.get_widget('entry20').get_text(), 'utf 8')
        bufferaux = self.widgets.get_widget('textview1').get_buffer()
        nota = unicode(bufferaux.get_text(bufferaux.get_start_iter(), bufferaux.get_end_iter()), 'utf 8')

        try:
            int(ident)
        except ValueError:
            self.error('El campo Identificador debe de ser un número entero.')
            return False
        try:
            int(norden)
        except ValueError:
            self.error('El campo Número de orden debe de ser un número entero.')
            return False
        try:
            int(ncofrade)
        except ValueError:
            self.error('El campo Número de cofrade debe de ser un número entero.')
            return False

        if (str(nombre) == ''):
            self.error('El campo nombre no puede estar vacío')
            return False

        if (str(apellido1) == ''):
            self.error('El campo primer apellido no puede estar vacío')
            return False

        if (str(apellido2) == ''):
            self.error('El campo segundo apellido no puede estar vacío')
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

        if (str(fechanacimiento) == ''):
            fechanacimiento = None
        else:
            if (not re.match('(0?[1-9]|[12][0-9]|3[01])\/(0?[1-9]|1[012])\/[0-9]{4}', fechanacimiento)):
                self.error('Introduzca una fecha de nacimiento en un formato válido (dd/mm/aaaa).')
                return False

        if (str(fechainscripcion) == ''):
            self.error('El campo fecha de inscripción no puede estar vacío')
            return False
        else:
            if (not re.match('(0?[1-9]|[12][0-9]|3[01])\/(0?[1-9]|1[012])\/[0-9]{4}', fechainscripcion)):
                self.error('Introduzca una fecha de inscripción en un formato válido (dd/mm/aaaa).')
                return False

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

        self.cursor.execute('select id from calles_nueva where nombre=%s', unicode(str.lower(str(calle)), 'utf 8'))
        if (fechanacimiento != None):
            fechanacimiento = self.ajustarFecha(fechanacimiento)
        fechainscripcion = self.ajustarFecha(fechainscripcion)
        tupla = self.cursor.fetchone()
        calle = int(tupla[0])
        lista = [ident, norden, ncofrade, dni, nombre, apellido1, apellido2, sexo, calle, numero, planta, piso,
                 fechanacimiento, fechainscripcion, nota, telefono, email]
        return lista

    def verifyDataEntries2(self):
        ident = self.widgets.get_widget('entry4').get_text()
        norden = self.widgets.get_widget('entry5').get_text()
        ncofrade = self.widgets.get_widget('entry21').get_text()

        nombre = unicode(self.widgets.get_widget('entry22').get_text(), 'utf 8')
        apellido1 = unicode(self.widgets.get_widget('entry23').get_text(), 'utf 8')
        apellido2 = unicode(self.widgets.get_widget('entry24').get_text(), 'utf 8')
        dni = self.widgets.get_widget('entry25').get_text()
        if (self.widgets.get_widget('radiobutton8').get_active() == True):
            sexo = 'Hombre'
        else:
            sexo = 'Mujer'

        calle = unicode(self.widgets.get_widget('entry28').get_text(), 'utf 8')
        numero = unicode(self.widgets.get_widget('entry29').get_text(), 'utf 8')
        planta = unicode(self.widgets.get_widget('entry30').get_text(), 'utf 8')
        piso = unicode(self.widgets.get_widget('entry31').get_text(), 'utf 8')
        fechanacimiento = self.widgets.get_widget('entry32').get_text()
        fechainscripcion = self.widgets.get_widget('entry33').get_text()
        telefono = self.widgets.get_widget('entry34').get_text()
        email = unicode(self.widgets.get_widget('entry35').get_text(), 'utf 8')
        bufferaux = self.widgets.get_widget('textview2').get_buffer()
        nota = unicode(bufferaux.get_text(bufferaux.get_start_iter(), bufferaux.get_end_iter()), 'utf 8')

        try:
            int(ident)
        except ValueError:
            self.error('El campo Identificador debe de ser un número entero.')
            return False
        try:
            int(norden)
        except ValueError:
            self.error('El campo Número de orden debe de ser un número entero.')
            return False
        try:
            int(ncofrade)
        except ValueError:
            self.error('El campo Número de cofrade debe de ser un número entero.')
            return False

        if (str(nombre) == ''):
            self.error('El campo nombre no puede estar vacío')
            return False

        if (str(apellido1) == ''):
            self.error('El campo primer apellido no puede estar vacío')
            return False

        if (str(apellido2) == ''):
            self.error('El campo segundo apellido no puede estar vacío')
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

        if (str(fechanacimiento) == ''):
            fechanacimiento = None
        else:
            if (not re.match('(0?[1-9]|[12][0-9]|3[01])\/(0?[1-9]|1[012])\/[0-9]{4}', fechanacimiento)):
                self.error('Introduzca una fecha de nacimiento en un formato válido (dd/mm/aaaa).')
                return False

        if (str(fechainscripcion) == ''):
            self.error('El campo fecha de inscripción no puede estar vacío')
            return False
        else:
            if (not re.match('(0?[1-9]|[12][0-9]|3[01])\/(0?[1-9]|1[012])\/[0-9]{4}', fechainscripcion)):
                self.error('Introduzca una fecha de inscripción en un formato válido (dd/mm/aaaa).')
                return False

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

        self.cursor.execute('select id from calles_nueva where nombre=%s', unicode(str.lower(str(calle)), 'utf 8'))
        if (fechanacimiento != None):
            fechanacimiento = self.ajustarFecha(fechanacimiento)
        fechainscripcion = self.ajustarFecha(fechainscripcion)
        tupla = self.cursor.fetchone()
        calle = int(tupla[0])
        lista = [dni, nombre, apellido1, apellido2, sexo, calle, numero, planta, piso, fechanacimiento,
                 fechainscripcion, nota, telefono, email, norden]
        return lista

    def ajustarFecha(self, fecha):
        day, month, year = fecha.split('/')

        fecha = year + '-' + month + '-' + day
        return fecha

    def showProvincia(self, widget, event, data):
        if (event == 0):
            widget.set_text('')
        else:
            aux = Provincia(widget)
            aux.window.set_modal(True)
            aux.window.present()

    def showMunicipio(self, widget, event, data):
        if (event == 0):
            widget.set_text('')
        else:
            if (widget.get_name() == 'entry12'):
                widget.set_text(self.widgets.get_widget('entry11').get_text())
            else:
                widget.set_text(self.widgets.get_widget('entry26').get_text())
            aux = Municipio(widget)
            aux.window.set_modal(True)
            aux.window.present()

    def showCalle(self, widget, event, data):
        if (event == 0):
            widget.set_text('')
        else:
            if (widget.get_name() == 'entry13'):
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
            self.error('Seleccione el cofrade que desea ' + msg)
            return False

    def getSelection2(self, msg):
        treeview = self.widgets.get_widget('treeview2')
        treeselection = treeview.get_selection()
        (model, iteration) = treeselection.get_selected()
        try:
            value = self.liststore2.get_value(iteration, 0)
            return value
        except TypeError:
            self.error('Seleccione el cofrade que desea ' + msg)
            return False

    def error(self, msg):
        self.insertPanel('ERROR', msg)
        dialog = self.widgets.get_widget('messagedialog1')
        dialog.format_secondary_text(str(msg))
        dialog.present()

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

    def hideWindow7(self, data=None):
        nombre = data.get_name()
        if nombre != 'button14':
            try:
                precio = float(self.widgets.get_widget('entry98').get_text())
                self.cursor.execute('update gasto_domiciliar set precio = %s where id = 0', precio)
            except ValueError:
                self.error('Introduzca un valor real: XXX.XX')
                return False
        self.widgets.get_widget('window7').hide()

    def hideWindow8(self, data=None):
        nombre = data.get_name()
        if nombre != 'button16':
            try:
                precio = float(self.widgets.get_widget('entry99').get_text())
                self.cursor.execute('update gasto_enviopostal set precio = %s where id = 0', precio)
            except ValueError:
                self.error('Introduzca un valor real: XXX.XX')
                return False
        self.widgets.get_widget('window8').hide()

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

    def hideCalendar(self, widget, data=None):
        self.widgets.get_widget('dialog1').hide()
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
        self.cursor.execute('select n_orden from cofrades_datospersonales where n_orden = %s',
                            (self.getSelection('insertar'),))
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
            # This is a right-click
            context_menu.popup(None, None, None, event.button, event.time)

    def rightClick2(self, widget, event=None):
        context_menu = self.widgets.get_widget("menu3")
        path = widget.get_path_at_pos(int(event.x), int(event.y))
        if (path == None):
            """If we didn't get apath then we don't want anything
		    to be selected."""
            selection = widget.get_selection()
            selection.unselect_all()
        if (event.button == 3):
            # This is a right-click
            context_menu.popup(None, None, None, event.button, event.time)


def main():
    Cofrade()
    gtk.gdk.threads_init()
    gtk.gdk.threads_enter()
    gtk.main()
    gtk.gdk.threads_leave()


if __name__ == "__main__":
    sys.exit(main())
