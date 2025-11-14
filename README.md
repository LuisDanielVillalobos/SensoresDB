# SensoresDB 
Requisitos para ejecucion python
-Python 3.8
carpetas con los archivos
y las librerias
--PySide6
--pyodbc
--matplotlib

Requisitos base de datos
la conectionstring depende enteramente del servidor o base que se utilice, se tendra que declarar en Insert_prueba.py, y en Graficaslogica.py
        connection_string = (
            r"Driver={SQL Server Native Client 11.0};"
            r"Server=DESKTOP-J4U2VS9\sqlexpress;"
            r"Database=Sensores;"
            r"Trusted_Connection=yes;"
        )
-Tabla con la estructura proporcionada: Data_Sensor
-Procedimiento para insertar: usp_InsertDataSensor
Para esto solo ejecutar los scripts con su estructura en una nueva query o consulta

Insert_prueba No se ejecuta junto con el programa, se corre en una terminal separada o de manera paralela a la ejecucion se las graficas
![diagrama](https://github.com/user-attachments/assets/0dec1ed6-9990-4c82-a499-727016020d11)
