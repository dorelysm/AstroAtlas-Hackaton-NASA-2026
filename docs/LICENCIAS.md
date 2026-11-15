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
