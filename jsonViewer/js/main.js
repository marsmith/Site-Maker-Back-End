var map;

//main document ready function
$(document).ready(function () {

	//initialize basemap
	var worldGrayCanvas = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}', {
		attribution: 'Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ',
		maxZoom: 16
	});
	var worldBoundAndPlacesRef = L.tileLayer("https://services.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}", {
		attribution: 'Copyright: &copy; 2013 Esri, DeLorme, NAVTEQ'
	});

	//initialize map
	map = new L.Map('map', {
		center: new L.LatLng(42.75, -75.5),
		zoom: 7,
		layers: [worldGrayCanvas, worldBoundAndPlacesRef],
		attributionControl: false,
		zoomControl: false
	});

	function onEachFeature(feature, layer) {
		if (feature.geometry.type == "Point") {
			console.log(feature);
			//bind click
			layer.on('mouseover', function (e) {
				// e = event
				if (e.target.feature.properties.real_site) {
					$('#theInfo').html("Real site: True<br>Site No.: " + e.target.feature.properties.site_no);
				} else {
					$('#theInfo').html("Real site: False<br>Assigned ID: " + e.target.feature.properties.assigned_id + "<br>ID: " + e.target.feature.properties.id);
				}
				console.log(e.target.feature.properties);
				// You can make your ajax call declaration here
				//$.ajax(... 
			});
		}
	}

	var theCircleIcon = new L.icon({
		iconUrl: 'circle.PNG',
		iconSize:     [7, 7], // size of the icon  
	});

	var theTriangleIcon = new L.icon({
		iconUrl: 'triangle.PNG',
		iconSize:     [10, 10], // size of the icon  
	});

	// load GeoJSON from an external file
	$.getJSON("data.json",function(data){
		// add GeoJSON layer to the map once the file is loaded
		theJsonLayer = L.geoJson(data, {
			pointToLayer: function (feature, latlng) {
				console.log(feature);
				if (feature.properties.id) {
					return L.marker(latlng, {icon: theCircleIcon});
				} else {
					return L.marker(latlng, {icon: theTriangleIcon});
				}
			},
			onEachFeature: onEachFeature
		}).addTo(map);
		map.fitBounds(theJsonLayer.getBounds());
	});

	//end document ready function
});