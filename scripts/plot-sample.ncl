load "/opt/shapefiles/shapefile_utils.ncl"

shapefile_root = "/opt/shapefiles"

procedure attach_china_map(wks, plot)
local res, res_scs, res_small_map, map_scs
begin

  res = True
  res@gsLineThicknessF = 3.0

  plot@china_map = gsn_add_shapefile_polylines(wks, plot, shapefile_root + "/china.shp", res)
  plot@china_nine_dotted_line_map = gsn_add_shapefile_polylines(wks, plot, shapefile_root + "/china_nine_dotted_line.shp", res)

  res_scs = True
  res_scs@gsnDraw = False
  res_scs@gsnFrame = False
  res_scs@vpWidthF = 0.15
  res_scs@mpMinLonF := 105.0
  res_scs@mpMaxLonF := 123.0
  res_scs@mpMinLatF := 2.0
  res_scs@mpMaxLatF := 23.5
  res_scs@mpOceanFillColor = 0
  res_scs@tmXBOn = False
  res_scs@tmXTOn = False
  res_scs@tmYLOn = False
  res_scs@tmYROn = False

  map_scs = gsn_csm_map(wks, res_scs)

  plot@china_map_in_small_map = gsn_add_shapefile_polylines(wks, map_scs, shapefile_root + "/china.shp", res)
  plot@china_nine_dotted_line_in_small_map = gsn_add_shapefile_polylines(wks, map_scs, shapefile_root + "/china_nine_dotted_line.shp", res)

  res_small_map = True
  res_small_map@amParallelPosF = -0.495
  res_small_map@amOrthogonalPosF = 0.495
  res_small_map@amJust = "BottomLeft"
  plot@south_china_sea_small_map = gsn_add_annotation(plot, map_scs, res_small_map)

end

wks = gsn_open_wks("pdf", "china")

res_map = True
res_map@gsnMaximize = True
res_map@gsnDraw = False
res_map@gsnFrame = False
res_map@gsnAddCyclic = False
res_map@mpLimitMode = "LatLon"
res_map@mpMinLonF = 70
res_map@mpMaxLonF = 140
res_map@mpMinLatF = 10
res_map@mpMaxLatF = 60
res_map@pmTickMarkDisplayMode = "Always"

plot = gsn_csm_map(wks, res_map)
attach_china_map(wks, plot)
draw(plot)
frame(wks)
