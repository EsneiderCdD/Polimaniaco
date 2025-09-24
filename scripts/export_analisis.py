import json
from datetime import datetime
from app import create_app, db
from app.models.models import AnalisisResultado


def export_analisis_to_json(filename=None):
    app = create_app()
    with app.app_context():
        analisis = AnalisisResultado.query.all()
        resultados = []
        for a in analisis:
            resultados.append({
                'id': a.id,
                'oferta_id': a.oferta_id,
                'fecha': a.fecha.isoformat() if a.fecha else None,
                'ciudad': a.ciudad,
                'modalidad': a.modalidad,
                'cargo': a.cargo,
                'lenguajes': a.lenguajes,
                'frameworks': a.frameworks,
                'librerias': a.librerias,
                'bases_datos': a.bases_datos,
                'nube_devops': a.nube_devops,
                'control_versiones': a.control_versiones,
                'arquitectura_metodologias': a.arquitectura_metodologias,
                'integraciones': a.integraciones,
                'inteligencia_artificial': a.inteligencia_artificial,
                'ofimatica_gestion': a.ofimatica_gestion,
                'ciberseguridad': a.ciberseguridad,
                'marketing_digital': a.marketing_digital,
                'erp_lowcode': a.erp_lowcode,
                'fecha_analisis': a.fecha_analisis.isoformat() if a.fecha_analisis else None
            })

        if not filename:
            fecha_hora = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"analisis_resultados_{fecha_hora}.json"

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(resultados, f, ensure_ascii=False, indent=4)

        print(f"✅ Archivo JSON generado: {filename}")

if __name__ == "__main__":
    export_analisis_to_json()
