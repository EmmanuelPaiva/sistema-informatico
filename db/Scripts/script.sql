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
ALTER TABLE productos ALTER COLUMN categoria DROP NOT NULL;
ALTER TABLE productos ALTER COLUMN costo_unitario DROP NOT NULL;
ALTER TABLE productos ADD COLUMN descripcion varchar(50);

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
    medio_pago  VARCHAR(30) NOT NULL,
    total_compra  NUMERIC(12, 2) NOT NULL
);
ALTER TABLE compras
ADD COLUMN total_compra NUMERIC(12, 2);

CREATE OR REPLACE FUNCTION actualizar_total_compra()
RETURNS TRIGGER AS $$
DECLARE
    id_compra_actual INTEGER;
BEGIN
    IF TG_OP = 'DELETE' THEN
        id_compra_actual := OLD.id_compra;
    ELSE
        id_compra_actual := NEW.id_compra;
    END IF;

    UPDATE compras
    SET total_compra = (
        SELECT COALESCE(SUM(subtotal), 0)
        FROM compra_detalles
        WHERE id_compra = id_compra_actual
    )
    WHERE id_compra = id_compra_actual;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS tg_actualizar_total ON compra_detalles;

CREATE TRIGGER tg_actualizar_total
AFTER INSERT OR UPDATE OR DELETE ON compra_detalles
FOR EACH ROW
EXECUTE FUNCTION actualizar_total_compra();


ALTER TABLE compras 
DROP COLUMN IF EXISTS id_producto,
DROP COLUMN IF EXISTS cantidad,
DROP COLUMN IF EXISTS precio_unitario;

CREATE TABLE compra_detalles (
    id_detalle SERIAL PRIMARY KEY,
    id_compra INTEGER NOT NULL REFERENCES compras(id_compra) ON DELETE CASCADE,
    id_producto INTEGER NOT NULL REFERENCES productos(id_producto),
    cantidad NUMERIC(10) NOT NULL CHECK (cantidad > 0),
    precio_unitario NUMERIC(12, 2) NOT NULL CHECK (precio_unitario > 0),
    subtotal NUMERIC(12, 2) GENERATED ALWAYS AS (cantidad * precio_unitario) STORED,
    CONSTRAINT uk_compra_producto UNIQUE (id_compra, id_producto)
);

ALTER TABLE compra_detalles
ALTER COLUMN cantidad TYPE INTEGER
USING cantidad::INTEGER;

ALTER TABLE compra_detalles
ALTER COLUMN cantidad SET NOT NULL;

ALTER TABLE compra_detalles
ADD CONSTRAINT chk_cantidad_positiva CHECK (cantidad > 0);


CREATE INDEX idx_compra_detalles_compra ON compra_detalles(id_compra);
CREATE INDEX idx_compra_detalles_producto ON compra_detalles(id_producto);


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
CREATE TABLE productos_proveedores (
    id SERIAL PRIMARY KEY,
    id_producto INTEGER NOT NULL,
    id_proveedor INTEGER NOT NULL,
    precio_unitario NUMERIC(10, 2) NOT NULL,
    CONSTRAINT fk_producto FOREIGN KEY (id_producto) REFERENCES productos(id_producto) ON DELETE CASCADE,
    CONSTRAINT fk_proveedor FOREIGN KEY (id_proveedor) REFERENCES proveedores(id_proveedor) ON DELETE CASCADE,
    CONSTRAINT unique_producto_proveedor UNIQUE (id_producto, id_proveedor)
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

