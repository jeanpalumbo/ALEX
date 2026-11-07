# Genera app.html (para la vista previa) e index.html (app web instalable) desde src.html
s=open('src.html').read().replace('/*UNITS*/',open('units.js').read()).replace('/*HERO*/',open('hero.js').read())
open('app.html','w').write(s)
head='<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="theme-color" content="#f26a1b"><link rel="manifest" href="manifest.webmanifest"><link rel="icon" href="icon-192.png"><link rel="apple-touch-icon" href="icon-192.png"></head><body style="margin:0">'
open('index.html','w').write(head+s+'</body></html>')
