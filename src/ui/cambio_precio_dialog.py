from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QKeyEvent

def parse_precio(texto: str) -> float:
    """
    Parsea de forma robusta cualquier formato de moneda argentina o internacional:
    Ejemplos soportados:
    - 2000 -> 2000.0
    - 10.000 -> 10000.0 (punto como miles)
    - 1.000.000 -> 1000000.0 (múltiples puntos como miles)
    - 1500,50 -> 1500.5 (coma como decimal)
    - 1500.50 -> 1500.5 (punto como decimal)
    - 1.500,50 -> 1500.5 (punto miles, coma decimal)
    - $ 10.000 -> 10000.0
    """
    if not texto:
        raise ValueError("Texto vacío")
    texto = texto.replace("$", "").strip()
    if not texto:
        raise ValueError("Texto vacío")

    # Caso 1: Contiene tanto punto como coma (ej: 1.000,50 o 1,000.50)
    if '.' in texto and ',' in texto:
        if texto.rfind(',') > texto.rfind('.'):
            # Formato 1.000,50 (Argentina / España)
            texto = texto.replace('.', '').replace(',', '.')
        else:
            # Formato 1,000.50 (EE. UU.)
            texto = texto.replace(',', '')

    # Caso 2: Solo contiene comas (ej: 250,50 o 1,000,000)
    elif ',' in texto:
        partes = texto.split(',')
        if len(partes) > 2:
            texto = texto.replace(',', '')
        else:
            texto = texto.replace(',', '.')

    # Caso 3: Solo contiene puntos (ej: 1.000.000 o 10.000 o 250.50)
    elif '.' in texto:
        partes = texto.split('.')
        if len(partes) > 2:
            # Múltiples puntos -> clarísimo separador de miles (ej: 1.000.000)
            texto = texto.replace('.', '')
        elif len(partes) == 2:
            # Un solo punto: si tiene 3 dígitos a la derecha (ej: 1.000 o 10.000), es separador de miles
            if len(partes[1]) == 3 and len(partes[0]) <= 3:
                texto = texto.replace('.', '')
            else:
                # Es decimal (ej: 250.50 o 10.5)
                pass

    val = float(texto)
    if val < 0:
        raise ValueError("No puede ser negativo")
    return val


class NumericPriceInput(QLineEdit):
    """Input numérico sin validadores restrictivos que rompen el locale en Windows."""
    def focusInEvent(self, event):
        super().focusInEvent(event)
        self.selectAll()


class CambioPrecioDialog(QDialog):
    """
    Diálogo modal limpio, robusto y sin emojis para modificar el precio de un producto
    en el punto de venta. Resuelve correctamente separadores de miles y decimales.
    """
    def __init__(self, parent, nombre_producto: str, codigo: str, precio_anterior: float, precio_nuevo: float = None):
        super().__init__(parent)
        self.nombre_producto = nombre_producto
        self.codigo = codigo or "Sin código"
        self.precio_anterior = float(precio_anterior)
        self.precio_nuevo_inicial = float(precio_nuevo) if precio_nuevo is not None else self.precio_anterior
        
        self.resultado_accion = None
        self.precio_seleccionado = self.precio_nuevo_inicial

        self.setWindowTitle("Modificar Precio")
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setFixedWidth(480)
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #161B22;
                color: #F0F6FC;
                font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)

        # 1. ENCABEZADO
        header_layout = QVBoxLayout()
        header_layout.setSpacing(4)

        lbl_seccion = QLabel("CAMBIO DE PRECIO")
        lbl_seccion.setStyleSheet("color: #8B949E; font-size: 11px; font-weight: 700; letter-spacing: 1px;")
        header_layout.addWidget(lbl_seccion)

        lbl_nombre = QLabel(self.nombre_producto)
        lbl_nombre.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        lbl_nombre.setStyleSheet("color: #FFFFFF;")
        lbl_nombre.setWordWrap(True)
        header_layout.addWidget(lbl_nombre)

        lbl_codigo = QLabel(f"Código: {self.codigo}")
        lbl_codigo.setStyleSheet("color: #8B949E; font-size: 12px;")
        header_layout.addWidget(lbl_codigo)

        layout.addLayout(header_layout)

        # 2. BLOQUE DE ENTRADA DE PRECIO
        frame_input = QFrame()
        frame_input.setStyleSheet("""
            QFrame {
                background-color: #0D1117;
                border: 1px solid #30363D;
                border-radius: 8px;
            }
        """)
        input_layout = QVBoxLayout(frame_input)
        input_layout.setContentsMargins(16, 14, 16, 14)
        input_layout.setSpacing(8)

        lbl_actual = QLabel(f"Precio actual: ${self.precio_anterior:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        lbl_actual.setStyleSheet("color: #8B949E; font-size: 13px; font-weight: 500; border: none;")
        input_layout.addWidget(lbl_actual)

        lbl_nuevo_rotulo = QLabel("Nuevo precio a cobrar:")
        lbl_nuevo_rotulo.setStyleSheet("color: #C9D1D9; font-size: 12px; font-weight: 600; border: none;")
        input_layout.addWidget(lbl_nuevo_rotulo)

        h_input = QHBoxLayout()
        h_input.setSpacing(8)

        lbl_signo = QLabel("$")
        lbl_signo.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        lbl_signo.setStyleSheet("color: #58A6FF; border: none;")
        h_input.addWidget(lbl_signo)

        self.input_precio = NumericPriceInput()
        # Formato limpio: si es entero muestra ej "2000" sin .00 innecesarios, si tiene centavos los muestra
        if self.precio_nuevo_inicial.is_integer():
            texto_inicial = f"{int(self.precio_nuevo_inicial)}"
        else:
            texto_inicial = f"{self.precio_nuevo_inicial:.2f}"

        self.input_precio.setText(texto_inicial)
        self.input_precio.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        self.input_precio.setStyleSheet("""
            QLineEdit {
                background-color: #161B22;
                color: #FFFFFF;
                border: 1px solid #388BFD;
                border-radius: 6px;
                padding: 6px 10px;
            }
            QLineEdit:focus {
                border: 2px solid #58A6FF;
            }
        """)
        self.input_precio.textChanged.connect(self.al_modificar_precio_input)
        h_input.addWidget(self.input_precio)

        input_layout.addLayout(h_input)

        self.lbl_mensaje_estado = QLabel("")
        self.lbl_mensaje_estado.setStyleSheet("font-size: 11px; border: none;")
        self.actualizar_estado(self.precio_nuevo_inicial)
        input_layout.addWidget(self.lbl_mensaje_estado)

        layout.addWidget(frame_input)

        # 3. PREGUNTA DE ALCANCE Y BOTONES DE ACCIÓN
        lbl_pregunta = QLabel("¿Cómo desea aplicar este nuevo precio?")
        lbl_pregunta.setStyleSheet("color: #C9D1D9; font-size: 12px; font-weight: 600;")
        layout.addWidget(lbl_pregunta)

        # Botón 1: Solo en esta venta
        self.btn_solo_venta = QPushButton()
        self.btn_solo_venta.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_solo_venta.setStyleSheet("""
            QPushButton {
                background-color: #212830;
                border: 1px solid #38444D;
                border-radius: 8px;
                padding: 12px 14px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #2A3441;
                border-color: #58A6FF;
            }
            QPushButton:pressed {
                background-color: #1A2129;
            }
        """)
        btn_v_layout = QVBoxLayout(self.btn_solo_venta)
        btn_v_layout.setContentsMargins(0, 0, 0, 0)
        btn_v_layout.setSpacing(3)

        lbl_v_tit = QLabel("Solo en esta venta  [ Enter ]")
        lbl_v_tit.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        lbl_v_tit.setStyleSheet("color: #FFFFFF; border: none; font-weight: bold;")
        btn_v_layout.addWidget(lbl_v_tit)

        lbl_v_desc = QLabel("Aplica únicamente a este ticket. El precio del catálogo no se modifica.")
        lbl_v_desc.setStyleSheet("color: #8B949E; font-size: 11px; border: none;")
        btn_v_layout.addWidget(lbl_v_desc)

        self.btn_solo_venta.clicked.connect(self.aplicar_solo_venta)
        layout.addWidget(self.btn_solo_venta)

        # Botón 2: Actualizar en catálogo
        self.btn_actualizar_bd = QPushButton()
        self.btn_actualizar_bd.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_actualizar_bd.setStyleSheet("""
            QPushButton {
                background-color: #1A362C;
                border: 1.5px solid #2EA043;
                border-radius: 8px;
                padding: 12px 14px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #22473A;
                border-color: #3FB950;
            }
            QPushButton:pressed {
                background-color: #142B23;
            }
        """)
        btn_bd_layout = QVBoxLayout(self.btn_actualizar_bd)
        btn_bd_layout.setContentsMargins(0, 0, 0, 0)
        btn_bd_layout.setSpacing(3)

        lbl_bd_tit = QLabel("Actualizar en catálogo  [ Ctrl+Enter o F2 ]")
        lbl_bd_tit.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        lbl_bd_tit.setStyleSheet("color: #3FB950; border: none; font-weight: bold;")
        btn_bd_layout.addWidget(lbl_bd_tit)

        lbl_bd_desc = QLabel("Guarda el nuevo precio en el catálogo para esta y todas las próximas ventas.")
        lbl_bd_desc.setStyleSheet("color: #8B949E; font-size: 11px; border: none;")
        btn_bd_layout.addWidget(lbl_bd_desc)

        self.btn_actualizar_bd.clicked.connect(self.aplicar_actualizar_bd)
        layout.addWidget(self.btn_actualizar_bd)

        # 4. BOTÓN CANCELAR
        btn_cancelar = QPushButton("Cancelar (Esc)")
        btn_cancelar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancelar.setFixedHeight(36)
        btn_cancelar.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #8B949E;
                border: 1px solid #30363D;
                border-radius: 6px;
                font-size: 12px;
                font-weight: 500;
            }
            QPushButton:hover {
                color: #F85149;
                border-color: #F85149;
                background-color: #211517;
            }
        """)
        btn_cancelar.clicked.connect(self.reject)
        layout.addWidget(btn_cancelar)

        # Foco inicial en el campo numérico
        self.input_precio.setFocus()
        self.input_precio.selectAll()

    def al_modificar_precio_input(self, texto):
        try:
            precio_val = parse_precio(texto)
            self.precio_seleccionado = precio_val
            self.actualizar_estado(precio_val)
            self.btn_solo_venta.setEnabled(True)
            self.btn_actualizar_bd.setEnabled(True)
        except ValueError:
            self.lbl_mensaje_estado.setText("Ingrese un número válido mayor o igual a 0.")
            self.lbl_mensaje_estado.setStyleSheet("color: #F85149; font-size: 11px; border: none;")
            self.btn_solo_venta.setEnabled(False)
            self.btn_actualizar_bd.setEnabled(False)

    def actualizar_estado(self, nuevo_precio: float):
        diferencia = nuevo_precio - self.precio_anterior
        if abs(diferencia) < 0.001:
            self.lbl_mensaje_estado.setText("El precio ingresado es igual al precio actual.")
            self.lbl_mensaje_estado.setStyleSheet("color: #8B949E; font-size: 11px; border: none;")
        elif diferencia > 0:
            self.lbl_mensaje_estado.setText(f"Aumento de +${diferencia:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            self.lbl_mensaje_estado.setStyleSheet("color: #3FB950; font-size: 11px; font-weight: 600; border: none;")
        else:
            self.lbl_mensaje_estado.setText(f"Rebaja de -${abs(diferencia):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            self.lbl_mensaje_estado.setStyleSheet("color: #F85149; font-size: 11px; font-weight: 600; border: none;")

    def aplicar_solo_venta(self):
        if not self.btn_solo_venta.isEnabled():
            return
        self.resultado_accion = "VENTA"
        self.accept()

    def aplicar_actualizar_bd(self):
        if not self.btn_actualizar_bd.isEnabled():
            return
        self.resultado_accion = "CATALOGO"
        self.accept()

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        modifiers = event.modifiers()

        # F2 o Ctrl+Enter -> Actualizar catálogo
        if key == Qt.Key.Key_F2 or ((key in (Qt.Key.Key_Return, Qt.Key.Key_Enter)) and (modifiers & Qt.KeyboardModifier.ControlModifier)):
            self.aplicar_actualizar_bd()
            return

        # Enter simple -> Solo venta
        if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.aplicar_solo_venta()
            return

        super().keyPressEvent(event)

    def ejecutar(self):
        res = self.exec()
        if res == QDialog.DialogCode.Accepted and self.resultado_accion:
            return self.resultado_accion, self.precio_seleccionado
        return None, None
