#! /usr/bin/env python
# -*- coding: utf-8 -*-
import pygtk
pygtk.require('2.0')
import gtk
import gtk.glade
import sys
from datetime import datetime
import os
import gzip

class Seguridad():
    def __init__(self, statusbar=None, panel=None):
        self.widgets = gtk.glade.XML('../seguridad/seguridad.glade')
        self.widgets.signal_autoconnect(self)

        self.caja = self.widgets.get_widget('vbox1')
        self.window = self.widgets.get_widget('window1')
        
        if (statusbar):
            self.statusbar = statusbar
        else:
            self.statusbar = gtk.Statusbar()
        if (panel):
            self.panel = panel
        else:
            self.panel = gtk.ListStore(str, str, str)
        
        self.window.connect("destroy", self.destroy)
        self.statusbar.push(1,'Realice copias de seguridad')
        self.insertPanel('INFO','Abierto gestor de copias de seguridad')

    def showCarpetas(self, widget=None, event=None, data=None):
        if (event==1):
            aux = self.widgets.get_widget('filechooserdialog1')
            aux.set_modal(True)
            aux.present()
        if (event==0):
            widget.set_text('')

    def showArchivos(self, widget=None, event=None, data=None):
        if (event==1):
            aux = self.widgets.get_widget('filechooserdialog2')
            aux.set_modal(True)
            aux.present()
        if (event==0):
            widget.set_text('')

    def acceptCarpeta(self, widget=None):
        self.widgets.get_widget('entry2').set_text(widget.get_filename())
        widget.hide()

    def acceptArchivo(self, widget=None):
        ruta = widget.get_filename()
        fichero = os.path.basename(ruta)
        extension = os.path.splitext(fichero)
        if extension[1] != '.gz':
            self.error('Seleccione un fichero válido con extensión .sql.gz')
            return False
        self.widgets.get_widget('entry3').set_text(ruta)
        widget.hide()

    def acceptCopia(self, widget=None):
        
            pagina = self.widgets.get_widget('notebook1').get_current_page()
            
            if pagina == 0:
                nombre = self.widgets.get_widget('entry1').get_text()
                
                ruta = self.widgets.get_widget('entry2').get_text()
                
                temp = "..\\seguridad\\temporal.sql"    
                if nombre == '':
                    self.error('Intruduzca un nombre para el fichero.')
                    return False
                if ruta == '':
                    self.error('Intruduzca un nombre para el fichero.')            
                    return False
                nombre += '.sql.gz'
                
                ruta = ruta+"\\"+nombre
                
                
                self.insertPanel('INFO','Generación del fichero SQL')
                os.system('mysqldump --opt --password=admin --user=root proyecto > '+temp)
                self.insertPanel('OK','Generación del fichero SQL completada')
                self.insertPanel('INFO','Comprimiendo fichero SQL')
                self.comprimir(temp, ruta)
                self.insertPanel('OK','Compresión realizada')
                #os.system('"C:\\Program Files\\MySQL\\MySQL Server 5.5\\bin\\mysqldump.exe" --opt --password=admin --user=root proyecto > '+ruta)
                self.destroy(self.window)
                self.insertPanel('OK','Creación correcta de la copia de seguridad')
            if pagina == 1:
                temp = "..\\seguridad\\temporal2.sql"
                ruta = self.widgets.get_widget('entry3').get_text()
                self.insertPanel('INFO','Descomprimiendo fichero SQL')
                self.descomprimir(ruta, temp)
                self.insertPanel('OK','Descompresión realizada')
                if ruta == '':
                    self.error('Intruduzca un nombre para el fichero.')            
                    return False
                os.system('mysql.exe --password=admin --user=root proyecto < '+temp)
                self.destroy(self.window)
                self.insertPanel('OK','Restauración completa de la copia de seguridad')

    def comprimir (self, origen, destino):
        f_in = open(origen, 'rb')
        f_out = gzip.open(destino, 'wb')
        f_out.writelines(f_in)
        f_out.close()
        f_in.close()
    
    def descomprimir (self, origen, destino):
        print origen
        f_in = gzip.open(origen, 'rb')
        f_out = open(destino, 'wb')
        f_out.writelines(f_in)
        f_out.close()
        f_in.close()
                    
    def deleteWindow(self, widget, data=None):
        widget.hide()
        return True

    def hidefilechooser(self, widget=None):        
        widget.hide()

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
    
    def destroy(self, widget, data=None):
        self.window.destroy()

    def error(self, msg):
        self.insertPanel('ERROR', msg)
        dialog = self.widgets.get_widget('messagedialog1')
        dialog.format_secondary_text(str(msg))
        dialog.show()
        
def main():
    Seguridad()
    gtk.gdk.threads_init()
    gtk.gdk.threads_enter()
    gtk.main()
    gtk.gdk.threads_leave()

if __name__ == "__main__":
    sys.exit(main())
