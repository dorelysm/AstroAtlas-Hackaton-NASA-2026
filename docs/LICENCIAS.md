# Licencias y atribución de los datos

Estado a 15 nov 2026. **"Comprobado"** = se leyó la condición en la propia documentación de la fuente durante el proyecto.
**"Por comprobar"** = es lo que sabemos de la fuente pero no se pudo abrir su página de licencia (en la comprobación del 15 nov
dos servidores —SEDAC y Copernicus— rechazaron la conexión): hay que abrirla antes de la entrega.

| Datos | Fuente | Licencia / condiciones | Estado | Qué hay que citar |
|---|---|---|---|---|
| Topografía de la Tierra | Copernicus DEM GLO-90 (ESA / Comisión Europea, vía AWS Open Data) | Uso libre y gratuito con atribución a Copernicus | Por comprobar | "Contains modified Copernicus data" (año de los datos). Texto exacto en la página de licencia de Copernicus DEM |
| Temperatura de superficie | NASA MODIS MOD11C3 | Datos abiertos de NASA EOSDIS | Por comprobar | Citar el producto y su DOI (LP DAAC) |
| Polvo y viento (contexto) | NASA MERRA-2 (M2TMNXAER, M2TMNXSLV v5.12.4; GES DISC) | Abierto, exige la licencia GESDISC (aceptada) | Comprobado (la descarga funciona) | GMAO (2015), MERRA-2 tavgM_2d_aer_Nx y tavgM_2d_slv_Nx, y el DOI del producto; Gelaro et al. (2017), *J. Climate* 30, 5419-5454 |
| Pits lunares | Losarcos y Dombard (2026), Zenodo 10.5281/zenodo.20516852 (de LROC QuickMap, Wagner y Robinson) | CC BY 4.0 | Comprobado (API de Zenodo) | Losarcos y Dombard (2026) y Wagner y Robinson (2014) |
| Tubos de lava terrestres | Pyroduct Digital Catalog v1, Zenodo 10.5281/zenodo.14535886 | CC BY 4.0 | Comprobado (LICENSE.txt y README) | Romio, F. A. P. y Lobosco, G. (2024), doi:10.5281/zenodo.14535886 |
| Cuevas de Marte | USGS Astrogeology, Mars Global Cave Candidate Catalog (Cushing; release PDS 2019) | Dominio público (USGS) | Por comprobar (se leyó el README y el XML, no el texto de licencia) | Cushing, G. E., Mars Global Cave Candidate Catalog, USGS/PDS (2019) |
| Inercia térmica de Marte (experimento) | MGS-TES, Putzig y Mellon 2007; PDS Geosciences `mgs-m-tes-5-timap-v1` | Abierto (NASA PDS) | Por comprobar | Putzig, N. E. y Mellon, M. T. (2007), *Icarus* 191, 68-94, doi:10.1016/j.icarus.2007.05.013 |
| Neutrones epitérmicos de Marte (hielo polar) | NASA PDS, Mars Odyssey GRS, Averaged Neutron Data v2.0 (`ODY-M-GRS-5-AND-V2.0`) | Abierto (NASA PDS) | Por comprobar | GRS Science Team (Univ. de Arizona), DOI 10.17189/1522868, PDS Geosciences Node |
| Vegetación (marca) | NASA MODIS MOD13C2 v061 | Datos abiertos de NASA EOSDIS | Por comprobar | Citar el producto y su DOI (LP DAAC) |
| Nieve | NASA MODIS MOD10CM | Datos abiertos de NASA EOSDIS | Por comprobar | Citar el producto y su DOI (NSIDC DAAC) |
| Humedad del suelo (solo diagnóstico) | NASA GLDAS Noah 2.1 (GES DISC) | Abierto, exige aceptar la licencia GESDISC en Earthdata (hecho) | Comprobado (descarga funciona) | Rodell et al. (2004), *BAMS* 85, 381-394, y el DOI del producto |
| Geología de la Tierra | GLiM v1.0 (Hartmann y Moosdorf 2012), PANGAEA | **CC-BY 3.0**. **No es de la NASA** (excepción aprobada por el equipo el 14 nov 2026) | Comprobado | Hartmann, J. y Moosdorf, N. (2012), *Geochem. Geophys. Geosyst.* 13, Q12004, doi:10.1029/2012GC004370; datos doi:10.1594/PANGAEA.788537 |
| Asentamientos | NASA SEDAC GRUMP v1 Settlement Points Rev. 01 | Datos abiertos de SEDAC (normalmente CC BY 4.0) | Por comprobar | CIESIN et al. (2017), doi:10.7927/H4BC3WG1, NASA SEDAC |
| Capa de análogos | USGS, Hunter (2020) "Known Terrestrial Analog Sites for Planetary Science" | Dominio público (metadatos del USGS); los cráteres vienen de la Earth Impact Database (Univ. de New Brunswick) | Comprobado en los metadatos | Hunter (2020), doi:10.5066/P9J72921; citar también la Earth Impact Database |
| Luna: topografía, térmica, hielo | LRO LOLA, LRO Diviner, Lunar Prospector GRS (NASA PDS) | Abiertos (PDS) | Por comprobar | Citar cada instrumento y su volumen PDS |
| Marte: topografía, hielo | MGS MOLA, Mars Odyssey GRS (NASA PDS) | Abiertos (PDS) | Por comprobar | Citar cada instrumento y su volumen PDS |
| Coordenadas de sitios lunares | Tablas LROC (Wagner et al. 2017, *Icarus* 283, 92-103; ASU/NASA) | Publicación científica abierta | Comprobado (se leyeron las tablas) | Wagner et al. 2017 |

## Qué se redistribuye en el repositorio
- `demo_data/` (≈ 0,5 MB) contiene **valores derivados** (estadísticos por celda de 50 km), no los datos originales. Aun así, cada fuente
  anterior pide ser citada; la cita está en este archivo, en `docs/FUENTES.md` y en el README.
- Los datos brutos y las descargas **no** se versionan (`data/` está en `.gitignore`).
- GLiM (CC-BY 3.0) permite redistribuir trabajos derivados **si se atribuye**: esa atribución es obligatoria en la entrega.

## Pendiente antes de la entrega
1. Abrir las páginas de licencia marcadas "Por comprobar" y copiar el texto exacto de atribución que pidan (sobre todo Copernicus y SEDAC).
2. Poner en la presentación y en la app una línea de créditos con las fuentes principales.

## Dundas et al. 2021 (coordenadas de hielo somero)
Del artículo (copia abierta en HAL) solo se toman **ocho pares de coordenadas** (hechos, no texto); la licencia exacta de la copia de HAL **por comprobar**. El data release del USGS (10.5066/P9Y8FR1R) es CC0 pero no se descargó. El PDF y su texto extraído quedan en `data/raw/swim/` (no versionado).

## Catálogo CAFE de la ESA (Preston, Grady y Barber 2012)
Solo se toman hechos (nombres, asignación a cuerpo y coordenadas), no texto. La licencia o condiciones de reutilización del PDF (alojado en un servidor de terceros) **están por comprobar**; el documento es un informe de la ESA y la Open University.

## Mapa de permafrost de Obu et al. (2018)
Licencia **CC-BY 3.0** (indicada en el registro de PANGAEA): hay que citar a los autores y el DOI. Se usa solo para clasificar celdas y sitios; no se redistribuye el archivo.

## Natural Earth (nombres de lugares y países)
Dominio público (sin condiciones de atribución; se cita igualmente en los créditos de la app). Los límites son a escala 1:110m y no representan posiciones políticas.

## Imágenes de la NASA en la app (GIBS y Trek)
Las vistas desde órbita se descargan en vivo de los servicios abiertos de la NASA y se muestran **con el crédito de cada producto** (MODIS: NASA GIBS; Blue Marble: NASA Earth Observatory; Viking MDIM 2.1: NASA/JPL/USGS; LRO WAC: NASA/GSFC/ASU). **No se redistribuyen en el repositorio.** Según las pautas de uso de medios de la NASA, el material de la NASA puede usarse con fines informativos y educativos citando la fuente y sin sugerir que la agencia respalda el proyecto (la app lo dice en sus créditos). **Por comprobar** por el equipo: las condiciones exactas de cada producto en las páginas de GIBS y Trek.
