#!/usr/bin/env python3
"""
Script inteligente de migraciones que verifica el estado antes de ejecutar
Previene conflictos de migraciones duplicadas en deployments
"""

import os
import sys
import subprocess
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_database_connection():
    """Verifica si la base de datos está disponible"""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        logger.error("❌ DATABASE_URL no está configurada")
        return False
    
    try:
        engine = create_engine(database_url)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("✅ Conexión a base de datos exitosa")
        return True
    except Exception as e:
        logger.error(f"❌ Error conectando a la base de datos: {e}")
        return False

def get_current_migration_version():
    """Obtiene la versión actual de migración de Alembic"""
    try:
        result = subprocess.run(['alembic', 'current'], 
                              capture_output=True, text=True, check=True)
        
        # Extraer la versión del output
        output = result.stdout.strip()
        if 'current' in output.lower() and 'none' not in output.lower():
            # Formato típico: "INFO [alembic.runtime.migration] Context impl PostgresqlImpl."
            # seguido de la versión
            lines = output.split('\n')
            for line in lines:
                if len(line.strip()) > 10 and 'INFO' not in line and 'Context' not in line:
                    version = line.strip()
                    if version and version != '(head)':
                        logger.info(f"📋 Versión actual de migración: {version}")
                        return version
        
        logger.info("📋 No hay migraciones aplicadas")
        return None
        
    except subprocess.CalledProcessError as e:
        logger.warning(f"⚠️ Error obteniendo versión actual: {e}")
        return None

def get_target_migration_version():
    """Obtiene la versión objetivo (head) de las migraciones"""
    try:
        result = subprocess.run(['alembic', 'heads'], 
                              capture_output=True, text=True, check=True)
        
        # Extraer la versión head
        output = result.stdout.strip()
        lines = output.split('\n')
        for line in lines:
            line = line.strip()
            if line and 'INFO' not in line and len(line) > 5:
                head_version = line.split()[0]  # Primera palabra suele ser el hash
                logger.info(f"🎯 Versión objetivo (head): {head_version}")
                return head_version
        
        logger.warning("⚠️ No se pudo determinar la versión head")
        return None
        
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Error obteniendo versión head: {e}")
        return None

def run_migrations():
    """Ejecuta las migraciones de Alembic"""
    try:
        logger.info("🔄 Ejecutando migraciones de Alembic...")
        result = subprocess.run(['alembic', 'upgrade', 'head'], 
                              capture_output=True, text=True, check=True)
        
        logger.info("✅ Migraciones ejecutadas exitosamente")
        logger.info(f"📋 Output: {result.stdout}")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Error ejecutando migraciones: {e}")
        logger.error(f"📋 Error output: {e.stderr}")
        return False

def check_if_seeded():
    """Verifica si los datos iniciales ya fueron cargados"""
    try:
        database_url = os.getenv('DATABASE_URL')
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Verificar si existen datos en la tabla campaigns
            result = conn.execute(text("SELECT COUNT(*) FROM campaigns"))
            count = result.scalar()
            
            if count > 0:
                logger.info(f"📊 Base de datos ya tiene {count} campañas cargadas")
                return True
            else:
                logger.info("📊 Base de datos vacía, necesita datos iniciales")
                return False
                
    except Exception as e:
        logger.warning(f"⚠️ No se pudo verificar datos existentes: {e}")
        return False

def run_seed():
    """Ejecuta el script de carga de datos iniciales"""
    try:
        logger.info("📊 Cargando datos iniciales...")
        result = subprocess.run(['python', 'seed.py'], 
                              capture_output=True, text=True, check=True)
        
        logger.info("✅ Datos iniciales cargados exitosamente")
        logger.info(f"📋 Output: {result.stdout}")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Error cargando datos iniciales: {e}")
        logger.error(f"📋 Error output: {e.stderr}")
        return False

def main():
    """Función principal que orquesta todo el proceso"""
    logger.info("🚀 Iniciando proceso inteligente de migraciones...")
    
    # 1. Verificar conexión a la base de datos
    if not check_database_connection():
        logger.error("❌ No se puede conectar a la base de datos")
        sys.exit(1)
    
    # 2. Verificar estado de migraciones
    current_version = get_current_migration_version()
    target_version = get_target_migration_version()
    
    # 3. Decidir si ejecutar migraciones
    migrations_needed = True
    
    if current_version and target_version:
        if current_version == target_version:
            logger.info("✅ Las migraciones ya están al día")
            migrations_needed = False
        else:
            logger.info(f"🔄 Migración necesaria: {current_version} → {target_version}")
    elif current_version is None:
        logger.info("🔄 Primera vez ejecutando migraciones")
    
    # 4. Ejecutar migraciones si es necesario
    if migrations_needed:
        if not run_migrations():
            logger.error("❌ Fallo en migraciones")
            sys.exit(1)
    else:
        logger.info("⏭️ Saltando migraciones (ya están aplicadas)")
    
    # 5. Verificar si necesita datos iniciales
    if not check_if_seeded():
        if not run_seed():
            logger.error("❌ Fallo cargando datos iniciales")
            sys.exit(1)
    else:
        logger.info("⏭️ Saltando carga de datos (ya existen)")
    
    logger.info("🎉 ¡Proceso completado exitosamente!")
    logger.info("📋 Credenciales por defecto:")
    logger.info("   👤 Usuario: admin@admin.com")
    logger.info("   🔑 Contraseña: admin")

if __name__ == "__main__":
    main()