#! /usr/bin/env python
# -*- coding: iso-8859-15 -*-
import MySQLdb

def conectar_buscar():
    db=MySQLdb.connect(user="root", passwd="manolo7", db='proyecto')
    cursor = db.cursor()

    cursor.execute('select n_orden, n_cofrade, str_to_date(fe_psitio,"%d/%m/%Y") from cofrades2005 where psitio = 1 order by str_to_date(fe_psitio,"%d/%m/%Y")');
    tuplas = cursor.fetchall()

    
    index = 1
    for tupla in tuplas:
        tupla = list(tupla)
        tupla.insert(0, index)


        cursor.execute("insert into cofrades_papeletassitio_2005 (id, n_orden, id_cofrade,fecha) values (%s, %s,%s,%s)", tupla);
        index += 1

        

    cursor.execute('select * from cofrades_papeletassitio_2005;')
    


    db.commit()

conectar_buscar()


