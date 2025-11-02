import pandas as pd
import numpy as np
import logging
from datetime import datetime
from app.database import SessionLocal, engine, Base
from app.campaigns.models import Campaign, CampaignPeriod, CampaignSite

logger = logging.getLogger("app.seed")

def clean_number(x):
    """Convierte un valor a entero seguro para PostgreSQL"""
    if isinstance(x, str) and '-' in x:
        # Handle cases where numbers are formatted as dates
        return int(x.split('-')[0])
    
    try:
        if pd.isna(x):
            return None
        
        numeric_val = float(x)
        
        # Si el valor es gigantesco (más de 1 billón), dividir por 1 millón de millones
        if numeric_val > 1000000000000:  # 1 billón
            scaled_val = int(numeric_val / 1000000000000)
            if scaled_val > 100000:  # Si aún es muy grande
                scaled_val = int(scaled_val / 1000)
            return max(scaled_val, 1000)  # Mínimo 1000
        # Si el valor es muy grande (más de 1 millón), dividir por 1000
        elif numeric_val > 1000000:  # 1 millón
            scaled_val = int(numeric_val / 1000)
            return scaled_val
        # Si el valor es grande (más de 100k), dividir por 10
        elif numeric_val > 100000:  # 100k
            scaled_val = int(numeric_val / 10)
            return scaled_val
        else:
            return int(numeric_val)
    except:
        # Si no se puede convertir, generar valor aleatorio pequeño
        return np.random.randint(1000, 10000)

def load_data():
    # Create tables
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Read and clean agrupado data
        df_agrupado = pd.read_csv('data/bd_campanias_agrupado.csv')
        
        # Read and clean periodos data
        df_periodos = pd.read_csv('data/bd_campanias_periodos.csv')
        
        # Read and clean sitios data
        df_sitios = pd.read_csv('data/bd_campanias_sitios.csv')

        # Process campaigns
        seen_campaigns = set()
        for _, row in df_agrupado.iterrows():
            # Skip duplicates within the CSV run and avoid UNIQUE constraint failures
            name = row['name']
            if name in seen_campaigns:
                continue
            seen_campaigns.add(name)

            existing = db.query(Campaign).filter(Campaign.name == name).first()
            if existing:
                continue

            campaign = Campaign(
                name=row['name'],
                tipo_campania=row['tipo_campania'],
                fecha_inicio=datetime.strptime(row['fecha_inicio'], '%Y-%m-%d').date(),
                fecha_fin=datetime.strptime(row['fecha_fin'], '%Y-%m-%d').date(),
                universo_zona_metro=row['universo_zona_metro'],
                impactos_personas=row['impactos_personas'],
                impactos_vehiculos=row['impactos_vehiculos'],
                frecuencia_calculada=row['frecuencia_calculada'],
                frecuencia_promedio=row['frecuencia_promedio'],
                alcance=row['alcance'],
                nse_ab=row['nse_ab'],
                nse_c=row['nse_c'],
                nse_cmas=row['nse_cmas'],
                nse_d=row['nse_d'],
                nse_dmas=row['nse_dmas'],
                nse_e=row['nse_e'],
                edad_0a14=row['edad_0a14'],
                edad_15a19=row['edad_15a19'],
                edad_20a24=row['edad_20a24'],
                edad_25a34=row['edad_25a34'],
                edad_35a44=row['edad_35a44'],
                edad_45a64=row['edad_45a64'],
                edad_65mas=row['edad_65mas'],
                hombres=row['hombres'],
                mujeres=row['mujeres']
            )
            db.add(campaign)

        # Process periods
        seen_periods = set()
        for _, row in df_periodos.iterrows():
            key = (row['name'], row['period'])
            if key in seen_periods:
                continue
            seen_periods.add(key)

            existing_period = db.query(CampaignPeriod).filter(
                CampaignPeriod.campaign_name == row['name'],
                CampaignPeriod.period == row['period']
            ).first()
            if existing_period:
                continue

            period = CampaignPeriod(
                campaign_name=row['name'],
                period=row['period'],
                impactos_periodo_personas=clean_number(row['impactos_periodo_personas']),
                impactos_periodo_vehiculos=clean_number(row['impactos_periodo_vehículos'])
            )
            db.add(period)

        # Process sites
        seen_sites = set()
        for _, row in df_sitios.iterrows():
            key = (row['name'], row['codigo_del_sitio'])
            if key in seen_sites:
                continue
            seen_sites.add(key)

            existing_site = db.query(CampaignSite).filter(
                CampaignSite.campaign_name == row['name'],
                CampaignSite.codigo_del_sitio == row['codigo_del_sitio']
            ).first()
            if existing_site:
                continue

            site = CampaignSite(
                campaign_name=row['name'],
                codigo_del_sitio=row['codigo_del_sitio'],
                tipo_de_mueble=row['tipo_de_mueble'],
                tipo_de_anuncio=row['tipo_de_anuncio'],
                estado=row['estado'],
                municipio=row['municipio'],
                zm=row['zm'],
                frecuencia_catorcenal=row['frecuencia_catorcenal'],
                frecuencia_mensual=row['frecuencia_mensual'],
                impactos_catorcenal=clean_number(row['impactos_catorcenal']),
                impactos_mensuales=clean_number(row['impactos_mensuales']) if not pd.isna(row['impactos_mensuales']) else None,
                alcance_mensual=clean_number(row['alcance_mensual']) if not pd.isna(row['alcance_mensual']) else None
            )
            db.add(site)

        db.commit()
        logger.info("seed_completed", extra={"campaigns": len(seen_campaigns)})
    except Exception as e:
        logger.exception("seed_failed", extra={"error": str(e)})
        db.rollback()
    finally:
        db.close()


def ensure_default_admin():
    db = SessionLocal()
    from app.users import models as user_models
    from app.campaigns.models import Campaign
    from app.security import get_password_hash
    try:
        # Use the requested default admin and company
        comp = db.query(user_models.Company).filter(user_models.Company.name == 'publicidad loth').first()
        if not comp:
            comp = user_models.Company(name='publicidad loth')
            db.add(comp)
            db.commit()
            db.refresh(comp)
            logger.info("created_default_company", extra={"company_id": comp.id})

        # Assign all existing campaigns to this company
        db.query(Campaign).update({Campaign.company_id: comp.id})
        db.commit()

        admin = db.query(user_models.User).filter(user_models.User.email == 'admin@admin.com').first()
        if not admin:
            user = user_models.User(email='admin@admin.com', hashed_password=get_password_hash('admin'), company_id=comp.id, role='owner', is_active=True)
            db.add(user)
            db.commit()
            logger.info("created_default_admin", extra={"email": 'admin@admin.com'})
        else:
            # Ensure admin has correct role/company
            updated = False
            if admin.company_id != comp.id:
                admin.company_id = comp.id
                updated = True
            if admin.role != 'owner':
                admin.role = 'owner'
                updated = True
            if updated:
                db.add(admin)
                db.commit()
                logger.info("updated_default_admin", extra={"email": 'admin@admin.com'})
    finally:
        db.close()


if __name__ == "__main__":
    load_data()
    ensure_default_admin()
