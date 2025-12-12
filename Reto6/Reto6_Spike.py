from hub import port
import runloop
import motor_pair
import motor
import color_sensor
import color
import distance_sensor
from hub import light_matrix, sound

# --- 1. DEFINICIÓN DE PUERTOS Y CONSTANTES ---
motor_izquierda = port.F
motor_derecha = port.B
puerto_garra = port.E
puerto_sensor_ultrasonico = port.A
puerto_sensor_color = port.C # Asignado al puerto 3 del XML

# CONSTANTES FÍSICAS
CIRCUNFERENCIA_RUEDA = 17.58 # float
GRADOS_POR_ROTACION = 360 # int

# --- 2. FUNCIÓN DE CONVERSIÓN ---
def cm_a_grados(cm: float) -> int:
    """Convierte centímetros a grados de motor usando la circunferencia de la rueda."""
    grados_float = (cm * GRADOS_POR_ROTACION) / CIRCUNFERENCIA_RUEDA
    return round(grados_float)

# --- 3. FUNCIONES PARA GARRA ---
async def subir_garra(grados: int = 90, velocidad: int = 365) -> None:
    """Sube la garra. Usa grados positivos."""
    await motor.run_for_degrees(puerto_garra, grados, velocidad)

async def bajar_garra(grados: int = 90, velocidad: int = 365) -> None:
    """Baja la garra. El valor de grados ingresado debe ser positivo."""
    await motor.run_for_degrees(puerto_garra, -grados, velocidad)

# --- 4. FUNCIONES PARA GIROS ---
async def girar_derecha_fase(grados: int = 200, direccion: int = 90, velocidad: int = 1000) -> None:
    """Gira en fase a la derecha según grados de motor."""
    await motor_pair.move_for_degrees(motor_pair.PAIR_1, grados, direccion, velocity=velocidad)

async def girar_izquierda_fase(grados: int = 200, direccion: int = 90, velocidad: int = 1000) -> None:
    """Gira en fase según grados de motor."""
    await motor_pair.move_for_degrees(motor_pair.PAIR_1, -grados, direccion, velocity=velocidad)

async def girar_derecha_desfase(grados: int = 90, velocidad: int = 500) -> None:
    """Gira a la derecha moviendo solo el motor izquierdo (desfase)."""
    motor.run(motor_izquierda, -500)
    await pausa(0.8)
    motor.stop(motor_izquierda, stop=motor.BRAKE)

async def girar_izquierda_desfase(grados: int = 90, velocidad: int = 500) -> None:
    """Gira a la izquierda moviendo solo el motor derecho (desfase)."""
    motor.run(motor_derecha, 500)
    await pausa(0.8)
    motor.stop(motor_derecha, stop=motor.BRAKE)

# --- 5. FUNCIONES DE AVANCE ---
async def avanzar_cm(cm: float, velocidad: int = 500) -> None:
    """Avanza recto la cantidad de cm especificada."""
    grados = cm_a_grados(cm)
    await motor_pair.move_for_degrees(motor_pair.PAIR_1, grados, 0, velocity=velocidad)

async def retroceder_cm(cm: float, velocidad: int = 500) -> None:
    """Retrocede recto la cantidad de cm especificada."""
    grados = cm_a_grados(cm)
    await motor_pair.move_for_degrees(motor_pair.PAIR_1, -grados, 0, velocity=velocidad)

async def avanzar_grados(grados: int, velocidad: int = 500) -> None:
    """Avanza recto la cantidad de grados de motor especificada."""
    await motor_pair.move_for_degrees(motor_pair.PAIR_1, grados, 0, velocity=velocidad)

async def retroceder_grados(grados: int, velocidad: int = 500) -> None:
    """Retrocede recto la cantidad de grados de motor especificada (valor negativo)."""
    await motor_pair.move_for_degrees(motor_pair.PAIR_1, -grados, 0, velocity=velocidad)

async def avanzar_rotaciones(rotaciones: int, velocidad: int = 500) -> None:
    """Avanza recto la cantidad de rotaciones especificadas."""
    grados = GRADOS_POR_ROTACION * rotaciones
    await motor_pair.move_for_degrees(motor_pair.PAIR_1, grados, 0, velocity=velocidad)

async def retroceder_rotaciones(rotaciones: int, velocidad: int = 500) -> None:
    """Retrocede recto la cantidad de rotaciones especificadas."""
    grados = GRADOS_POR_ROTACION * rotaciones
    await motor_pair.move_for_degrees(motor_pair.PAIR_1, -grados, 0, velocity=velocidad)

# Funciones de Avance/Retroceso Indefinido
def avanzar_indefinidamente(velocidad: int = 500) -> None:
    motor_pair.move(motor_pair.PAIR_1, 0, velocity=velocidad)

def retroceder_indefinidamente(velocidad: int = 500) -> None:
    motor_pair.move(motor_pair.PAIR_1, 0, velocity=-velocidad)

# --- 6. FUNCIÓN PAUSA ---
async def pausa(segundos: float = 2) -> None:
    """Pausa asíncrona no bloqueante."""
    await runloop.sleep_ms(int(segundos * 1000))

async def emote():
    motor.run(motor_derecha, 1000)
    light_matrix.show_image(light_matrix.IMAGE_HAPPY)
    sound.beep(440, 10000, 100)
    await pausa(10)
    motor.stop(motor_derecha)

#--- 7. FUNCIÓN DETENER MOVIMIENTO ---
async def detener() -> None:
    """Detener movimiento."""
    motor_pair.stop(motor_pair.PAIR_1)

#--- 8. FUNCIÓN SENSOR ULTRASÓNICO ---
async def avanzar_hasta_detectar_objeto(distancia_cm) -> None:
    """Detiene el movimiento hasta que el sensor detecte un objeto."""
    avanzar_indefinidamente()
    while True:
        distancia = distance_sensor.distance(puerto_sensor_ultrasonico)
        if distancia <= distancia_cm*10:
            motor_pair.stop(motor_pair.PAIR_1)
            break

# --- FUNCIÓN PRINCIPAL Y EJECUCIÓN ---
async def main():
    # Inicialización del par de motores
    motor_pair.pair(motor_pair.PAIR_1, motor_izquierda, motor_derecha)

    # Bloque 1: Salida del puerto
    await avanzar_cm(63, velocidad=1000)
    await girar_derecha_fase(90, velocidad=300)

    # Bloque 2: Seguidor de línea LARGO hacia VERDE
    # Reiniciar encoder del motor derecho (B) para medir distancia
    motor.reset_relative_position(motor_derecha)
    # Loop hasta superar 3450 grados (aprox 160cm)
    while abs(motor.relative_position(motor_derecha)) < 3450:
        color_detectado = color_sensor.color(puerto_sensor_color)
        if color_detectado == color.BLACK: # XML dice Gris #585858
            # Curva suave: Izq 1200 / Der 1100
            motor_pair.move_tank(motor_pair.PAIR_1, 1000, 900)
        else:
            # Corrección: Izq 1100 / Der 1200
            motor_pair.move_tank(motor_pair.PAIR_1, 900, 1000)
    
    # Avanzar hasta detectar VERDE
    avanzar_indefinidamente(velocidad=900)
    while color_sensor.color(puerto_sensor_color) != color.GREEN:
        await runloop.sleep_ms(10)
    await detener()

    # Bloque 3: Maniobra en zona Verde
    await girar_izquierda_fase(90, velocidad=300)
    await avanzar_cm(5, velocidad=900)
    await girar_izquierda_fase(90, velocidad=300)

    # Bloque 4: Seguidor de línea hacia AMARILLO
    motor.reset_relative_position(motor_derecha)
    while abs(motor.relative_position(motor_derecha)) < 1200:
        if color_sensor.color(puerto_sensor_color) == color.BLACK:
            motor_pair.move_tank(motor_pair.PAIR_1, 900, 800)
        else:
            motor_pair.move_tank(motor_pair.PAIR_1, 800, 900)
            
    # Avanzar hasta detectar AMARILLO (#f7d117)
    avanzar_indefinidamente(velocidad=900)
    while color_sensor.color(puerto_sensor_color) != color.YELLOW:
        await runloop.sleep_ms(10)
    await detener()

    # Bloque 5: Maniobra en zona Amarilla
    await girar_izquierda_fase(90, velocidad=300)
    await avanzar_cm(5, velocidad=900)
    await girar_izquierda_fase(90, velocidad=300)

    # Bloque 6: Seguidor de línea hacia ROJO
    motor.reset_relative_position(motor_derecha)
    while abs(motor.relative_position(motor_derecha)) < 1600:
        if color_sensor.color(puerto_sensor_color) == color.BLACK:
            motor_pair.move_tank(motor_pair.PAIR_1, 900, 800)
        else:
            motor_pair.move_tank(motor_pair.PAIR_1, 800, 900)

    # Avanzar hasta detectar ROJO (#dc143c)
    avanzar_indefinidamente(velocidad=900)
    while color_sensor.color(puerto_sensor_color) != color.RED:
        await runloop.sleep_ms(10)
    await detener()

    # Bloque 7: Maniobra en zona Roja
    await girar_izquierda_fase(90, velocidad=300)
    await avanzar_cm(15, velocidad=900)
    await girar_izquierda_fase(90, velocidad=300)

    # Bloque 8: Seguidor de línea hacia AZUL
    motor.reset_relative_position(motor_derecha)
    while abs(motor.relative_position(motor_derecha)) < 3800:
        if color_sensor.color(puerto_sensor_color) == color.BLACK:
            motor_pair.move_tank(motor_pair.PAIR_1, 900, 800)
        else:
            motor_pair.move_tank(motor_pair.PAIR_1, 800, 900)

    # Avanzar hasta detectar AZUL (#0057a6)
    avanzar_indefinidamente(velocidad=900)
    while color_sensor.color(puerto_sensor_color) != color.BLUE:
        await runloop.sleep_ms(10)
    await detener()

    # Bloque 9: Compleja maniobra en puerto Azul
    await girar_derecha_fase(90, velocidad=300)
    await avanzar_cm(35, velocidad=900)
    await girar_derecha_fase(90, velocidad=300)
    await avanzar_cm(25, velocidad=900)
    await girar_derecha_fase(90, velocidad=300)
    await avanzar_cm(20, velocidad=900)
    await retroceder_cm(20, velocidad=900)
    await girar_derecha_fase(90, velocidad=300)
    await avanzar_cm(25, velocidad=900)
    await girar_izquierda_fase(90, velocidad=300)
    await avanzar_cm(30, velocidad=900)
    await girar_derecha_fase(90, velocidad=300)

    # Bloque 10: Seguidor de línea hacia BLANCO
    motor.reset_relative_position(motor_derecha)
    while abs(motor.relative_position(motor_derecha)) < 4100:
        if color_sensor.color(puerto_sensor_color) == color.BLACK:
            motor_pair.move_tank(motor_pair.PAIR_1, 900, 800)
        else:
            motor_pair.move_tank(motor_pair.PAIR_1, 800, 900)

    # Avanzar hasta detectar BLANCO
    avanzar_indefinidamente(velocidad=900)
    while color_sensor.color(puerto_sensor_color) != color.WHITE:
        await runloop.sleep_ms(10)
    await detener()

    # Bloque 11: Maniobra intermedia
    await girar_izquierda_fase(90, velocidad=300)
    await avanzar_cm(5, velocidad=900)
    await girar_izquierda_fase(90, velocidad=300)

    # Bloque 12: Seguidor de línea hacia NEGRO (Meta/Puerto)
    motor.reset_relative_position(motor_derecha)
    while abs(motor.relative_position(motor_derecha)) < 1700:
        if color_sensor.color(puerto_sensor_color) == color.BLACK:
            motor_pair.move_tank(motor_pair.PAIR_1, 900, 800)
        else:
            motor_pair.move_tank(motor_pair.PAIR_1, 800, 900)

    # Avanzar hasta detectar NEGRO (#000000)
    avanzar_indefinidamente(velocidad=900)
    while color_sensor.color(puerto_sensor_color) != color.BLACK:
        await runloop.sleep_ms(10)
    await detener()

    # Bloque 13: Salida del puerto
    await girar_izquierda_fase(90, velocidad=300)
    await avanzar_cm(5, velocidad=900)
    await girar_izquierda_fase(90, velocidad=300)

    # Bloque 14: Retorno a zona central
    motor.reset_relative_position(motor_derecha)
    while abs(motor.relative_position(motor_derecha)) < 1600:
        if color_sensor.color(puerto_sensor_color) == color.BLACK:
            motor_pair.move_tank(motor_pair.PAIR_1, 900, 800)
        else:
            motor_pair.move_tank(motor_pair.PAIR_1, 800, 900)
            
    # Avanzar hasta detectar AZUL nuevamente
    avanzar_indefinidamente(velocidad=900)
    while color_sensor.color(puerto_sensor_color) != color.BLUE:
        await runloop.sleep_ms(10)
    await detener()
    
    # Bloque 15: Ajuste Azul
    await girar_izquierda_fase(90, velocidad=300)
    await avanzar_cm(5, velocidad=900)
    await girar_izquierda_fase(90, velocidad=300)

    # Bloque 16: Seguidor de línea hacia Gris
    motor.reset_relative_position(motor_derecha)
    while abs(motor.relative_position(motor_derecha)) < 1500:
        if color_sensor.color(puerto_sensor_color) == color.BLACK:
            motor_pair.move_tank(motor_pair.PAIR_1, 900, 800)
        else:
            motor_pair.move_tank(motor_pair.PAIR_1, 800, 900)

    # Detenerse en GRIS (simulado como detectar línea y parar)
    avanzar_indefinidamente(velocidad=900)
    await runloop.sleep_ms(200) # Pequeña pausa simulando detección
    await detener()

    # Bloque 17: Giro
    await girar_derecha_fase(90, velocidad=300)

    # Bloque 18: Seguidor de línea hacia BLANCO
    motor.reset_relative_position(motor_derecha)
    while abs(motor.relative_position(motor_derecha)) < 1200:
        if color_sensor.color(puerto_sensor_color) == color.BLACK:
            motor_pair.move_tank(motor_pair.PAIR_1, 900, 800)
        else:
            motor_pair.move_tank(motor_pair.PAIR_1, 800, 900)

    avanzar_indefinidamente(velocidad=900)
    while color_sensor.color(puerto_sensor_color) != color.WHITE:
        await runloop.sleep_ms(10)
    await detener()

    # Bloque 19: Maniobra final
    await girar_izquierda_fase(90, velocidad=300)
    await avanzar_cm(5, velocidad=900)
    await girar_izquierda_fase(90, velocidad=300)

    # Bloque 20: Tramo final a casa
    motor.reset_relative_position(motor_derecha)
    while abs(motor.relative_position(motor_derecha)) < 1700:
        if color_sensor.color(puerto_sensor_color) == color.BLACK:
            motor_pair.move_tank(motor_pair.PAIR_1, 900, 800)
        else:
            motor_pair.move_tank(motor_pair.PAIR_1, 800, 900)

    # Bloque 21: Parking
    await girar_izquierda_fase(90, velocidad=300)
    await avanzar_cm(90, velocidad=900)

    await detener()

# Ejecutar programa
runloop.run(main())