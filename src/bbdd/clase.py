import MySQLdb

class Cofrade:
    def __init__(self):
        self.n_orden = None;
        self.n_cofrade = None;
        self.dni = None;
        self.nombre = None;
        self.apellido1 = None;
        self.apellido2 = None;
        self.id_sexo = None;
        self.id_direccion = None;
        self.numero = None;
        self.planta = None;
        self.piso = None;

        self.fecha_nacimiento = None;
        self.fecha_i = None;
        self.nota = None;
        self.telefono = None;
        self.email = None;
        
def conectar():
    db=MySQLdb.connect(user="root", passwd="manolo7", db='proyecto')
    cursor = db.cursor()
    cursor.execute('select * from cofrades');
    return cursor.fetchall()

hola = conectar()
for linea in hola:
    print linea
    exit()
