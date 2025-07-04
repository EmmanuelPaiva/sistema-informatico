create table usuarios(
    id serial primary key,
    nombre varchar(25) not null,
    contrasena varchar(255) not null,
    email varchar(150),
    rol VARCHAR(20) NOT NULL CHECK (rol IN ('admin', 'vendedor', 'jefe', 'empleado'))
);
create table proveedores(
    id_proveedor serial primary key,
    nombre varchar(30),
    telefono varchar(20) not null default '000000000',
    direccion varchar(50)
);
create table empleados(
    id serial primary key,
    nombre varchar(25) not null,
    edad int check (edad >= 18),
    salario decimal(10, 2),
    fecha_contratacion date default (current_date)
    
);
create table clientes(
    id serial primary key,
    nombre varchar(20) not null,
    email varchar(100) not null,
    telefono varchar(15) not null default '000000000'
);
DROP TABLE IF EXISTS productos CASCADE;

CREATE TABLE productos (
    id_producto serial PRIMARY KEY,
    categoria varchar(25) NOT NULL,
    nombre varchar(50) NOT NULL,
    precio_venta float NOT NULL,
    stock_actual int NOT NULL,
    costo_unitario decimal(10,2) NOT NULL,
    id_proveedor INTEGER REFERENCES proveedores(id_proveedor)
);

create table ventas(
    id_venta serial primary key,
    id_cliente int references clientes(id),
    total_venta float not null,
    fecha_venta date default(current_date)
);
CREATE TABLE ventas_detalle (
    id_detalle SERIAL PRIMARY KEY,
    id_venta INTEGER REFERENCES ventas(id_venta),
    id_producto INTEGER REFERENCES productos(id_producto),
    cantidad INTEGER NOT NULL CHECK (cantidad > 0),
    precio_unitario DECIMAL(10,2) NOT NULL
);
CREATE TABLE inventario (
    id_inventario SERIAL PRIMARY KEY,
    id_producto INTEGER REFERENCES productos(id_producto),
    stock_actual INTEGER NOT NULL,
    stock_minimo INTEGER DEFAULT 0,
    ubicacion VARCHAR(50)
);
CREATE TABLE movimientos_stock (
    id_movimiento SERIAL PRIMARY KEY,
    id_producto INTEGER REFERENCES productos(id_producto),
    tipo_movimiento VARCHAR(20) CHECK (tipo_movimiento IN ('entrada', 'salida', 'ajuste')),
    cantidad INTEGER NOT NULL,
    motivo TEXT,
    fecha TIMESTAMP DEFAULT current_timestamp
);
CREATE TABLE compras (
    id_compra SERIAL PRIMARY KEY,
    id_proveedor INTEGER REFERENCES proveedores(id_proveedor),
    fecha DATE NOT NULL DEFAULT current_date,
    factura VARCHAR(50),
    medio_pago VARCHAR(30),
    estado VARCHAR(15) CHECK (estado IN ('pendiente', 'pagado')) NOT NULL
);
CREATE TABLE compras_detalle (
    id_detalle SERIAL PRIMARY KEY,
    id_compra INTEGER REFERENCES compras(id_compra),
    id_producto INTEGER REFERENCES productos(id_producto),
    cantidad INTEGER NOT NULL CHECK (cantidad > 0),
    precio_unitario DECIMAL(10,2) NOT NULL
);
create table obras(
    id_obra serial primary key,
    id_cliente INTEGER REFERENCES clientes(id),
    nombre varchar(50) not null,
    estado varchar(10) CHECK (estado IN ('en proceso', 'finalizada', 'cancelada')) not null,
    fecha_inicio date not null,
    fecha_fin date not null,
    responsable INTEGER references empleados(id),
    presupuesto decimal(15, 2) not null
);

create function insertar_cliente(
    nombre varchar(20),
    email varchar(150),
    telefono varchar(15) default '000000000'
)
returns void as $$
begin
    insert into clientes(nombre, email, telefono) values(nombre, email, telefono);
    end;
$$ Language plpgsql;

