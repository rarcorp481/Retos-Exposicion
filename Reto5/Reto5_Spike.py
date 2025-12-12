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
puerto_sensor_ultrasonico = port.A # XML dice puerto 4, asignado a A. ¡Verificar!
puerto_sensor_color = port.C       # XML dice puerto 2, asignado a C.

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

    # Bloque 1: Salida inicial larga
    # Avanza 172 cm rápido
    await avanzar_cm(172, velocidad=1000)
    # Turn Right 90
    await girar_derecha_fase(90, velocidad=300)
    
    # Bloque 2: Aproximación inicial
    # Avanza 55 cm rápido
    await avanzar_cm(55, velocidad=1000)
    
    # Bloque 3: Sincronización con línea negra
    # Esperar a ver NEGRO para asegurar posición antes de medir distancia
    while color_sensor.color(puerto_sensor_color) != color.BLACK:
        await runloop.sleep_ms(10)

    # Bloque 4: Aproximación final con Ultrasonido
    # Lógica del XML: Esperar negro -> Avanzar lento -> Esperar blanco -> Avanzar lento -> Esperar US < 35
    
    # Comenzar avance lento
    avanzar_indefinidamente(velocidad=300)
    
    # Asegurar que sigue viendo negro (por si acaso el bucle anterior fue muy rápido)
    # y luego esperar a salir de la línea negra (ver blanco)
    while color_sensor.color(puerto_sensor_color) != color.WHITE:
        await runloop.sleep_ms(10)
        
    # Continuar avanzando lento hasta detectar objeto a 35 cm
    while True:
        # El sensor devuelve mm, 35cm = 350mm
        distancia = distance_sensor.distance(puerto_sensor_ultrasonico)
        if distancia is not None and distancia < 350:
            motor_pair.stop(motor_pair.PAIR_1)
            break
        await runloop.sleep_ms(10)
    
    # Bloque 5: Giro tras detección y agarre (asumido)
    await girar_izquierda_fase(90, velocidad=300)
    
    # Bloque 6: Tramo intermedio hacia zona de decisión
    await avanzar_cm(70, velocidad=1000)
    
    # Bloque 7: Condicional de Color (AMARILLO)
    # Si ve AMARILLO (#f7d117), espera y gira a la izquierda
    # Si NO ve amarillo, el robot continuará recto hacia el Bloque 8
    detected_color = color_sensor.color(puerto_sensor_color)
    if detected_color == color.YELLOW:
        await pausa(0.5)
        await girar_izquierda_fase(90, velocidad=300)
        
    # Bloque 8: Cruce de línea de seguridad (Confirmación de posición)
    # Esta lógica se ejecuta tanto si giró como si no, asegurando que cruza la siguiente línea negra
    
    # Esperar a llegar a la línea negra
    while color_sensor.color(puerto_sensor_color) != color.BLACK:
        await runloop.sleep_ms(10)
    
    # Avanzar lento cruzando la línea
    avanzar_indefinidamente(velocidad=300)
    
    # Esperar a ver BLANCO (fin de línea)
    while color_sensor.color(puerto_sensor_color) != color.WHITE:
        await runloop.sleep_ms(10)
    
    # Pequeño avance extra para asegurar cruce y detenerse
    await pausa(0.2) 
    await detener()
    
    # Bloque 9: Tramo final hacia meta/ensamblaje
    await avanzar_cm(50, velocidad=1000)
    await girar_izquierda_fase(90, velocidad=300)
    await avanzar_cm(15, velocidad=1000)

    # Detener al finalizar
    await detener()

# Ejecutar programa
runloop.run(main())