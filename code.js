//@version=6
indicator('Calculador de Magnitudes Armónicas', overlay = true)

// ── Medias ──────────────────────────────────────────────────────────────────
e10  = ta.ema(close, 10)
e55  = ta.ema(close, 55)
e200 = ta.ema(close, 200)

// ── Distancias precio → media (%) ───────────────────────────────────────────
dist_price_10  = (close - e10)  / e10  * 100
dist_price_55  = (close - e55)  / e55  * 100
dist_price_200 = (close - e200) / e200 * 100

// ── Pendientes (cambio en 5 velas, %) ───────────────────────────────────────
slope10  = (e10  - e10[5])  / e10[5]  * 100
slope55  = (e55  - e55[5])  / e55[5]  * 100
slope200 = (e200 - e200[5]) / e200[5] * 100

// ── Distancias entre medias (%) ─────────────────────────────────────────────
dist_10_55  = (e10  - e55)  / e55  * 100
dist_55_200 = (e55  - e200) / e200 * 100

// ── Ratio Armónico ──────────────────────────────────────────────────────────
ratio_armonico = dist_10_55 / dist_55_200

// ── Helper: número → string sin comas de miles, 3 decimales ─────────────────
f_fmt(float v) =>
    str.tostring(v, '#.###')

// ── Header: solo en la primera vela con datos completos ─────────────────────
if barstate.isfirst
    log.info('date,close,ema10,ema55,ema200,dist_p10,dist_p55,dist_p200,slope10,slope55,slope200,dist_10_55,dist_55_200,ratio_armonico')

// ── Una línea CSV por vela ───────────────────────────────────────────────────
date_str = str.format('{0,date,yyyy-MM-dd}', time) + 'T' + str.format('{0,date,HH:mm}', time)

log.info('{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11},{12},{13}',
  date_str,
  f_fmt(close),
  f_fmt(e10),
  f_fmt(e55),
  f_fmt(e200),
  f_fmt(dist_price_10),
  f_fmt(dist_price_55),
  f_fmt(dist_price_200),
  f_fmt(slope10),
  f_fmt(slope55),
  f_fmt(slope200),
  f_fmt(dist_10_55),
  f_fmt(dist_55_200),
  f_fmt(ratio_armonico))

// ── Tabla visual (sin cambios) ───────────────────────────────────────────────
var table dataTable = table.new(position.top_right, 2, 4, bgcolor = color.new(color.black, 80), border_width = 1)

if barstate.islast
    table.cell(dataTable, 0, 0, 'Magnitud',       text_color = color.white)
    table.cell(dataTable, 1, 0, 'Valor (%)',       text_color = color.white)
    table.cell(dataTable, 0, 1, 'Relación 10/55',  text_color = color.blue)
    table.cell(dataTable, 1, 1, f_fmt(dist_10_55)  + '%', text_color = color.white)
    table.cell(dataTable, 0, 2, 'Relación 55/200', text_color = color.yellow)
    table.cell(dataTable, 1, 2, f_fmt(dist_55_200) + '%', text_color = color.white)
    table.cell(dataTable, 0, 3, 'Ratio Armónico',  text_color = color.orange)
    table.cell(dataTable, 1, 3, f_fmt(ratio_armonico),    text_color = color.white)
