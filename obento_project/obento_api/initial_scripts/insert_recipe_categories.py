import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="obento-admin",
  password="Admin1234?",
  database="obento_database"
)

mycursor = mydb.cursor()

sql = '''INSERT INTO recipe_category (description) VALUES
('Arroces'),
('Bocadillos y Hamburguesas'),
('Carnes'),
('Ensaladas y Bowls'),
('Guisos'),
('Legumbres'),
('Pastas'),
('Pescado y marisco'),
('Salteado'),
('Sandwich'),
('Sopas y crema'),
('Verduras y vegetales');'''
mycursor.execute(sql)

mydb.commit()