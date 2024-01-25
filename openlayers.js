var osmLayer = new ol.layer.Tile({
  source: new ol.source.OSM(),
});

var wohnheim_layer = new ol.layer.Vector({
  source: new ol.source.Vector({
    format: new ol.format.GeoJSON(),
    url: function (extent) {
      return 'http://localhost:8080/geoserver/wfs?service=wfs&request=GetFeature&version=1.1.0&typeNames=whdb:wohnheim&outputFormat=json';
    },
  }),
  style: function (feature, resolution) {
    var zoom = map.getView().getZoom(); 

    var polygonGeometry = feature.getGeometry();
    var polygonCenter = ol.extent.getCenter(polygonGeometry.getExtent());

    var iconStyle = new ol.style.Style({
      image: new ol.style.Icon({
        anchor: [0.5, 1],
        src: 'img/icon_rot.png',
        scale: 0.05,
      }),
      geometry: new ol.geom.Point(polygonCenter),
	  zIndex: 1	  
    });
	
	var iconStyle2 = new ol.style.Style({
      image: new ol.style.Icon({
        anchor: [0.5, 1],
        src: 'img/icon_gelb.png',
        scale: 0.05,
      }),
      geometry: new ol.geom.Point(polygonCenter), 
	  zIndex: 2 
    });
	
	var iconStyle3 = new ol.style.Style({
      image: new ol.style.Icon({
        anchor: [0.5, 1],
        src: 'img/icon_gruen.png',
        scale: 0.05,
      }),
      geometry: new ol.geom.Point(polygonCenter),
	  zIndex: 3
    });

    var polygonStyle = new ol.style.Style({
      fill: new ol.style.Fill({
        color: '#5c2483',
      }),
      stroke: new ol.style.Stroke({
        color: '#5c2483',
        width: 2,
      })
    });
    
    if (zoom >= 16) {
      return [polygonStyle]; 
    } else {
		if (feature.get("Verfügbarkeit") == "über 18 Monate") {
		return [iconStyle]; } else if (feature.get("Verfügbarkeit") == "7 - 18 Monate") {
			return [iconStyle2]; } else {
				return [iconStyle3]; }
    }
  },
});


var extent = ol.proj.transformExtent([12.6, 52.2, 14.4, 52.8], 'EPSG:4326', 'EPSG:3857'); 

var view = new ol.View({
	center: ol.proj.fromLonLat([13.44, 52.5]),
	zoom: 11.6,
	minZoom: 10, 
	extent: extent 
});


var berlin_maske = new ol.layer.Vector({
  source: new ol.source.Vector({
    format: new ol.format.GeoJSON(),
    url: function (extent) {
      return 'http://localhost:8080/geoserver/wfs?service=wfs&request=GetFeature&version=1.1.0&typeNames=whdb:berlin_maske_4326&outputFormat=json';
    },
  }),
  style: new ol.style.Style({
    fill: new ol.style.Fill({
      color: 'rgba(255, 255, 255, 0.6)',
    }),
    stroke: new ol.style.Stroke({
      color: 'rgba(0, 0, 0, 0)',
      width: 0, 
    }),
  }),
});



var map = new ol.Map({
  target: 'map',
  layers: [
	osmLayer, 
	wohnheim_layer,
	berlin_maske
  ],
  view: view
});  

function filterWohnheime() {

  var duscheWert = document.getElementById('dusche').value;
  var kuecheWert = document.getElementById('kueche').value;
  var moebliertWert = document.getElementById('moebliert').value;
  var barrierefreiWert = document.getElementById('barrierefrei').value;
  var wartezeitWert1 = document.getElementById('wartezeit');
  var wartezeitWert2 = wartezeitWert1.options[wartezeitWert1.selectedIndex].text;
  var maxMietpreisWert = Number(document.getElementById('maxMietpreis').value);
  var wohnWert = document.getElementById('minWohn').value;
  var personenWert = convertPersonen(document.getElementById('personen').value);


  wohnheim_layer.getSource().forEachFeature(function(feature) {
    var dusche = feature.get('Dusche'); 
    var kueche = feature.get('Küche');
    var moebliert = feature.get('möbliert');
	var barrierefrei = feature.get('behindertengerecht');
	var wartezeit = feature.get('Verfügbarkeit');
	var maxMietpreis = feature.get('Mietpreis_max');
	var maxWohn = feature.get('Wohnfläche_max');
	var minWohn = feature.get('Wohnfläche_min');
	var minPersonen = feature.get('Personen_min');
	var maxPersonen = feature.get('Personen_max');

  var isVisible = true;
    if (duscheWert !== 'option1' && duscheWert !== convertToDropdownValue(dusche)) isVisible = false;
    if (kuecheWert !== 'option1' && kuecheWert !== convertToDropdownValue(kueche)) isVisible = false;
    if (moebliertWert !== 'option1' && moebliertWert !== convertToDropdownValue(moebliert)) isVisible = false;
	if (barrierefreiWert !== 'option1' && barrierefreiWert !== convertToDropdownValue(barrierefrei)) isVisible = false;
	if (wartezeitWert1.value !== 'option1' && wartezeitWert2 !== wartezeit) isVisible = false;
	if (maxMietpreisWert <= maxMietpreis && maxMietpreisWert !== 0) isVisible = false;
	if (wohnWert >= maxWohn && wohnWert !== 0) isVisible = false;
	if (personenWert !== 100 && (personenWert < minPersonen || personenWert > maxPersonen)) isVisible = false;
	

    feature.setStyle(isVisible ? null : new ol.style.Style({ display: 'none' }));
  });
};

function convertToDropdownValue(value) {
  if (value === true) {
    return 'option2'; 
  } else if (value === false) {
    return 'option3'; 
  }
};

function convertPersonen(value) {
  switch (value) {
    case 'option1':
	  return 100;
	case 'option2':
      return 1;
    case 'option3':
      return 2;
    case 'option4':
      return 3;
    case 'option5':
      return 4;
    default:
      return 5;
  }
};

var container = document.getElementById('map-popup');
var content = document.getElementById('popup-content');
var closer = document.getElementById('popup-closer');

var popupOverlay = new ol.Overlay({
        element: container,
        autoPan: true,
    autoPanAnimation: {
        duration: 250
    }
});

map.addOverlay(popupOverlay);

closer.onclick = function() {
    popupOverlay.setPosition(undefined);
    closer.blur();
    return false;
};
	
map.on('singleclick', function(evt) {
    var feature = map.forEachFeatureAtPixel(evt.pixel, function(feature) {
        return feature;
    });
	
	 if (feature) {
        var minPersonen = feature.get('Personen_min');
        var maxPersonen = feature.get('Personen_max');
        var personenText;

        if (minPersonen === maxPersonen) {
            personenText = minPersonen;
        } else {
            personenText = minPersonen + ' - ' + maxPersonen;
        };

        var contentString = '<div class="popupContent">';
        contentString += '<p class="popupTextTitle"><a href="' + feature.get('link') + '" target="_blank">' + feature.get('wh_name') + '</a></p>';
        contentString += '<p class="popupText"><b>Anzahl Wohnungen:</b> ' + feature.get('Anzahl') + '</p>';
        contentString += '<p class="popupText"><b>Wohnung/Zimmer für:</b> ' + personenText + ' Person(en)</p>';
        contentString += '<p class="popupText"><b>Wohnfläche:</b> ' + feature.get('Wohnfläche_min') + " - " + feature.get('Wohnfläche_max') + " m²" + '</p>';
        contentString += '<p class="popupText"><b>Mietpreis:</b> ' + feature.get('Mietpreis_min') + "€ - " + feature.get('Mietpreis_max') + "€" + '</p>';
        contentString += '<p class="popupText"><b>Wartezeit:</b> ' + feature.get('Verfügbarkeit') + '</p>';
        contentString += '<p class="popupText"><b>Internet:</b> ' + convertBoolean(feature.get('Internet')) + '</p>';
        contentString += '<p class="popupText"><b>Dusche:</b> ' + convertBoolean(feature.get('Dusche')) + '</p>';
        contentString += '<p class="popupText"><b>Küche:</b> ' + convertBoolean(feature.get('Küche')) + '</p>';
        contentString += '<p class="popupText"><b>Möbliert:</b> ' + convertBoolean(feature.get('möbliert')) + '</p>';
        contentString += '<p class="popupText"><b>Behindertengerecht:</b> ' + convertBoolean(feature.get('behindertengerecht')) + '</p>';
        contentString += '</div>';
        content.innerHTML = contentString;
        
        popupOverlay.setPosition(evt.coordinate);
    } else {
        popupOverlay.setPosition(undefined);
    }
});

function convertBoolean(value) {
  if (value === true) {
	  return "ja";
  } else { 
	  return "nein";
  }
};