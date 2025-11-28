#!/usr/bin/env python3
"""
Script de utilidades para gestión del Dashboard
"""
import asyncio
import sys
from database import db
from scheduler import scheduler
from services import binance_p2p_service, bcv_service, bvc_service
from datetime import date


async def poblar_acciones_ejemplo():
    """Poblar base de datos con acciones reales de BVC"""
    print("📥 Poblando base de datos con acciones de BVC...")
    
    acciones_bvc = [
        {"codigo": "ABC.A", "nombre": "Banco ABC - Clase A", "acciones_circulacion": 1000000000},
        {"codigo": "ALZ.B", "nombre": "Almacenes La Estrella - Clase B", "acciones_circulacion": 800000000},
        {"codigo": "BNC", "nombre": "Banco Nacional de Crédito", "acciones_circulacion": 1500000000},
        {"codigo": "BPV", "nombre": "Banco Provincial", "acciones_circulacion": 2000000000},
        {"codigo": "BVCC", "nombre": "Bolsa de Valores de Caracas", "acciones_circulacion": 500000000},
        {"codigo": "BVL", "nombre": "Banco de Venezuela", "acciones_circulacion": 1200000000},
        {"codigo": "CCR", "nombre": "Caroní", "acciones_circulacion": 600000000},
        {"codigo": "MERC", "nombre": "Banco Mercantil", "acciones_circulacion": 1800000000},
    ]
    
    for accion in acciones_bvc:
        success = await db.insert_accion(
            codigo=accion["codigo"],
            nombre=accion["nombre"],
            acciones_circulacion=accion["acciones_circulacion"]
        )
        if success:
            print(f"✅ Acción {accion['codigo']} creada")
        else:
            print(f"⚠️  Acción {accion['codigo']} ya existe o hubo un error")


async def test_bcv():
    """Probar conexión con BCV"""
    print("🔍 Probando scraping del BCV...")
    
    tasa = bcv_service.get_official_rate()
    if tasa:
        print(f"✅ Tasa oficial BCV: {tasa['tasa_oficial']:.2f} Bs/USD")
        print(f"   Fecha: {tasa['fecha']}")
    else:
        print("❌ Error al obtener tasa del BCV")


async def test_binance_p2p():
    """Probar conexión con Binance P2P"""
    print("🔍 Probando Binance P2P...")
    
    # Top 5 ofertas
    ofertas = binance_p2p_service.get_top5_usdt_ves()
    if ofertas:
        print(f"✅ Top 5 ofertas USDT/VES:")
        for i, oferta in enumerate(ofertas, 1):
            print(f"   {i}. {oferta['price']:.2f} Bs/USDT - Vol: {oferta['volume_usdt']:.2f} USDT - {oferta['merchant']}")
    else:
        print("❌ Error al obtener ofertas de Binance P2P")
    
    # Precio promedio
    precio_promedio = binance_p2p_service.get_precio_promedio_compra()
    if precio_promedio:
        print(f"\n✅ Precio promedio ponderado: {precio_promedio:.2f} Bs/USDT")
    else:
        print("❌ Error al calcular precio promedio")


async def test_bvc():
    """Probar conexión con BVC"""
    print("🔍 Probando extracción de datos BVC...")
    print("⚠️  NOTA: Esto puede tardar varios minutos...")
    
    # Primero obtener tasas
    print("\n1. Obteniendo tasas de cambio...")
    tasa_bcv = bcv_service.get_official_rate()
    tasa_p2p = binance_p2p_service.get_precio_promedio_compra()
    
    if not tasa_bcv or not tasa_p2p:
        print("❌ No se pudieron obtener las tasas de cambio")
        return
    
    print(f"   Oficial: {tasa_bcv['tasa_oficial']:.2f} Bs/USD")
    print(f"   Paralelo: {tasa_p2p:.2f} Bs/USD")
    
    # Obtener precios BVC (solo primeras 3 acciones para testing)
    print("\n2. Obteniendo precios de BVC (testing con 3 acciones)...")
    simbolos_test = ['BNC', 'BPV', 'MERC']
    
    for simbolo in simbolos_test:
        print(f"\n   Procesando {simbolo}...")
        datos = bvc_service.obtener_datos_desnudos(simbolo)
        if datos:
            df = bvc_service.procesar_datos_accion(simbolo, datos)
            if not df.empty and 'PRECIO_CIE' in df.columns:
                ultimo_precio = df.iloc[0]['PRECIO_CIE'] if not df.empty else None
                print(f"   ✅ {simbolo}: {ultimo_precio:.2f} Bs" if ultimo_precio else f"   ⚠️ {simbolo}: Sin datos")
        else:
            print(f"   ❌ {simbolo}: Error al obtener datos")


async def actualizar_ahora():
    """Ejecutar actualización manual inmediata"""
    print("🔄 Ejecutando actualización manual de precios BVC...")
    print("⚠️  ADVERTENCIA: Esto tardará varios minutos...")
    print("   - Extraerá datos de ~30 acciones")
    print("   - Consultará BCV y Binance P2P")
    print("   - Procesará y guardará en Supabase\n")
    
    respuesta = input("¿Continuar? (s/n): ")
    if respuesta.lower() != 's':
        print("❌ Actualización cancelada")
        return
    
    await scheduler.ejecutar_ahora("bvc")
    print("✅ Actualización completada")


async def ver_resumen():
    """Ver resumen del mercado"""
    print("📊 Obteniendo resumen del mercado...")
    
    resumen = await db.get_resumen_mercado()
    
    print(f"\n{'='*60}")
    print(f"Total de acciones: {resumen.get('total_acciones', 0)}")
    print(f"Capitalización total (Oficial): ${resumen.get('capitalizacion_total_oficial', 0):,.2f}")
    print(f"Capitalización total (Paralelo): ${resumen.get('capitalizacion_total_paralelo', 0):,.2f}")
    print(f"Fecha de actualización: {resumen.get('fecha_actualizacion', 'N/A')}")
    print(f"{'='*60}\n")
    
    if resumen.get('acciones_detalle'):
        print("Detalle de acciones:")
        print(f"{'Código':<10} {'Precio Oficial':<15} {'Precio Paralelo':<15}")
        print("-" * 40)
        for accion in resumen['acciones_detalle'][:10]:
            codigo = accion.get('codigo', 'N/A')
            precio_ofi = accion.get('precio_oficial', 0)
            precio_par = accion.get('precio_paralelo', 0)
            print(f"{codigo:<10} ${precio_ofi:>13.2f} ${precio_par:>13.2f}")


async def verificar_config():
    """Verificar configuración del sistema"""
    print("🔧 Verificando configuración del sistema...\n")
    
    configs = [
        'hora_actualizacion_bvc',
        'timezone',
        'ultima_actualizacion_bvc'
    ]
    
    for config in configs:
        valor = await db.get_config(config)
        print(f"{config}: {valor or 'No configurado'}")


def mostrar_menu():
    """Mostrar menú de opciones"""
    print("\n" + "="*60)
    print("🚀 DASHBOARD RENTA VARIABLE - UTILIDADES")
    print("="*60)
    print("1. Poblar base de datos con acciones de BVC")
    print("2. Probar scraping BCV (tasa oficial)")
    print("3. Probar Binance P2P (tasa paralelo)")
    print("4. Probar extracción BVC (3 acciones de prueba)")
    print("5. Actualizar precios ahora (¡LENTO! ~5 min)")
    print("6. Ver resumen del mercado")
    print("7. Verificar configuración")
    print("0. Salir")
    print("="*60)


async def main():
    """Función principal"""
    while True:
        mostrar_menu()
        
        try:
            opcion = input("\nSelecciona una opción: ").strip()
            
            if opcion == "0":
                print("👋 ¡Hasta luego!")
                break
            elif opcion == "1":
                await poblar_acciones_ejemplo()
            elif opcion == "2":
                await test_bcv()
            elif opcion == "3":
                await test_binance_p2p()
            elif opcion == "4":
                await test_bvc()
            elif opcion == "5":
                await actualizar_ahora()
            elif opcion == "6":
                await ver_resumen()
            elif opcion == "7":
                await verificar_config()
            else:
                print("❌ Opción inválida")
            
            input("\nPresiona Enter para continuar...")
            
        except KeyboardInterrupt:
            print("\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            input("\nPresiona Enter para continuar...")


if __name__ == "__main__":
    asyncio.run(main())
