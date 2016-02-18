import MySQLdb

def conectar_buscar():
    db=MySQLdb.connect(user="root", passwd="manolo7", db='proyecto')
    cursor = db.cursor()
    cursor.execute('select id,n_orden,n_cofrade,dni,nombre,apellido1,apellido2, sexoid_,callesId_,num, pl, pi, str_to_date(fecha_n,"%d/%m/%Y"), str_to_date(fecha_i,"%d/%m/%Y"), nota, telefono,email from cofrades');

    registros = cursor.fetchall()
    print registros
    for tupla in registros:
        cursor.execute("insert into cofrades_datospersonales values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", tupla);

    db.commit()
conectar_buscar()


