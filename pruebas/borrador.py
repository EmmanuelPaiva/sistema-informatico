def abrir_formulario_nueva_venta(self, Form):
        self.ui_nueva_venta = nuevaVentaUi()
        self.formulario_nueva_venta = QWidget(Form)  # o el contenedor principal
        self.ui_nueva_venta.setupUi(self.formulario_nueva_venta)
        
        
      
        
        ancho_formulario = 300
        alto_formulario = Form.height()


        # Posición inicial fuera de pantalla (izquierda)
        self.formulario_nueva_venta.setGeometry(Form.width(), 0, ancho_formulario, alto_formulario)
        self.formulario_nueva_venta.show()

        # Animación para deslizar
        self.anim = QPropertyAnimation(self.formulario_nueva_venta, b"geometry")
        self.anim.setDuration(300)
        self.anim.setStartValue(QRect(Form.width(), 0, ancho_formulario, alto_formulario))
        self.anim.setEndValue(QRect(Form.width() - ancho_formulario, 0, ancho_formulario, alto_formulario))
        self.anim.start()
        
        conexion_db = conexion()
        cursor = conexion_db.cursor()
        
        cursor.execute("SELECT id, nombre FROM clientes;")
        
        clientes = cursor.fetchall()
        
        
        for idC, nombreC in clientes:
            self.ui_nueva_venta.comboBox.addItem(nombreC, idC)
            if idC == clientes:
                self.ui_nueva_venta.comboBox.setCurrentIndex(
                    self.ui_nueva_venta.comboBox.count() - 1
                )
                
        cursor.execute("SELECT id_producto, nombre FROM productos;")
        productos = cursor.fetchall()
        
        for idP, nombreP in productos:
            self.ui_nueva_venta.comboBoxProducto.addItem(nombreP, idP)
        if idP == productos:
            self.ui_nueva_venta.comboBoxProducto.setCurrentIndex(
                self.ui_nueva_venta.comboBoxProducto.count() - 1
            )
        
        cursor.close()
        conexion_db.close()
        
        
        

        
        self.ui_nueva_venta.pushButtonCancelar.clicked.connect(lambda: self.cancelar(Form))
       
        
    #BOTON CANCELAR  
                
    def cancelar(self, Form):
        ancho_formulario = 300
        alto_formulario = Form.height()
        
        self.anim = QPropertyAnimation(self.formulario_nueva_venta, b"geometry")
        self.anim.setDuration(300)
        self.anim.setStartValue(QRect(Form.width() - ancho_formulario, 0, ancho_formulario, alto_formulario))
        self.anim.setEndValue(QRect(Form.width(), 0, ancho_formulario, alto_formulario))
        self.anim.start()
        
        
    # BOTON ACEPTAR 
        
    def aceptar(self, id):
        pass
    
    
    #FUNCIONES DE PRECIO DE VENT A (TOTAL, SUBTOTAL)
    
    def obtener_precio_producto(self, nombre_producto):
        conexion_db = conexion()
        cursor = conexion_db.cursor()
        cursor.execute("SELECT precio_venta FROM productos WHERE nombre = %s", (nombre_producto,))
        resultado = cursor.fetchone()
        conexion_db.close()
        return resultado[0] if resultado else 0

        
    def actualizar_precio_subtotal(self, combo_producto, cantidad_input, precio_label, subtotal_label):
        producto = self.ui_nueva_venta.comboBoxProducto.currentText()
        precio = self.obtener_precio_producto(producto)
        self.ui_nueva_venta.lineEditPrecio.setText(str(precio))

        try:
            cantidad = int(self.ui_nueva_venta.lineEditCantidad.text())
            subtotal = cantidad * precio
            self.ui_nueva_venta.lineEditPrecio.setText(str(subtotal))
        except ValueError:
            subtotal_label.setText("0")

        self.recalcular_total_venta()
        self.agregar_producto()
        
    
    def recalcular_total_venta(self):
        total = 0
        for fila in self.lista_productos:
            try:
                subtotal = float(fila['subtotal_input'].text())
            except ValueError:
                subtotal = 0
            total += subtotal
        self.ui_nueva_venta.lineEditPrecioTotal.setText(str(total))
        
        
    def agregar_producto(self):
        combo_producto = self.ui_nueva_venta.comboBoxProducto
        cantidad_input = self.ui_nueva_venta.lineEditCantidad
        precio_input = self.ui_nueva_venta.lineEditPrecio
        subtotal_input= self.ui_nueva_venta.lineEditPrecioTotal

        producto = {
            'combo': combo_producto,
            'cantidad_input': cantidad_input,
            'precio_input': precio_input,
            'subtotal_input': subtotal_input
        }

        self.lista_productos.append(producto)
        