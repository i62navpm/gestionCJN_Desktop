#! /usr/bin/env python
# -*- coding: utf-8 -*-
from autoridades.autoridades import Autoridad
from cofrades.cofrades import Cofrade
from datetime import datetime
from win32com.client import Dispatch
import MySQLdb
import gtk
import gtk.glade
import os
import glob
import pygtk
import re
import sys
import time
import shutil

pygtk.require('2.0')

class Informe():
    def __init__(self, statusbar=None, panel=None):
        self.widgets = gtk.glade.XML('../informes/informes2.glade')
        self.widgets.signal_autoconnect(self)

        self.caja = self.widgets.get_widget('vbox1')
        self.window = self.widgets.get_widget('window1')

        self.window.connect("destroy", self.destroy)
        self.cursor = self.conectar()
        
        self.handler_id = dict()
        
        self.widgets.get_widget('combobox1').set_active(0)
        self.widgets.get_widget('combobox2').set_active(0)
        self.widgets.get_widget('combobox3').set_active(0)
        self.widgets.get_widget('combobox4').set_active(0)
        self.widgets.get_widget('combobox5').set_active(0)
        self.widgets.get_widget('combobox6').set_active(0)
        
        
        self.handler_id["combobox1"] = self.widgets.get_widget('combobox1').connect("changed", self.resetCombo, "combobox1")
        self.handler_id["combobox2"] = self.widgets.get_widget('combobox2').connect("changed", self.resetCombo, "combobox2")
        self.handler_id["combobox3"] = self.widgets.get_widget('combobox3').connect("changed", self.resetCombo, "combobox3")
        self.handler_id["combobox4"] = self.widgets.get_widget('combobox4').connect("changed", self.resetCombo, "combobox4")
        self.handler_id["combobox5"] = self.widgets.get_widget('combobox5').connect("changed", self.resetCombo, "combobox5")
        self.handler_id["combobox6"] = self.widgets.get_widget('combobox6').connect("changed", self.resetCombo, "combobox6")
        
        self.dictCofrades={1: ('../informes/cofrades/registroc.rpt',None),
                           2: ('../informes/cofrades/cofradesporsectores.rpt',None),
                           3: ('../informes/cofrades/cofradespendientesdepago.rpt',None),
                           4: ('../informes/cofrades/recibospendientes/recibospendientes.rpt',None),
                           5: ('../informes/cofrades/menores1anio/menores.rpt','..\\informes\\cofrades\\menores1anio\\carta.docx'),
                           6: ('../informes/cofrades/circular/circular.rpt','..\\informes\\cofrades\\circular\\carta_circular.docx'),
                           7: ('../informes/cofrades/censo.rpt',None),
                           8: ('../informes/cofrades/sobrescofrades.rpt',None)
        }
        
        self.dictLoterias={1: ('../informes/loterias/cartaloteria/sbloteria.rpt','..\\informes\\loterias\\cartaloteria\\carta.docx'),
                           2: ('../informes/loterias/cartaloteriasindetalle/sbloteria.rpt','..\\informes\\loterias\\cartaloteriasindetalle\\carta.docx'),
                           3: ('../informes/loterias/liqbancossindetalle.rpt',None),
                           4: ('../informes/loterias/liqbancoscondetalle.rpt',None),
                           5: ('../informes/loterias/CorreosLoteria.rpt',None),
                           6: ('../informes/loterias/liqbancosExpL.rpt',None),
                           7: ('../informes/loterias/remesaNorma19.rpt',None)
        }
        
        self.dictRecibos ={1: ('../informes/recibos/recibos/recibosec.rpt','..\\informes\\recibos\\recibos\\texto_recibo.docx'),
                           2: ('../informes/recibos/liqbancos_recibos2.rpt', None),
                           3: ('../informes/recibos/liqbancosExpL_recibos.rpt',None),                          
                           4: ('../informes/recibos/remesaNorma19.rpt',None)
        }
        
        self.dictPapeletas={1: ('../informes/papeletas/cirpapeleta2.rpt', None),
                            2: ('../informes/papeletas/cirpapeleta2blanco.rpt', None),
                            3: ('../informes/papeletas/papeletalist.rpt',None)                          
        }
        
        self.dictAutoridades={1: ('../informes/autoridades/carta_autoridades/cartaautoridad.rpt', '..\\informes\\autoridades\\carta_autoridades\\carta.docx')                                                    
        }
        
        self.dictCostaleros={'Titular':{1:('../informes/costaleros/titulares/carta/cartacostalerostalla2.rpt','..\\informes\\costaleros\\titulares\\carta\\carta_titular.docx'),
                                        2:('../informes/costaleros/titulares/listcostalerostitular.rpt',None),
                                        3:('../informes/costaleros/titulares/titularescondireccion.rpt',None)
                                        },
                           'Aspirante':{1:('../informes/costaleros/aspirantes/carta/cartacostalerosaspirante.rpt','..\\informes\\costaleros\\aspirantes\\carta\\carta_aspirante.docx'),
                                        2:('../informes/costaleros/aspirantes/listcostaleroaspirante.rpt',None),
                                        3:('../informes/costaleros/aspirantes/aspirantescondireccion.rpt',None)
                                        }
                             }                                      
        
        
        self.dictInformes={'combobox1': self.dictCofrades,
                           'combobox2': self.dictLoterias,
                           'combobox3': self.dictRecibos,
                           'combobox4': self.dictPapeletas,
                           'combobox5': self.dictCostaleros,
                           'combobox6': self.dictAutoridades}
        
        self.widgets.get_widget('button1').set_property('sensitive', False)
        self.widgets.get_widget('button2').set_property('sensitive', False)
        self.widgets.get_widget('button3').set_property('sensitive', False)
        self.widgets.get_widget('button4').set_visible(False)
        self.widgets.get_widget('button5').set_property('sensitive', False)
        self.widgets.get_widget('button6').set_property('sensitive', False)
        
        self.informeActivo = None
        self.AutorCof = "Cofrades"
        
        f = open('../inicio/anio.txt', 'r')
        anio = f.read()
        f.close()
        
        self.tabla = 'cofrades_papeletassitio_'+anio
        
        self.cursor.execute('alter view vista_papeletas (id, fecha,n_orden) as select id_cofrade, fecha, n_orden from '+ self.tabla+' order by n_orden')
        
        if (statusbar):
            self.statusbar = statusbar
        else:
            self.statusbar = gtk.Statusbar()
        if (panel):
            self.panel = panel
        else:
            self.panel = gtk.ListStore(str, str, str)

        self.statusbar.push(1,'Seleccione un informe')
        self.insertPanel('INFO','Abierta herramienta de informes')

        self.widgets.get_widget('entry1').set_property('sensitive', False)
        self.widgets.get_widget('entry3').set_property('sensitive', False)
        
        self.cursor.execute('select max(id) from sectores')
        tupla = self.cursor.fetchone()
        self.widgets.get_widget('spinbutton1').set_range(1,tupla[0])
        
        
        self.opcion = -1
        
        
        
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

    def resetCombo(self, data, widget):
        
        for key in self.handler_id.keys():
            combo = self.widgets.get_widget(key)
            
            if widget != key:
                boton = 'button'+ str(combo.get_name()[-1])
                self.widgets.get_widget(boton).set_property('sensitive', False)
                combo.handler_block(self.handler_id[key])
                combo.set_active(0)
                combo.handler_unblock(self.handler_id[key])
                combo.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse("white"))
                
            else:
                try:
                    combo.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse("yellow"))
                    print combo.get_name()
                    if combo.get_name() != "combobox5":
                        self.informeActivo = self.dictInformes[combo.get_name()][combo.get_active()]
                    else:
                        if self.widgets.get_widget('radiobutton1').get_active():
                            self.informeActivo = self.dictCostaleros["Titular"][combo.get_active()]
                        else:
                            self.informeActivo = self.dictCostaleros["Aspirante"][combo.get_active()]
                    
                    print self.informeActivo
                    self.checkModificarCarta(combo)
                    self.checkAutCof()
                except KeyError:
                    combo.set_active(0)
                    combo.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse("white"))
                    self.informeActivo = None
                
    def checkAutCof(self):
        self.widgets.get_widget('entry1').set_text("")
        self.widgets.get_widget('entry3').set_text("")
        if self.informeActivo ==('../informes/autoridades/carta_autoridades/cartaautoridad.rpt', '.\\autoridades\\carta_autoridades\\carta.docx'):
            self.AutorCof = "autoridades"
            self.widgets.get_widget('entry1').set_visible(False)
            self.widgets.get_widget('entry3').set_visible(True)
        else:
            self.AutorCof = "cofrades"
            self.widgets.get_widget('entry3').set_visible(False)
            self.widgets.get_widget('entry1').set_visible(True)

            
    def checkModificarCarta(self, combo):
        boton = 'button'+ str(combo.get_name()[-1])
        if combo.get_name() != 'combobox5':
            if self.dictInformes[combo.get_name()][combo.get_active()][1] == None:
                self.widgets.get_widget(boton).set_property('sensitive', False)
            else:
                self.widgets.get_widget(boton).set_property('sensitive', True)
        else:
            if self.widgets.get_widget('radiobutton1').get_active():
                print "titulares"
                if self.dictCostaleros["Titular"][combo.get_active()][1] == None:
                    self.widgets.get_widget(boton).set_property('sensitive', False)
                else:
                    self.widgets.get_widget(boton).set_property('sensitive', True)
                
            else:
                print "aspirantes"
                if self.dictCostaleros["Aspirante"][combo.get_active()][1] == None:
                    self.widgets.get_widget(boton).set_property('sensitive', False)
                else:
                    self.widgets.get_widget(boton).set_property('sensitive', True)
    
    def clearCombo(self, data):
        key = data.get_name()
        boton = 'button'+ str(data.get_name()[-1])
        self.widgets.get_widget(boton).set_property('sensitive', False)
        data.handler_block(self.handler_id[key])
        data.set_active(0)
        data.handler_unblock(self.handler_id[key])
        data.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse("white"))
        self.informeActivo = None
        
    def modificarcarta(self, data):
        os.startfile(self.informeActivo[1])


    def cambio2(self, data): 
        aux = data.get_name()   
        if aux == 'radiobutton15':
            self.widgets.get_widget('spinbutton1').set_property('sensitive', True)
            self.widgets.get_widget('entry1').set_property('sensitive', False)
            self.widgets.get_widget('entry3').set_property('sensitive', False)
            self.widgets.get_widget('radiobutton12').set_property('sensitive', True)
            self.widgets.get_widget('radiobutton13').set_property('sensitive', True)
            self.widgets.get_widget('radiobutton16').set_property('sensitive', True)
        elif aux == 'radiobutton14':
            self.widgets.get_widget('spinbutton1').set_property('sensitive', False)
            self.widgets.get_widget('entry1').set_property('sensitive', False)
            self.widgets.get_widget('entry3').set_property('sensitive', False)
        else:
            self.widgets.get_widget('spinbutton1').set_property('sensitive', False)
            self.widgets.get_widget('entry1').set_property('sensitive', True)
            self.widgets.get_widget('entry3').set_property('sensitive', True)
            self.widgets.get_widget('radiobutton12').set_property('sensitive', False)
            self.widgets.get_widget('radiobutton13').set_property('sensitive', False)
            self.widgets.get_widget('radiobutton16').set_property('sensitive', False)

    def showCofrade(self, widget=None, event=None, data=None):
        if (event==1):
            aux = Cofrade(widget)
            aux.window.set_modal(True)
            aux.window.present()
        if (event==0):
            widget.set_text('')

    def showAutoridad(self, widget=None, event=None, data=None):
        if (event==1):
            aux = Autoridad(widget)
            aux.window.set_modal(True)
            aux.window.present()
        if (event==0):
            widget.set_text('')
    
    def searchCofrade(self, widget=None, event=None, data=None):
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
            self.widgets.get_widget('entry1').set_text(nombre_completo)
        else:
            self.widgets.get_widget('entry1').set_text('')

    def searchAutoridad(self, widget=None, event=None, data=None):
        
        id = self.widgets.get_widget('entry4').get_text()
        self.cursor.execute('select nombre, apellido1, apellido2 from autoridades where id=%s', id)
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
            
    def liqBancosD(self, radio, modalidad):
        if (radio.get_name() == 'radiobutton17') and (modalidad == 'Domiciliados'):
            return True
        else:
            return False

    def liqRecibosD(self, radio, modalidad):
        if (radio.get_name() == 'radiobutton24') and (modalidad == 'Domiciliados'):
            return True
        else:
            return False

    def showCarpetas(self, widget=None, event=None, data=None):
        aux = self.widgets.get_widget('filechooserdialog1')
        aux.set_modal(True)
        aux.present()
        
    
    def acceptCarpeta(self, widget=None):
        aux = widget.get_filename()
        if aux != None:
            nom_fich_rpt = os.path.realpath(self.informeActivo[0])
            aplicacion = Dispatch('CrystalRunTime.Application')
            informe = aplicacion.OpenReport(nom_fich_rpt)
            if informe.HasSavedData: informe.DiscardSavedData()
            nom_fich_txt = os.path.realpath('../informes/temp/Remesa.q19')
            informe.ExportOptions.DiskFileName = nom_fich_txt
            informe.ExportOptions.DestinationType = '1'
            informe.ExportOptions.FormatType = '8'
            informe.Export(False)
            shutil.move(nom_fich_txt,aux)
            widget.hide()
        else:
            pass
    
    def hidefilechooser(self, widget=None):        
        widget.hide()
    
    def exportar(self, data):
        self.opcion=2
        if self.informeActivo ==('../informes/cofrades/censo.rpt',None):
            self.showWindow2()
        else:

            mod = self.modalidad()
            num = self.sectores()
            cof = self.cofrades()
            ord = self.orden()
            
            self.cursor.execute('update filtrado4 set tipo=%s where id=0', ord)

            
            if cof != 'Error' and cof != False:
                self.cursor.execute('update filtrado3 set filtrado=True, n_orden=%s where id=0', cof)
            elif cof == False:
                self.cursor.execute('update filtrado3 set filtrado=False where id=0')
            else:
                return False
            
            if num:
                self.cursor.execute('update filtrado set filtrado=True, n_sector=%s where id=0', num)
            else:
                self.cursor.execute('update filtrado set filtrado=False where id=0')
    
            if mod == 'Domiciliados':
                self.cursor.execute('update filtrado2 set filtrado="Domiciliar" where id=0')
                
            elif mod == 'Sin domiciliar':
                self.cursor.execute('update filtrado2 set filtrado="Sin domiciliar" where id=0')
            else:
                self.cursor.execute('update filtrado2 set filtrado="Ambos" where id=0')
    
            """
            if not self.liqBancosD(button, mod):
                nom_fich_rpt = os.path.realpath(self.dictReports[button.get_name()])
            else:
                nom_fich_rpt = os.path.realpath(self.dictReports['radiobutton17D'])
            
            if not self.liqRecibosD(button, mod):
                nom_fich_rpt = os.path.realpath(self.dictReports[button.get_name()])
            else:
                nom_fich_rpt = os.path.realpath(self.dictReports['radiobutton24D'])
            """
            
            nom_fich_rpt = os.path.realpath(self.informeActivo[0])
            aplicacion = Dispatch('CrystalRunTime.Application')
            informe = aplicacion.OpenReport(nom_fich_rpt)
            if informe.HasSavedData: informe.DiscardSavedData()
            
            if self.informeActivo ==('../informes/loterias/remesaNorma19.rpt',None) or self.informeActivo ==('../informes/recibos/remesaNorma19.rpt',None):
                self.showCarpetas()
            else:
                informe.ExportOptions.DestinationType = '1'
                informe.ExportOptions.FormatType = '31'
                informe.Export(True)
        
    def visualizar(self, data):
        self.opcion=1
        
        if self.informeActivo ==('../informes/cofrades/censo.rpt',None):
            self.showWindow2()
        else:
            mod = self.modalidad()
            num = self.sectores()
            cof = self.cofrades()
            ord = self.orden()
            
            self.cursor.execute('update filtrado4 set tipo=%s where id=0', (ord,))
            
            if cof != 'Error' and cof != False:
                self.cursor.execute('update filtrado3 set filtrado=True, n_orden=%s where id=0', cof)
            elif cof == False:
                self.cursor.execute('update filtrado3 set filtrado=False where id=0')
            else:
                return False
            
            if num:
                self.cursor.execute('update filtrado set filtrado=True, n_sector=%s where id=0', num)
            else:
                self.cursor.execute('update filtrado set filtrado=False where id=0')
    
            if mod == 'Domiciliados':
                self.cursor.execute('update filtrado2 set filtrado="Domiciliar" where id=0')
       
            elif mod == 'Sin domiciliar':
                self.cursor.execute('update filtrado2 set filtrado="Sin domiciliar" where id=0')
            else:
                self.cursor.execute('update filtrado2 set filtrado="Ambos" where id=0')
            """
            if not self.liqBancosD(button, mod):
                nom_fich_rpt = os.path.realpath(self.dictReports[button.get_name()])
            else:
                nom_fich_rpt = os.path.realpath(self.dictReports['radiobutton17D'])
            
            if not self.liqRecibosD(button, mod):
                nom_fich_rpt = os.path.realpath(self.dictReports[button.get_name()])
            else:
                nom_fich_rpt = os.path.realpath(self.dictReports['radiobutton24D'])
            """
            
            nom_fich_rpt = os.path.realpath(self.informeActivo[0])
            print nom_fich_rpt
            nom_fich_pdf = os.path.realpath('../informes/temp/'+str(int(time.time()))+'.pdf')
            aplicacion = Dispatch('CrystalRunTime.Application')
            informe = aplicacion.OpenReport(nom_fich_rpt)
            if informe.HasSavedData: informe.DiscardSavedData()
            
            informe.ExportOptions.DiskFileName = nom_fich_pdf
            informe.ExportOptions.DestinationType = '1'
            informe.ExportOptions.FormatType = '31'
            informe.Export(False)
            os.startfile(nom_fich_pdf)
        
    def imprimir(self, data):
        self.opcion = 0
        
        if self.informeActivo ==('../informes/cofrades/censo.rpt',None):
            self.showWindow2()
        else:
            mod = self.modalidad()
            num = self.sectores()
            cof = self.cofrades()
            ord = self.orden()
            
            self.cursor.execute('update filtrado4 set tipo=%s where id=0', ord)
            
            if cof != 'Error' and cof != False:
                self.cursor.execute('update filtrado3 set filtrado=True, n_orden=%s where id=0', cof)
            elif cof == False:
                self.cursor.execute('update filtrado3 set filtrado=False where id=0')
            else:
                return False
            
            if num:
                self.cursor.execute('update filtrado set filtrado=True, n_sector=%s where id=0', num)
            else:
                self.cursor.execute('update filtrado set filtrado=False where id=0')
    
            if mod == 'Domiciliados':
                self.cursor.execute('update filtrado2 set filtrado="Domiciliar" where id=0')
    
            elif mod == 'Sin domiciliar':
                self.cursor.execute('update filtrado2 set filtrado="Sin domiciliar" where id=0')
            else:
                self.cursor.execute('update filtrado2 set filtrado="Ambos" where id=0')
            """
            if not self.liqBancosD(button, mod):
                nom_fich_rpt = os.path.realpath(self.dictReports[button.get_name()])
            else:
                nom_fich_rpt = os.path.realpath(self.dictReports['radiobutton17D'])
            
            if not self.liqRecibosD(button, mod):
                nom_fich_rpt = os.path.realpath(self.dictReports[button.get_name()])
            else:
                nom_fich_rpt = os.path.realpath(self.dictReports['radiobutton24D'])
            """
            nom_fich_rpt = os.path.realpath(self.informeActivo[0])
            aplicacion = Dispatch('CrystalRunTime.Application')
            informe = aplicacion.OpenReport(nom_fich_rpt)
            if informe.HasSavedData: informe.DiscardSavedData()
            
            informe.PrintOut(promptUser=True)
    
    def borraFecha(self, widget=None, event=None, data=None):
        if (event==0):
            widget.set_text('')
    
    def cambiarFecha(self, data=None):
        year, month, day = self.widgets.get_widget('calendar1').get_date()
        entry = self.widgets.get_widget('entry17')
        month = month + 1
        if (len(str(month)) == 1):
            month = '0'+str(month)
        fecha = str(day)+'/'+str(month)+'/'+str(year)
        entry.set_text(fecha)

    def verifyFecha(self, data=None):
        fecha = self.widgets.get_widget('entry17').get_text()
        if (str(fecha) == '' or str(fecha) == 'dd/mm/aaaa'):
            self.error('El campo fecha de baja no puede estar vacío')
            
        elif (not re.match('(0?[1-9]|[12][0-9]|3[01])\/(0?[1-9]|1[012])\/[0-9]{4}', str(fecha))):
                self.error('Introduzca una fecha en un formato válido (dd/mm/aaaa).')
        else:  
            
            fecha = self.ajustarFecha(fecha)
            
            self.cursor.execute('update fecha_votos set fecha=%s where id = 0', fecha)
            self.hideWindow2()
            
            num = self.sectores()
            cof = self.cofrades()
            ord = self.orden()
            
            self.cursor.execute('update filtrado4 set tipo=%s where id=0', ord)
            
            if cof != 'Error' and cof != False:
                self.cursor.execute('update filtrado3 set filtrado=True, n_orden=%s where id=0', cof)
            elif cof == False:
                self.cursor.execute('update filtrado3 set filtrado=False where id=0')
            else:
                return False
            
            if num:
                self.cursor.execute('update filtrado set filtrado=True, n_sector=%s where id=0', num)
            else:
                self.cursor.execute('update filtrado set filtrado=False where id=0')
    
            
            nom_fich_rpt = os.path.realpath(self.informeActivo[0])

            aplicacion = Dispatch('CrystalRunTime.Application')
            informe = aplicacion.OpenReport(nom_fich_rpt)
            if informe.HasSavedData: informe.DiscardSavedData()
            
            if self.opcion==0:
                informe.PrintOut(promptUser=True)
            elif self.opcion==1:
                nom_fich_pdf = os.path.realpath('../informes/temp/'+str(int(time.time()))+'.pdf')
                informe.ExportOptions.DiskFileName = nom_fich_pdf
                informe.ExportOptions.DestinationType = '1'
                informe.ExportOptions.FormatType = '31'
                informe.Export(False)
                os.startfile(nom_fich_pdf)
            else:
                informe.ExportOptions.DestinationType = '1'
                informe.ExportOptions.FormatType = '31'
                informe.Export(True)
    
    def ajustarFecha(self, fecha):
        day, month, year = fecha.split('/')

        fecha = year+'-'+month+'-'+day
        return fecha
    
    def hideWindow2(self, data=None):
        self.widgets.get_widget('window2').hide()
    
    def showWindow2(self, data=None):
        self.widgets.get_widget('entry17').set_text('dd/mm/aaaa')
        fecha = datetime.today().strftime("%d/%m/%Y")
        day, month, year = fecha.split('/')
        self.widgets.get_widget('calendar1').select_month(int(month)-1, int(year))
        self.widgets.get_widget('calendar1').select_day(int(day))
        self.widgets.get_widget('window2').show()
    
    def encontrar(self):
        grupo = self.widgets.get_widget('radiobutton8').get_group()
        for aux in grupo:
            if aux.get_active():
                return aux

    def modalidad(self):
        grupo = self.widgets.get_widget('radiobutton12').get_group()
        for aux in grupo:
            if aux.get_active():
                return aux.get_label()

    def sectores(self):
        grupo = self.widgets.get_widget('radiobutton14').get_group()
        for aux in grupo:
            if aux.get_active():
                if aux.get_name()=='radiobutton14':
                    return False
                else:
                    return int(self.widgets.get_widget('spinbutton1').get_value())
    
    def cofrades(self):
        grupo = self.widgets.get_widget('radiobutton14').get_group()
        for aux in grupo:
            if aux.get_active():
                if aux.get_name()=='radiobutton20':
                    try:
                        if self.AutorCof == "autoridades":
                            print "autoridaderrrrs"
                            return(int(self.widgets.get_widget('entry4').get_text()))
                        else:
                            return(int(self.widgets.get_widget('entry2').get_text()))
                    except ValueError:
                        self.error('Introduzca un cofrade')
                        return 'Error'
                else:
                    return False
    
    def orden(self):
        grupo = self.widgets.get_widget('radiobutton3').get_group()
        for aux in grupo:
            if aux.get_active():
                return unicode(aux.get_label(), 'utf 8')
    
    def error(self, msg):
        self.insertPanel('ERROR', msg)

    
    def destroy(self, widget, data=None):
        for pdf in glob.glob('../informes/temp/*.pdf'):
            os.remove(pdf)
        
        self.desconectar()
        self.window.destroy()
    
    def conectar(self):
        self.db = MySQLdb.connect(user="root", passwd="admin", db='proyecto')
        return self.db.cursor()

    def desconectar(self):
        self.db.close()
  
def main():
    Informe()
    gtk.gdk.threads_init()
    gtk.gdk.threads_enter()
    gtk.main()
    gtk.gdk.threads_leave()

if __name__ == "__main__":
    sys.exit(main())
