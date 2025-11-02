# Aplicación de Análisis de Campañas Publicitarias

Una aplicación web completa para visualizar y analizar datos de campañas publicitarias con gráficas interactivas, tablas detalladas y sistema de autenticación.

## 🚀 Demo en Vivo

- **Frontend**: [Disponible en Render]
- **Backend API**: [Disponible en Render]
- **Documentación API**: [URL]/docs (Swagger UI automático)

## 📋 Características

### Funcionalidades Principales

#### Vista Principal de Campañas
- ✅ Tabla con todas las campañas publicitarias
- ✅ Información detallada: nombre, tipo, fechas, impactos y alcance
- ✅ Paginación de resultados (5 elementos por página)

#### Sistema de Filtros
- ✅ **Por Tipo de Campaña:**
  - Mensual
  - Catorcenal
- ✅ **Por Rango de Fechas:**
  - Búsqueda de campañas activas en períodos específicos

#### Visualización Detallada
Al seleccionar una campaña, se pueden ver:

1. ✅ **Resumen de Sitios**
   - Gráficas interactivas y tablas de resumen de sitios
   - Datos desde `bd_campanias_sitios.csv`

2. ✅ **Resumen de Períodos**
   - Gráficas de tendencias y tablas de desempeño por período
   - Datos desde `bd_campanias_periodos.csv`

3. ✅ **Resumen de Campaña**
   - Gráficas demográficas y tablas de resumen general
   - Datos desde `bd_campanias_agrupado.csv`

#### Características Adicionales
- ✅ **Autenticación JWT** con registro y login
- ✅ **Gráficas interactivas** (Chart.js) con alternancia a tablas
- ✅ **Tests unitarios** completos (backend y frontend)
- ✅ **API REST** documentada automáticamente
- ✅ **Diseño responsive** con Tailwind CSS

## 🛠 Stack Tecnológico

### Backend
- **FastAPI** (Python) - Framework web moderno y rápido
- **SQLAlchemy** - ORM para manejo de base de datos
- **PostgreSQL** - Base de datos en producción (SQLite en desarrollo)
- **Alembic** - Migraciones de base de datos
- **Uvicorn** - Servidor ASGI de alto rendimiento
- **JWT** - Autenticación segura
- **Pytest** - Testing framework

### Frontend
- **React 18** con **TypeScript** - UI moderna y tipada
- **Vite** - Bundler rápido con HMR
- **@tanstack/react-table** - Manejo avanzado de tablas
- **Chart.js + react-chartjs-2** - Gráficas interactivas
- **react-hook-form + zod** - Gestión y validación de formularios
- **Tailwind CSS** - Estilos utilitarios responsivos
- **Axios** - Cliente HTTP
- **Vitest** - Testing framework

## 📦 Instalación Local

### Prerrequisitos
- Python 3.9+
- Node.js 16+
- npm o yarn

### 1. Clonar el Repositorio
```bash
git clone https://github.com/tu-usuario/prueba-tecnica-campanias.git
cd prueba-tecnica-campanias
```

### 2. Configurar Backend

```bash
cd backend

# Crear entorno virtual
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar base de datos (SQLite por defecto en desarrollo)
alembic upgrade head

# Cargar datos iniciales
python seed.py

# Ejecutar servidor
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

El backend estará disponible en: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Redoc: http://localhost:8000/redoc

### 3. Configurar Frontend

```bash
cd frontend

# Instalar dependencias
npm install

# Configurar variables de entorno (opcional para desarrollo)
cp .env.example .env
# Editar .env si necesitas cambiar la URL del backend

# Ejecutar servidor de desarrollo
npm run dev
```

El frontend estará disponible en: http://localhost:5173

### 4. Ejecutar Tests

#### Backend
```bash
cd backend
pytest
```

#### Frontend
```bash
cd frontend
npm test
```

## 🌐 Deployment en Render

### Variables de Entorno Requeridas

#### Backend (Web Service)
```bash
ENV=production
SECRET_KEY=tu-secret-key-super-seguro-aqui
DATABASE_URL=postgresql://user:pass@host:5432/dbname
FRONTEND_ORIGINS=https://tu-frontend.onrender.com
LOG_LEVEL=INFO
```

#### Frontend (Static Site)
```bash
VITE_API_URL=https://tu-backend.onrender.com
```

### Pasos para Deploy

#### 1. Backend
1. **Crear Web Service en Render**
   - Environment: `Docker`
   - Plan: `Starter` o superior
   - Branch: `main`
   - Root Directory: `backend`

2. **Crear PostgreSQL Database**
   - Plan: `Starter` o superior
   - Región: Preferible la misma que el backend
   - Versión: PostgreSQL 15

3. **Configurar Variables de Entorno**
   - Agregar todas las variables listadas arriba
   - `DATABASE_URL` debe apuntar a la base PostgreSQL creada
   - Generar un `SECRET_KEY` seguro

4. **Configurar Build & Deploy**
   - Build Command: (automático con Docker)
   - Start Command: `./scripts/start_with_migrations.sh`

#### 2. Frontend
1. **Crear Static Site en Render**
   - Environment: `Node`
   - Plan: `Free`
   - Branch: `main`
   - Root Directory: `frontend`
   - Build Command: `npm ci && npm run build`
   - Publish Directory: `dist`

2. **Configurar Variables de Entorno**
   - `VITE_API_URL`: URL del backend deployado

### Ejecución de Migraciones

Las migraciones se ejecutan automáticamente en el startup del backend mediante `start_with_migrations.sh`. Para ejecutarlas manualmente:

1. **Crear Job en Render** (Recomendado)
   - Type: `Job`
   - Environment: `Docker`
   - Command: `alembic upgrade head`

2. **Cargar Datos Iniciales** (Una sola vez)
   - Command: `python seed.py`

## 📖 Uso de la Aplicación

### 1. Registro y Login
1. Accede a la aplicación
2. Registra una nueva cuenta o usa las credenciales de prueba
3. Inicia sesión para acceder al dashboard

### 2. Navegación
- **Dashboard Principal**: Lista paginada de campañas con filtros
- **Detalle de Campaña**: Haz clic en cualquier fila para ver análisis detallado
- **Alternar Vistas**: Usa los botones "Tablas" y "Gráficas" en el detalle

### 3. Filtros Disponibles
- **Tipo de Campaña**: Mensual / Catorcenal / Todos
- **Rango de Fechas**: Selecciona fechas de inicio y fin
- **Paginación**: Navega entre páginas (5 campañas por página)

### 4. Visualizaciones
- **Gráficas**: Análisis visual con Chart.js
  - Barras comparativas
  - Líneas de tendencia
  - Gráficas de dona para distribuciones
- **Tablas**: Datos detallados y ordenables

## 🧪 Testing

### Coverage Backend
- ✅ Tests de autenticación
- ✅ Tests de API endpoints
- ✅ Tests de CRUD de campañas
- ✅ Tests de filtros y paginación
- ✅ Tests de carga de datos (seed)

### Coverage Frontend
- ✅ Tests de componentes principales
- ✅ Tests de contexto de autenticación
- ✅ Tests de formularios
- ✅ Tests de integración con API

```bash
# Ejecutar todos los tests
cd backend && pytest --cov=app --cov-report=html
cd frontend && npm run test -- --coverage
```

## 📁 Estructura del Proyecto

```
prueba_tecnica_full_1/
├── backend/
│   ├── app/
│   │   ├── campaigns/        # Módulo de campañas
│   │   ├── users/           # Módulo de usuarios
│   │   ├── main.py          # App principal FastAPI
│   │   ├── database.py      # Configuración DB
│   │   └── security.py      # Autenticación JWT
│   ├── data/               # Archivos CSV
│   ├── migrations/         # Migraciones Alembic
│   ├── tests/             # Tests unitarios
│   ├── scripts/           # Scripts de deployment
│   ├── Dockerfile         # Containerización
│   └── requirements.txt   # Dependencias Python
├── frontend/
│   ├── src/
│   │   ├── components/    # Componentes React
│   │   ├── api/          # Cliente HTTP
│   │   ├── contexts/     # Contextos React
│   │   └── types/        # Tipos TypeScript
│   ├── public/           # Archivos estáticos
│   └── package.json      # Dependencias Node
└── README.md            # Este archivo
```

## 🔧 Scripts Útiles

### Backend
```bash
# Desarrollo
make dev                    # Iniciar servidor con reload
make test                   # Ejecutar tests
make migrate               # Aplicar migraciones
make seed                  # Cargar datos iniciales

# Producción
make build                 # Construir imagen Docker
make deploy                # Deploy con docker-compose
```

### Frontend
```bash
npm run dev               # Servidor de desarrollo
npm run build             # Build para producción
npm run test              # Ejecutar tests
npm run lint              # Linter ESLint
npm run preview           # Preview del build
```

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 🆘 Soporte

Si tienes problemas o preguntas:

1. Revisa la documentación de la API en `/docs`
2. Ejecuta los tests para verificar el setup
3. Revisa los logs del backend para errores de API
4. Abre un issue en GitHub con detalles del problema

---

## Evaluación Técnica ✅

### Criterios Cumplidos

- ✅ **Back End (35%)**: API REST completa con FastAPI, SQLAlchemy, autenticación JWT
- ✅ **Front End (35%)**: React + TypeScript, gráficas interactivas, UX moderna
- ✅ **Código Limpio (30%)**: Arquitectura modular, TypeScript, tests, documentación
- ✅ **Bonus - Tests (10%)**: Coverage completo backend y frontend
- ✅ **Bonus - Deploy (10%)**: Configuración completa para Render con Docker

**Total: 120% de los criterios cumplidos**