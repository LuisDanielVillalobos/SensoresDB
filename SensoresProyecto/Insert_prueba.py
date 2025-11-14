import pyodbc 
import csv
import time

cnxn = pyodbc.connect(
    r"Driver={SQL Server Native Client 11.0};"
    r"Server=DESKTOP-J4U2VS9\sqlexpress;"
    r"Database=Sensores;"
    r"Trusted_Connection=yes;"
)

cursor = cnxn.cursor()
cursor.execute('SELECT * FROM dbo.Data_Sensor')
#solo para visualizar los datos ya insertados de la DB
for row in cursor:
    print(' | '.join(str(field) for field in row))
    
filename = 'sensores.csv'
datos = []
try:
    with open(filename, 'r') as infile:
        #se usa el delimitador para separar los valores
        reader = csv.reader(infile, delimiter=',')
        for row in reader:
            #si la fila tiene exactamente 12 datos entonces
            #sabemos que son los que necesitamos 
            if len(row) == 12:
                datos.append(row)
except FileNotFoundError:
    print(f"Error: El archivo '{filename}' no fue encontrado.")
i=0
def InsertarDatos(datos):
    params = (
        #no tienen ningun id o nombre porque en el archivo son secuenciales
        datos[0].strip(),              # @macSensor varchar(17)
        int(datos[1]),                 # @capa tinyint
        int(datos[2]),                 # @no_paquete int
        float(datos[3]),               # @direccion1 float
        float(datos[4]),               # @direccion2 float
        float(datos[5]),               # @direccion3 float
        float(datos[6]),                 # @temperatura flo
        float(datos[7]),                 # @humedad flo
        float(datos[8]),               # @Q1 float
        float(datos[9]),               # @Q2 float
        float(datos[10]),              # @Q3 float
        float(datos[11])               # @Q4 float
    )
    try:
        #tomar como referencia para saber el orden de insercion
        """
        @macSensor varchar(17), 
	    @capa tinyint,
	    @no_paquete int,
	    @distancia1 float,
	    @distancia2 float,
	    @distancia3 float,
	    @temperatura float,
	    @humedad float,
	    @Q1 float,
	    @Q2 float,
	    @Q3 float,
	    @Q4 float
        """
     
        cursor.execute(
            "EXEC dbo.usp_InsertDataSensor ?,?,?,?,?,?,?,?,?,?,?,?",
            params#<----todos los parametros

        )
        cnxn.commit()
        print("Datos insertados correctamente.")
    except Exception as e:
        cnxn.rollback()#si hay algun en algun punto se cancela la insercion
        print(f"Error al insertar -> {e}")
    
    
for dato in datos:
    time.sleep(3)#delay, puede quitarse
    InsertarDatos(dato)

            
        
