# inventario/signals.py (o como se llame tu app)
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Movimiento, StockActual  # 🌟 Asegúrate de importar tus modelos

@receiver(post_save, sender=Movimiento)
def actualizar_stock(sender, instance, created, **kwargs):
    if created:
        # Aquí va tu lógica actual para sumar al stock destino...
        
        # 🌟 NUEVO CASO: TRANSFORMATIVO / PRODUCTO TERMINADO
        if instance.lote_origen:
            stock_padre = StockActual.objects.filter(
                lote=instance.lote_origen,
                kilos_netos__gt=0
            ).first()
            
            if stock_padre:
                stock_padre.kilos_netos -= instance.kilos_netos 
                stock_padre.unidades -= instance.unidades 
                stock_padre.save() # ⚠️ Ojo: Corregí un typo aquí, decía stock_parent.save()