#! /usr/bin/env python
# -*- coding: utf-8 -*-
import pygtk
pygtk.require('2.0')
import gtk.glade
import sys
#sys.path.append('C:\\Documents and Settings\\Manolo\\Escritorio\\final\\src')
sys.path.append('C:\\Program Files\\Gestion_de_cofradias')
sys.path.append('C:\\Archivos de programa\\Gestion_de_cofradias')
import re
import MySQLdb
from datetime import datetime
from operator import itemgetter
from provincias.provincias import Provincia
from municipios.municipios import Municipio
from calles.calles import Calle
from bancos.bancos import Banco
from sectores.sectores import Sector
from cofrades.cofrades import Cofrade
from directivos.directivos import Directivo
from autoridades.autoridades import Autoridad
from seguridad.seguridad import Seguridad
from informes.informes import Informe
from papeletasitio.papeletasitio import PapeletaSitio
from costaleros.costaleros import Costalero

class Inicio():
    def __init__(self):
        
        self.widgets = gtk.glade.XML('./glade/presentacion.glade')
        self.widgets.signal_autoconnect(self)
        self.widgets.get_widget('window1').show()

    def enterSistem(self, widget=None):
        user = self.widgets.get_widget('entry1').get_text()
        password = self.widgets.get_widget('entry2').get_text()
        try:
            MySQLdb.connect(user=user, passwd=password, db='proyecto')
            self.init2()
        except MySQLdb.Error:
            state = self.widgets.get_widget('label3').get_state()
            self.widgets.get_widget('label3').modify_fg(state,gtk.gdk.color_parse("#8A0808"))
            self.widgets.get_widget('label3').set_text('Acceso denegado.\n\nEl usuario o la contraseña\nson incorrectos.')
            self.widgets.get_widget('entry2').set_text('')
        
    def init2(self):    
        self.widgets.get_widget('window1').destroy()

        self.widgets = gtk.glade.XML('./glade/inicio.glade')
        self.widgets.signal_autoconnect(self)
        
        self.cursor = self.conectar()
        
        self.fillLeftFrame()
        self.bottomFrame()
        self.fillTopFrame()
        
        self.createTreeviewTables()
        
        self.widgets.get_widget('window1').show()
        """
        alin = self.widgets.get_widget('alignment1')
        aux = gtk.glade.XML('./glade/index.glade')
        aux.signal_autoconnect(self)
        aux.get_widget('hbox1').reparent(alin)
        
        aux.get_widget('hbox1').show_all()
        """
        
    def showWindow6(self, data=None):
        self.widgets.get_widget('entry95').set_text('')
        self.widgets.get_widget('window6').show()
    
    def hideWindow6(self, data=None):
        self.widgets.get_widget('window6').hide()

    def showAbout(self, data=None):
        self.widgets.get_widget('window2').show()

    def hideAbout(self, data=None):
        self.widgets.get_widget('window2').hide()

    def acceptNewYear(self, data=None):
        label = self.widgets.get_widget('label3')
        label.modify_fg(0,gtk.gdk.color_parse("red"))
        combo = self.widgets.get_widget('combobox1')
        liststore = combo.get_model()
        num = data.get_text()
        try:
            num = int(num)
            if (not re.match('^20[0-9]{2}', str(num))):
                raise ValueError
            for aux in self.dictAnio:
                if (self.dictAnio[aux] == int(num)):
                    raise ValueError
            liststore.append([num])
            self.dictAnio[len(self.dictAnio)]= num
            combo.set_active(len(self.dictAnio)-1)
            self.hideWindow6()
            self.crearTabla(num)
        except ValueError:
            label.set_text('Intruduzca un número de año correcto y que no exista')
            data = datetime.today().strftime("%d/%m/%y %H:%M:%S")
            self.liststorebottom.append([data, 'Intruduzca un número de año correcto y que no exista', '#8A0808'])
            
    def crearTabla(self, num):
        nombre = 'cofrades_papeletassitio_'+str(num)
        self.cursor.execute('CREATE TABLE if not exists '+ nombre +' LIKE cofrades_papeletassitio_2011')
        data = datetime.today().strftime("%d/%m/%y %H:%M:%S")
        self.liststorebottom.append([data, 'Año creado correctamente', '#0B0B61'])
        
    def deleteWindow(self, widget, data=None):
        widget.hide()
        return True    

    def conectar(self):
        self.db = MySQLdb.connect(user="root", passwd="admin", db='proyecto')
        return self.db.cursor()

    def desconectar(self):
        try:
            self.db.close()
        except AttributeError:
            pass
    
    def fillTopFrame(self):
        combo = self.widgets.get_widget('combobox1')
        liststore = gtk.ListStore(int)

        self.cursor.execute('select distinct anio from morosos order by anio')
        tupla = self.cursor.fetchall()
        cell = gtk.CellRendererText()
        combo.pack_start(cell, True)
        combo.add_attribute(cell, 'text', 0) 
        self.dictAnio = dict()
        index = 0
        for aux in tupla:
            #liststore.append([int(aux[0])])
            self.dictAnio[index] = int(aux[0])
            index += 1
        self.cursor.execute('show tables')
        tupla = self.cursor.fetchall()
        vector = list()
        for aux in self.dictAnio:
            vector.append(self.dictAnio[aux])

        for aux in tupla:
            if aux[0].count('cofrades_papeletassitio_'):
                num = aux[0][-4:]
                num = int(num)
                try:
                    if vector.index(num):
                        pass
                except ValueError:
                    #liststore.append([num])
                    self.dictAnio[len(self.dictAnio)]= num
                    index += 1
        orden = sorted(self.dictAnio.items(), key=itemgetter(1))
        
        index = 0
        for aux in orden:
            self.dictAnio[index] = aux[1]
            index +=1
        for aux in self.dictAnio:
            liststore.append([self.dictAnio[aux]])
        
        combo.set_model(liststore)
        combo.set_active(index-1)

    def clickDeleteAnio(self, data=None):
        self.widgets.get_widget('messagedialog1').show()

    def responseDialog(self, data=None, widget=None):
        self.widgets.get_widget('messagedialog1').hide()
        if widget == -5:
            self.eliminarAnio()
            
    def eliminarAnio(self):
        combo = self.widgets.get_widget('combobox1')
        num = combo.get_active()
        iteration = combo.get_active_iter()
        liststore = combo.get_model()
        anio = liststore.get_value(iteration, 0)
        borrar = True
        
        self.cursor.execute('select * from morosos where anio=%s', anio)
        tupla = self.cursor.fetchall()
        if len(tupla)>0:
            data = datetime.today().strftime("%d/%m/%y %H:%M:%S")
            self.liststorebottom.append([data, 'No se puede borrar porque existen datos de ese año', '#8A0808'])
            return False
        self.cursor.execute('show tables')
        tupla = self.cursor.fetchall()

        for aux in tupla:
            if aux[0].count('cofrades_papeletassitio_'):
                num = aux[0][-4:]
                num = int(num)
                if num == anio:
                    self.cursor.execute('select * from '+'cofrades_papeletassitio_'+str(anio))
                    tuplas2 = self.cursor.fetchall()
                    if len(tuplas2)>0:
                        data = datetime.today().strftime("%d/%m/%y %H:%M:%S")
                        self.liststorebottom.append([data, 'No se puede borrar porque existen datos de ese año', '#8A0808'])
                        borrar = False
                        return False
        
        if borrar:
            num = combo.get_active()
            liststore.remove(iteration)
            del self.dictAnio[num]
            combo.set_active(len(self.dictAnio)-1)
            data = datetime.today().strftime("%d/%m/%y %H:%M:%S")
            self.liststorebottom.append([data, 'Año eliminado correctamente', '#0B0B61'])
            self.aux.desconectar()
            self.cursor.execute('DROP TABLE IF EXISTS '+'cofrades_papeletassitio_'+str(anio))

    def comboChange(self, data=None):
        f = open('anio.txt', 'w')
        try:
            f.write(str(self.dictAnio[data.get_active()]))
            f.close()
            alin = self.widgets.get_widget('alignment1')
            test = alin.get_child()
            if (test != None):
                child = alin.get_child()
                child.destroy()

            aux = gtk.glade.XML('./glade/index.glade')
            aux.signal_autoconnect(self)
            aux.get_widget('hbox1').reparent(alin)
            self.widgets.get_widget('scrolledwindow3').hide()
            
            for i in range(1,13):
                nombre = 'button' + str(i)
                button = aux.get_widget(nombre)
                button.modify_bg(2,gtk.gdk.color_parse("#0B0B61"))
                label =  button.get_children()
                label = label[0]
                label.modify_fg(2,gtk.gdk.color_parse("blue"))
            aux.get_widget('label10').modify_fg(0,gtk.gdk.color_parse("#8A0808"))
            aux.get_widget('label1').modify_fg(0,gtk.gdk.color_parse("#8A0808"))
            aux.get_widget('label9').modify_fg(0,gtk.gdk.color_parse("#8A0808"))
            aux.get_widget('label12').modify_fg(0,gtk.gdk.color_parse("#8A0808"))
            aux.get_widget('label14').modify_fg(0,gtk.gdk.color_parse("#8A0808"))
            aux.get_widget('label16').modify_fg(0,gtk.gdk.color_parse("#8A0808"))
            aux.get_widget('label18').modify_fg(0,gtk.gdk.color_parse("#8A0808"))
            aux.get_widget('label20').modify_fg(0,gtk.gdk.color_parse("#8A0808"))
            aux.get_widget('label22').modify_fg(0,gtk.gdk.color_parse("#8A0808"))

            data = datetime.today().strftime("%d/%m/%y %H:%M:%S")
            self.liststorebottom.append([data, 'El año de gestión se ha cambiado', '#0B0B61'])
        except KeyError:
            pass
        
    def createTreeviewTables(self):
        treeview = self.widgets.get_widget('treeview3')
        self.liststore2 = gtk.ListStore(str, str)
        treeview.set_model(self.liststore2)
        
        tvcolumn = gtk.TreeViewColumn('Tablas')
        self.liststore2.append(['gtk-directory', 'Provincias'])
        self.liststore2.append(['gtk-directory', 'Municipios'])
        self.liststore2.append(['gtk-directory', 'Calles'])
        self.liststore2.append(['gtk-directory', 'Bancos'])
        treeview.append_column(tvcolumn)

        cellpb = gtk.CellRendererPixbuf()
        cell = gtk.CellRendererText()
        
        tvcolumn.pack_start(cellpb, False)
        tvcolumn.pack_start(cell, True)
        
        tvcolumn.set_attributes(cellpb, stock_id=0)
        tvcolumn.set_attributes(cell, text=1)
        
    def fillLeftFrame(self):
        treeview = self.widgets.get_widget('treeview1')

        cell = gtk.CellRendererPixbuf()
        tvcolumn = gtk.TreeViewColumn('Opciones', cell)
        tvcolumn.set_cell_data_func(cell, self.file_icon)
        
        cell.set_property('xalign', 1.0)
        
        cell = gtk.CellRendererText()        
        cell.set_property('height', 40)
        tvcolumn.pack_start(cell, True)
        tvcolumn.set_cell_data_func(cell, self.file_name)
        treeview.append_column(tvcolumn)

        self.liststore = gtk.ListStore(str,str)
        treeview.set_model(self.liststore)

        self.liststore.append(('Inicio',gtk.STOCK_HOME))        
        self.liststore.append(('Cofrades',gtk.STOCK_ABOUT))
        self.liststore.append(('Costaleros',gtk.STOCK_HELP))
        self.liststore.append(('Directivos','gtk-orientation-portrait'))
        self.liststore.append(('Autoridades','gtk-no'))
        self.liststore.append(('Sectores','gtk-jump-to'))
        self.liststore.append(('Papeletas de sitio','gtk-index'))
        self.liststore.append(('Informes','gtk-print'))
        self.liststore.append(('Gestión de tablas','gtk-select-color'))
        self.liststore.append(('Copias de seguridad','gtk-dialog-authentication'))
    
    def mierda(self):
        scrolled = self.widgets.get_widget('scrolledwindow2').get_vadjustment()
        scrolled.set_value(scrolled.get_upper() - scrolled.get_page_size()) # Ponemos la barra al final
        self.widgets.get_widget('scrolledwindow2').set_vadjustment(scrolled)

    def bottomFrame(self):
        treeview = self.widgets.get_widget('treeview2')

        cell = gtk.CellRendererText()
        
        tvcolumn = gtk.TreeViewColumn('Fecha')
        treeview.append_column(tvcolumn)
        tvcolumn.pack_start(cell, True)
        tvcolumn.add_attribute(cell, 'text', 0)
        cell.set_property("size-points",8)
        tvcolumn.set_cell_data_func(cell, self.color_rowDate)
        
        cell = gtk.CellRendererText()
        tvcolumn = gtk.TreeViewColumn('Msg')
        treeview.append_column(tvcolumn)
        tvcolumn.pack_start(cell, True)
        tvcolumn.set_cell_data_func(cell, self.color_row)
        tvcolumn.add_attribute(cell, 'text', 1)
        cell.set_property("foreground-set",True)
        cell.set_property("size-set",True)
        cell.set_property("size-points",10)
        
        data = datetime.today().strftime("%d/%m/%y %H:%M:%S")

        self.liststorebottom = gtk.ListStore(str,str,str)
        treeview.set_model(self.liststorebottom)
        self.liststorebottom.append([data, 'Inicio del programa', '#0B610B'])

    def color_rowDate(self, column, cell, model, iter):
        cell.set_property("foreground",'black')
        self.mierda()
        
    def color_row(self, column, cell, model, iter):
        cell.set_property("foreground",model.get_value(iter, 2))

    def file_name(self, column, cell, model, iter):
        cell.set_property('text', model.get_value(iter, 0))
        return

    def file_icon(self, column, cell, model, iter):
        #cell.set_property('icon-name', model.get_value(iter, 1))
        cell.set_property('xpad', 5)
        treeview = self.widgets.get_widget('treeview1')
        stock = model.get_value(iter, 1)
        pb = treeview.render_icon(stock, gtk.ICON_SIZE_MENU, None)
        cell.set_property('pixbuf', pb)
        return

    def fillTreeviewTables(self, widget, data=None):
        iterator = self.liststore2.get_iter_first()

        for i in range(4):
            self.liststore2.set_value(iterator, 0, 'gtk-directory')
            iterator = self.liststore2.iter_next(iterator)

        treeview = self.widgets.get_widget('treeview3')
        treeselection = treeview.get_selection()
        (model, iteration) = treeselection.get_selected()
        
        try:
            value = self.liststore2.get_value(iteration, 1)
            self.liststore2.set_value(iteration, 0, 'gtk-file')
            
            alin = self.widgets.get_widget('alignment1')
            test = alin.get_child()
            if (test != None):
                child = alin.get_child()
                child.destroy()
            
            if (value == 'Provincias'):
                self.showProvincia()
            if (value == 'Municipios'):
                self.showMunicipio()
            if (value == 'Calles'):
                self.showCalle()
            if (value == 'Bancos'):
                self.showBanco()
        except TypeError, e:
            print e

    def showBanco(self, data=None):
        alin = self.widgets.get_widget('alignment1')
        test = alin.get_child()
        if (test != None):
            child = alin.get_child()
            child.destroy()
            
        aux = Banco(None, self.widgets.get_widget('statusbar1'), self.liststorebottom)
        aux.caja.reparent(alin)
        aux.widgets.get_widget('statusbar1').hide()
        aux.widgets.get_widget('menubar1').hide()
        aux.widgets.get_widget('hbuttonbox3').hide()

    def showCalle(self, data=None):
        alin = self.widgets.get_widget('alignment1')
        test = alin.get_child()
        if (test != None):
            child = alin.get_child()
            child.destroy()
        
        aux = Calle(None, self.widgets.get_widget('statusbar1'), self.liststorebottom)
        aux.caja.reparent(alin)
        aux.widgets.get_widget('statusbar1').hide()
        aux.widgets.get_widget('menubar1').hide()
        aux.widgets.get_widget('hbuttonbox3').hide()

    def showMunicipio(self, data=None):
        alin = self.widgets.get_widget('alignment1')
        test = alin.get_child()
        if (test != None):
            child = alin.get_child()
            child.destroy()
        
        aux = Municipio(None, self.widgets.get_widget('statusbar1'), self.liststorebottom)
        aux.caja.reparent(alin)
        aux.widgets.get_widget('statusbar1').hide()
        aux.widgets.get_widget('menubar1').hide()
        aux.widgets.get_widget('hbuttonbox3').hide()

    def showProvincia(self, data=None):
        alin = self.widgets.get_widget('alignment1')
        test = alin.get_child()
        if (test != None):
            child = alin.get_child()
            child.destroy()
        
        aux = Provincia(None, self.widgets.get_widget('statusbar1'), self.liststorebottom)
        aux.caja.reparent(alin)
        aux.widgets.get_widget('statusbar1').hide()
        aux.widgets.get_widget('menubar1').hide()
        aux.widgets.get_widget('hbuttonbox3').hide()

    def showPapeletasSitio(self, data=None):
        alin = self.widgets.get_widget('alignment1')
        test = alin.get_child()
        if (test != None):
            child = alin.get_child()
            child.destroy()

        self.widgets.get_widget('scrolledwindow3').hide()
        self.widgets.get_widget('hseparator2').hide()        
        self.aux = PapeletaSitio(None, self.widgets.get_widget('statusbar1'), self.liststorebottom)
        aux = self.aux
        aux.caja.reparent(alin)
        aux.widgets.get_widget('statusbar1').hide()
        aux.widgets.get_widget('menubar1').hide()
        aux.widgets.get_widget('hbuttonbox3').hide()

    def showAutoridades(self, data=None):
        alin = self.widgets.get_widget('alignment1')
        test = alin.get_child()
        if (test != None):
            child = alin.get_child()
            child.destroy()
            
        self.widgets.get_widget('scrolledwindow3').hide()
        self.widgets.get_widget('hseparator2').hide()
        aux = Autoridad(None, self.widgets.get_widget('statusbar1'), self.liststorebottom)
        aux.caja.reparent(alin)
        aux.widgets.get_widget('statusbar1').hide()
        aux.widgets.get_widget('menubar1').hide()
        aux.widgets.get_widget('hbuttonbox3').hide()

    def showSectores(self, data=None):
        alin = self.widgets.get_widget('alignment1')
        test = alin.get_child()
        if (test != None):
            child = alin.get_child()
            child.destroy()
        
        self.widgets.get_widget('scrolledwindow3').hide()
        self.widgets.get_widget('hseparator2').hide()
        aux = Sector(None, self.widgets.get_widget('statusbar1'), self.liststorebottom)
        aux.caja.reparent(alin)
        aux.widgets.get_widget('statusbar1').hide()
        aux.widgets.get_widget('menubar1').hide()
        aux.widgets.get_widget('hbuttonbox3').hide()

    def showCofrades(self, data=None):
        alin = self.widgets.get_widget('alignment1')
        test = alin.get_child()
        if (test != None):
            child = alin.get_child()
            child.destroy()
            
        self.widgets.get_widget('scrolledwindow3').hide()
        self.widgets.get_widget('hseparator2').hide()
        aux = Cofrade(None, self.widgets.get_widget('statusbar1'), self.liststorebottom)
        aux.caja.reparent(alin)
        aux.widgets.get_widget('statusbar1').hide()
        aux.widgets.get_widget('menubar1').hide()
        aux.widgets.get_widget('hbuttonbox3').hide()

    def showSeguridad(self, data=None):
        alin = self.widgets.get_widget('alignment1')
        test = alin.get_child()
        if (test != None):
            child = alin.get_child()
            child.destroy()
            
        self.widgets.get_widget('scrolledwindow3').hide()
        self.widgets.get_widget('hseparator2').hide()
        aux = Seguridad(self.widgets.get_widget('statusbar1'), self.liststorebottom)
        aux.caja.reparent(alin)

    def showInformes(self, data=None):
        alin = self.widgets.get_widget('alignment1')
        test = alin.get_child()
        if (test != None):
            child = alin.get_child()
            child.destroy()
            
        self.widgets.get_widget('scrolledwindow3').hide()
        self.widgets.get_widget('hseparator2').hide()
        aux = Informe(self.widgets.get_widget('statusbar1'), self.liststorebottom)
        aux.caja.reparent(alin)

    def showDirectivos(self, data=None):
        alin = self.widgets.get_widget('alignment1')
        test = alin.get_child()
        if (test != None):
            child = alin.get_child()
            child.destroy()
            
        self.widgets.get_widget('scrolledwindow3').hide()
        self.widgets.get_widget('hseparator2').hide()
        aux = Directivo(None, self.widgets.get_widget('statusbar1'), self.liststorebottom)
        aux.caja.reparent(alin)
        aux.widgets.get_widget('statusbar1').hide()
        aux.widgets.get_widget('menubar1').hide()
        aux.widgets.get_widget('hbuttonbox3').hide()

    def showCostaleros(self, data=None):
        alin = self.widgets.get_widget('alignment1')
        test = alin.get_child()
        if (test != None):
            child = alin.get_child()
            child.destroy()
            
        self.widgets.get_widget('scrolledwindow3').hide()
        self.widgets.get_widget('hseparator2').hide()
        aux = Costalero(None, self.widgets.get_widget('statusbar1'), self.liststorebottom)
        aux.caja.reparent(alin)
        aux.widgets.get_widget('statusbar1').hide()
        aux.widgets.get_widget('menubar1').hide()
        aux.widgets.get_widget('hbuttonbox3').hide()
        
    def clickLeftFrame(self, widget, event, data=None):
        iterator = self.liststore2.get_iter_first()

        for i in range(4):
            self.liststore2.set_value(iterator, 0, 'gtk-directory')
            iterator = self.liststore2.iter_next(iterator)
            
        treeview = self.widgets.get_widget('treeview1')
        treeselection = treeview.get_selection()
        (model, iteration) = treeselection.get_selected()   
        value = self.liststore.get_value(iteration, 0)
        alin = self.widgets.get_widget('alignment1')
        test = alin.get_child()
        
        if (test != None):
            child = alin.get_child()
            child.destroy()
        
        if (value == 'Inicio'):
            self.widgets.get_widget('scrolledwindow3').hide()
            self.widgets.get_widget('hseparator2').hide()
            aux = gtk.glade.XML('./glade/index.glade')
            aux.signal_autoconnect(self)
            aux.get_widget('hbox1').reparent(alin)
            for i in range(1,13):
                nombre = 'button' + str(i)
                button = aux.get_widget(nombre)
                button.modify_bg(2,gtk.gdk.color_parse("#0B0B61"))
                label =  button.get_children()
                label = label[0]
                label.modify_fg(2,gtk.gdk.color_parse("blue"))
            aux.get_widget('label10').modify_fg(0,gtk.gdk.color_parse("#8A0808"))
            aux.get_widget('label1').modify_fg(0,gtk.gdk.color_parse("#8A0808"))
            aux.get_widget('label9').modify_fg(0,gtk.gdk.color_parse("#8A0808"))
            aux.get_widget('label12').modify_fg(0,gtk.gdk.color_parse("#8A0808"))
            aux.get_widget('label14').modify_fg(0,gtk.gdk.color_parse("#8A0808"))
            aux.get_widget('label16').modify_fg(0,gtk.gdk.color_parse("#8A0808"))
            aux.get_widget('label18').modify_fg(0,gtk.gdk.color_parse("#8A0808"))
            aux.get_widget('label20').modify_fg(0,gtk.gdk.color_parse("#8A0808"))
            aux.get_widget('label22').modify_fg(0,gtk.gdk.color_parse("#8A0808"))
            aux.get_widget('hbox1').show_all()
        if (value == 'Sectores'):
            self.showSectores()
        if (value == 'Cofrades'):
            self.showCofrades()
        if (value == 'Papeletas de sitio'):
            self.showPapeletasSitio()
        if (value == 'Autoridades'):
            self.showAutoridades()
        if (value == 'Directivos'):
            self.showDirectivos()
        if (value == 'Costaleros'):
            self.showCostaleros()
        if (value == 'Copias de seguridad'):   
            self.showSeguridad()     
        if (value == 'Informes'):   
            self.showInformes()                 
        if (value == 'Gestión de tablas'):
            aux = gtk.glade.XML('./glade/inicioTablas.glade')
            aux.get_widget('table1').reparent(alin)
            data = datetime.today().strftime("%d/%m/%y %H:%M:%S")
            self.liststorebottom.append([data, 'Inicio del gestor de tablas', '#0B610B'])
            aux.get_widget('table1').show_all()
            self.widgets.get_widget('hseparator2').show_all()
            self.widgets.get_widget('scrolledwindow3').show_all()
            
    def destroy(self, widget, data=None):
        self.desconectar()
        gtk.main_quit()

def main():
    Inicio()
    gtk.gdk.threads_init()
    gtk.gdk.threads_enter()
    gtk.main()
    gtk.gdk.threads_leave()

if __name__ == "__main__":
    sys.exit(main())
