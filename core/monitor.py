import os
import logging

LOG_PATH = os.path.join("logs", "aegis_maule_audit.log")

class AegisSecurityMonitor:
    def __init__(self, threshold=2):
        self.threshold = threshold

    def analizar_alertas_logs(self):
        if not os.path.exists(LOG_PATH):
            return 0, "No se encontró el archivo de auditoría de seguridad."

        intentos_fallidos = 0
        try:
            with open(LOG_PATH, "r", encoding="utf-8", errors="replace") as f:
                for linea in f:
                    if "ALERTA DE SEGURIDAD" in linea or "Acceso fallido" in linea:
                        intentos_fallidos += 1
            
            if intentos_fallidos >= self.threshold:
                alerta_msg = f"[ALERTA CRÍTICA] Se detectaron {intentos_fallidos} intentos de acceso no autorizado. Posible ataque de fuerza bruta."
                logging.critical(alerta_msg)
                return intentos_fallidos, alerta_msg
            else:
                return intentos_fallidos, f"Estado normal. Intentos fallidos registrados: {intentos_fallidos} (Umbral seguro: < {self.threshold})"
        except Exception as e:
            return 0, f"Error al analizar registros: {str(e)}"