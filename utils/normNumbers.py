def formatear_numero(valor):
    try:
        numero = float(valor)
    except (TypeError, ValueError):
        return "0,00"

    texto = f"{numero:,.0f}"
    texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
    return texto
