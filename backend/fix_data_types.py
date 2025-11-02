#!/usr/bin/env python3
"""
Script para corregir tipos de datos en la base de datos de producción
"""

import psycopg2
import os

def update_data_types():
    try:
        # Configurar conexión con SSL
        connection_params = {
            'host': 'dpg-ctfqhqe8ii6s73b8g1og-a.oregon-postgres.render.com',
            'database': 'campaign_analytics',
            'user': 'campaign_analytics_user',
            'password': 'U3Gz8gnsBqz6rB3N6EQ0c5S1FO9cSZht',
            'port': 5432,
            'sslmode': 'prefer'
        }
        
        print("🔄 Conectando a la base de datos...")
        conn = psycopg2.connect(**connection_params)
        cursor = conn.cursor()
        
        print("🔄 Verificando tipo de datos actual...")
        cursor.execute("""
            SELECT data_type 
            FROM information_schema.columns 
            WHERE table_name = 'campaign_periods' 
            AND column_name = 'impactos_periodo_personas'
        """)
        
        current_type = cursor.fetchone()
        if current_type:
            current_type = current_type[0]
            print(f"📊 Tipo actual: {current_type}")
            
            if current_type == 'integer':
                print("🔄 Actualizando impactos_periodo_personas a BIGINT...")
                cursor.execute("""
                    ALTER TABLE campaign_periods 
                    ALTER COLUMN impactos_periodo_personas TYPE BIGINT
                """)
                
                print("🔄 Actualizando impactos_periodo_vehiculos a BIGINT...")
                cursor.execute("""
                    ALTER TABLE campaign_periods 
                    ALTER COLUMN impactos_periodo_vehiculos TYPE BIGINT
                """)
                
                conn.commit()
                print("✅ Tipos de datos actualizados exitosamente")
            else:
                print("⏭️ Los tipos de datos ya están actualizados")
        else:
            print("❌ No se encontró la tabla campaign_periods")
            
        cursor.close()
        conn.close()
        print("✅ Proceso completado")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("🔄 Intentando con configuración SSL alternativa...")
        
        try:
            # Intentar sin SSL
            connection_params['sslmode'] = 'disable'
            conn = psycopg2.connect(**connection_params)
            cursor = conn.cursor()
            
            print("🔄 Actualizando impactos_periodo_personas a BIGINT...")
            cursor.execute("""
                ALTER TABLE campaign_periods 
                ALTER COLUMN impactos_periodo_personas TYPE BIGINT
            """)
            
            print("🔄 Actualizando impactos_periodo_vehiculos a BIGINT...")
            cursor.execute("""
                ALTER TABLE campaign_periods 
                ALTER COLUMN impactos_periodo_vehiculos TYPE BIGINT
            """)
            
            conn.commit()
            cursor.close()
            conn.close()
            print("✅ Tipos de datos actualizados exitosamente (sin SSL)")
            
        except Exception as e2:
            print(f"❌ Error en segundo intento: {e2}")

if __name__ == "__main__":
    update_data_types()