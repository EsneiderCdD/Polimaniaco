from app import create_app
from app.extensions import db
from app.models.models import (
    AnalisisResultado,
    MetricasTecnologia,
    MetricasUbicacion,
    MetricasModalidad,
    MetricasGenerales
)
from collections import Counter
from datetime import datetime

def calcular_metricas():
    app = create_app()
    with app.app_context():
        resultados = AnalisisResultado.query.all()
        total_ofertas = len(resultados)

        if total_ofertas == 0:
            print("No hay ofertas para calcular métricas.")
            return

        # --------- Tecnologías ---------
        tech_counter = Counter()
        categorias = {}

        for r in resultados:
            for cat in [
                "lenguajes", "frameworks", "librerias", "bases_datos",
                "nube_devops", "control_versiones", "arquitectura_metodologias",
                "integraciones", "inteligencia_artificial",
                "ofimatica_gestion", "ciberseguridad", "marketing_digital",
                "erp_lowcode"
            ]:
                items = getattr(r, cat)
                if items:
                    for t in [x.strip() for x in items.split(",")]:
                        if t:
                            tech_counter[t] += 1
                            categorias[t] = cat

        # Guardar métricas de tecnologías
        db.session.query(MetricasTecnologia).delete()
        for t, count in tech_counter.items():
            porcentaje = round((count / total_ofertas) * 100, 2)
            m = MetricasTecnologia(
                nombre_tecnologia=t,
                categoria=categorias[t],
                conteo=count,
                porcentaje=porcentaje,
                fecha_calculo=datetime.utcnow()
            )
            db.session.add(m)

        # --------- Ubicaciones ---------
        ubicaciones = Counter(r.ciudad for r in resultados if r.ciudad)
        db.session.query(MetricasUbicacion).delete()
        for ciudad, count in ubicaciones.items():
            porcentaje = round((count / total_ofertas) * 100, 2)
            m = MetricasUbicacion(
                ciudad=ciudad,
                conteo=count,
                porcentaje=porcentaje,
                fecha_calculo=datetime.utcnow()
            )
            db.session.add(m)

        # --------- Modalidades ---------
        modalidades = Counter(r.modalidad for r in resultados if r.modalidad)
        db.session.query(MetricasModalidad).delete()
        for mod, count in modalidades.items():
            porcentaje = round((count / total_ofertas) * 100, 2)
            m = MetricasModalidad(
                modalidad=mod,
                conteo=count,
                porcentaje=porcentaje,
                fecha_calculo=datetime.utcnow()
            )
            db.session.add(m)

        # --------- Generales ---------
        promedio_compat = round(
            sum((r.compatibilidad or 0) for r in resultados) / total_ofertas, 2
        )
        db.session.query(MetricasGenerales).delete()
        m_gen = MetricasGenerales(
            total_ofertas=total_ofertas,
            promedio_compatibilidad=promedio_compat,
            fecha_calculo=datetime.utcnow()
        )
        db.session.add(m_gen)

        db.session.commit()
        print("✅ Métricas calculadas y guardadas correctamente.")

if __name__ == "__main__":
    calcular_metricas()
