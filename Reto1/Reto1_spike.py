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

# CONSTANTES FÍSICAS
CIRCUNFERENCIA_RUEDA = 17.58 # float
GRADOS_POR_ROTACION = 360 # int

# --- 2. FUNCIÓN DE CONVERSIÓN ---
def cm_a_grados(cm: float) -> int:
    """Convierte centímetros a grados de motor usando la circunferencia de la rueda."""
    # Fórmula: (Distancia * 360) / Circunferencia
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

    # Bloque 1: Salida de la base y posicionamiento inicial
    await avanzar_cm(195, velocidad=600)
    await girar_derecha_fase(90, velocidad=300)
    await avanzar_cm(80, velocidad=600)
    
    # Bloque 2: Maniobra de ajuste y avance intermedio
    await retroceder_cm(80, velocidad=600)
    await girar_derecha_fase(88, velocidad=300)
    await avanzar_cm(122, velocidad=600)
    
    # Bloque 3: Navegación hacia la zona central
    await girar_derecha_fase(88, velocidad=300)
    await avanzar_cm(89, velocidad=600)
    await girar_izquierda_fase(88, velocidad=300)
    
    # Bloque 4: Primera interacción corta (adelante/atrás)
    await avanzar_cm(20, velocidad=600)
    await retroceder_cm(20, velocidad=600)
    
    # Bloque 5: Tramo largo hacia el otro extremo
    await girar_izquierda_fase(89, velocidad=300)
    await avanzar_cm(89, velocidad=600)
    await girar_derecha_fase(88, velocidad=300)
    await avanzar_cm(270, velocidad=900) # Tramo rápido
    
    # Bloque 6: Segunda interacción y retorno
    await girar_derecha_fase(88, velocidad=300)
    await avanzar_cm(85, velocidad=600)
    await retroceder_cm(85, velocidad=600)
    
    # Bloque 7: Tramo rápido de regreso
    await girar_derecha_fase(90, velocidad=300)
    await avanzar_cm(197, velocidad=1000) # Velocidad máxima
    await girar_derecha_fase(90, velocidad=300)
    await avanzar_cm(40, velocidad=600)
    
    # Bloque 8: Dejar la pieza roja
    await girar_derecha_fase(88, velocidad=300) # Giro para dejar la roja
    await avanzar_cm(197, velocidad=600)
    await girar_izquierda_fase(90, velocidad=300)
    
    # Bloque 9: Ajuste fino
    await avanzar_cm(7, velocidad=300)
    await retroceder_cm(7, velocidad=300)
    
    # Bloque 10: Dirigirse a la zona azul
    await girar_derecha_fase(90, velocidad=300) # Giro para dirigirse a la azul
    await retroceder_cm(197, velocidad=600)
    await girar_derecha_fase(90, velocidad=300)
    await avanzar_cm(80, velocidad=600)
    
    # Bloque 11: Interacción en zona azul y salida
    await girar_izquierda_fase(90, velocidad=300)
    await avanzar_cm(23, velocidad=600)
    await retroceder_cm(23, velocidad=600)
    await girar_izquierda_fase(90, velocidad=300)
    await avanzar_cm(40, velocidad=600)
    
    # Bloque 12: Regreso final a meta
    await girar_izquierda_fase(90, velocidad=300)
    await avanzar_cm(195, velocidad=1000)
    await girar_izquierda_fase(90, velocidad=300)
    await avanzar_cm(80, velocidad=1000)

    # Detener el robot al finalizar
    await detener()

# Línea de código para correr el programa del robot
runloop.run(main())