#!/bin/bash

cd /root/Proyecto-

echo "🔄 Actualizando desde GitHub..."
git fetch origin
git reset --hard origin/main

echo "📦 Reiniciando servicio..."
systemctl restart chomelo

echo "✅ Listo"