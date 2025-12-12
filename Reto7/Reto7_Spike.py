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
puerto_sensor_ultrasonico = port.A # Verifica si tu robot lo tiene en el A o D (XML dice 3)
puerto_sensor_color = port.C       # Asignado al puerto C (XML dice 2)

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

    # BLOQUE 1: Calibración/Salida inicial (Cruce de línea)
    # Espera inicial para asegurar posición
    while color_sensor.color(puerto_sensor_color) != color.WHITE:
        await runloop.sleep_ms(10)
    
    # Avanza rápido cruzando la línea
    avanzar_indefinidamente(velocidad=1000)
    
    # Lógica de cruce seguro: Esperar a ver negro y luego ver blanco otra vez
    while color_sensor.color(puerto_sensor_color) != color.BLACK:
        await runloop.sleep_ms(10)
    while color_sensor.color(puerto_sensor_color) != color.WHITE:
        await runloop.sleep_ms(10)
    await detener()
    
    await pausa(0.5)

    # BLOQUE 2: Recorrido inicial rápido
    await girar_izquierda_fase(90, velocidad=300)
    await avanzar_cm(70, velocidad=1000)
    await girar_derecha_fase(90, velocidad=300)
    await avanzar_cm(45, velocidad=1000)
    await pausa(0.5)

    # BLOQUE 3: Navegación de esquinas
    await girar_derecha_fase(90, velocidad=300)
    await avanzar_cm(72, velocidad=1000)
    await girar_derecha_fase(90, velocidad=300)
    await avanzar_cm(50, velocidad=1000)

    # BLOQUE 4: Segundo cruce de línea
    while color_sensor.color(puerto_sensor_color) != color.BLACK:
        await runloop.sleep_ms(10)
    
    avanzar_indefinidamente(velocidad=1000)
    
    while color_sensor.color(puerto_sensor_color) != color.WHITE:
        await runloop.sleep_ms(10)
    await detener()

    # BLOQUE 5: Ajuste fino y lento
    await avanzar_cm(8.8, velocidad=300)
    await girar_derecha_fase(90, velocidad=300)
    await avanzar_cm(5, velocidad=300)

    # BLOQUE 6: Detección Ultrasónica
    # Esperar a ver negro para iniciar la medición
    while color_sensor.color(puerto_sensor_color) != color.BLACK:
        await runloop.sleep_ms(10)
    
    avanzar_indefinidamente(velocidad=1000)
    
    # Avanzar hasta que el ultrasonido mida menos de 50cm
    while True:
        if distance_sensor.distance(puerto_sensor_ultrasonico) < 500: # 50cm = 500mm
            break
        await runloop.sleep_ms(10)
    await detener()

    # BLOQUE 7: Comprobación de Color ROJO
    await girar_izquierda_fase(90, velocidad=300)
    await avanzar_cm(27, velocidad=300) # Acercamiento lento para leer color

    # Si ve ROJO (#dc143c), retrocede mucho
    if color_sensor.color(puerto_sensor_color) == color.RED:
        await retroceder_cm(135, velocidad=1000)

    await girar_derecha_fase(90, velocidad=300)
    await avanzar_cm(45, velocidad=1000)
    await pausa(0.5)

    # BLOQUE 8: Maniobras de retorno
    await retroceder_cm(45, velocidad=1000)
    await girar_izquierda_fase(90, velocidad=300)
    await avanzar_cm(108, velocidad=1000)
    await girar_izquierda_fase(90, velocidad=300)
    await avanzar_cm(20, velocidad=1000)
    await girar_derecha_fase(90, velocidad=300)
    await avanzar_cm(21, velocidad=1000)

    # BLOQUE 9: Comprobación de Color VERDE
    # Si ve VERDE (#00642e), retrocede
    if color_sensor.color(puerto_sensor_color) == color.GREEN:
        await retroceder_cm(21, velocidad=1000)

    await girar_izquierda_fase(90, velocidad=300)

    # BLOQUE 10: Cruce de línea final
    while color_sensor.color(puerto_sensor_color) != color.BLACK:
        await runloop.sleep_ms(10)
    
    avanzar_indefinidamente(velocidad=1000)
    
    while color_sensor.color(puerto_sensor_color) != color.WHITE:
        await runloop.sleep_ms(10)
    await detener()

    # BLOQUE 11: Llegada a meta
    await avanzar_cm(8, velocidad=1000)
    await girar_izquierda_fase(90, velocidad=300)
    await avanzar_cm(5, velocidad=1000)

    # Cruce final para asegurar posición
    while color_sensor.color(puerto_sensor_color) != color.BLACK:
        await runloop.sleep_ms(10)
    
    avanzar_indefinidamente(velocidad=1000)
    
    while color_sensor.color(puerto_sensor_color) != color.WHITE:
        await runloop.sleep_ms(10)
    await detener()

# Ejecutar programa
runloop.run(main())