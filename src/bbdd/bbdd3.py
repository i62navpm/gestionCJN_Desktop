#! /usr/bin/env python
# -*- coding: utf-8 -*-
import MySQLdb

def conectar_buscar():
    db=MySQLdb.connect(user="root", passwd="admin", db='proyecto')
    cursor = db.cursor()
          
    cursor.execute("CREATE TABLE IF NOT EXISTS `gasto_enviopostal` (`id` int(11) NOT NULL DEFAULT 0,`precio` float NOT NULL DEFAULT 3,PRIMARY KEY (`id`)) ENGINE=MyISAM DEFAULT CHARSET=latin1 COLLATE=latin1_spanish_ci;")
    cursor.execute("INSERT INTO `proyecto`.`gasto_enviopostal`(`id`,`precio`)VALUES(0,3);")
    db.commit()
conectar_buscar()
raw_input("Actualizada la base de datos.\nPulsa intro para salir")
