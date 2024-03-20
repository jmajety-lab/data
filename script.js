function showConditionalInputs(value) {
    var segmentOptions = document.getElementById('segment-options');
    var intersectionOptions = document.getElementById('intersection-options');
    var rampOptions = document.getElementById('ramp-options');
    var crosscountyOp = document.getElementById('cross-county-options');
    // Hide all conditional inputs first
    segmentOptions.classList.add('hidden');
    intersectionOptions.classList.add('hidden');
    rampOptions.classList.add('hidden');
    crosscountyOp.classList.add('hidden');
    // Show the selected option's inputs
    if (value === 'segment') {
        segmentOptions.classList.remove('hidden');
    } else if (value === 'intersection') {
        intersectionOptions.classList.remove('hidden');
    }
    else if (value === 'ramp') {
        rampOptions.classList.remove('hidden');
    }
    else if (value === 'cross-county') {
        crosscountyOp.classList.remove('hidden');
    }
}
require([
    "esri/Map",
    "esri/views/MapView",
    "esri/layers/FeatureLayer",
    "esri/Graphic",
    "esri/geometry/Polyline",
    "esri/symbols/SimpleLineSymbol",
    "esri/tasks/support/Query",
    "esri/geometry/Circle",
    "esri/geometry/Point",
    "esri/symbols/SimpleFillSymbol",
  "esri/symbols/SimpleLineSymbol"
], function (Map, MapView, FeatureLayer, Graphic, Polyline, SimpleLineSymbol, Query, Circle, Point,     SimpleFillSymbol, SimpleLineSymbol) {

    var map = new Map({
        basemap: "streets-navigation-vector"
    });

    var view = new MapView({
        container: "viewDiv",
        map: map,
        zoom: 10,
        center: [-76.7, 39.1] // Centered over Maryland
    });

    var milePointsLayer = new FeatureLayer({
        url: "https://maps.roads.maryland.gov/arcgis/rest/services/Milepoints/Milepoints_Maryland_MDOTSHA/MapServer/1"
    });

    var lineSymbol = new SimpleLineSymbol({
        color: "black",
        width: "2px"
    });

    window.highlightRoute = function () {
        var check=0;
        var segmentCountyNumber = document.getElementById('segment-county-number').value;
        var segmentRouteNumber = document.getElementById('segment-route-number').value;
        var segmentPrefixNumber = document.getElementById('segment-prefix-number').value;
        var segmentSuffixNumber=document.getElementById('segment-suffix-number').value;
        var segmentMpFrom = document.getElementById('segment-mp-from').value;
        var segmentMpTo = document.getElementById('segment-mp-to').value;
       if(segmentSuffixNumber==''){
        check=1;
        var queryWhere = "COUNTY=" + segmentCountyNumber + " and ID_PREFIX='" + segmentPrefixNumber + "' and ID_RTE_NO = " + segmentRouteNumber + " and MP_DIRECTION='N' and id_mp >= " + segmentMpFrom + " and id_mp < " + segmentMpTo +" and MP_SUFFIX is null";
       }
       else{
        var queryWhere = "COUNTY=" + segmentCountyNumber + " and ID_PREFIX='" + segmentPrefixNumber + "' and ID_RTE_NO = " + segmentRouteNumber + " and MP_DIRECTION='N' and id_mp >= " + segmentMpFrom + " and id_mp < " + segmentMpTo + " and MP_SUFFIX='"+segmentSuffixNumber+"'" ;
       }
        console.log(queryWhere)
        var query = milePointsLayer.createQuery();
        query.where = queryWhere;
        query.outFields = "*";
        query.returnGeometry = true;

        milePointsLayer.queryFeatures(query).then(function (results) {
            view.graphics.removeAll();
            var features = results.features;


            var paths = [];
            var currentPath = [];
            var lastIdMp = null;
            
            features.forEach(function (feature, index) {
                if (lastIdMp !== null && feature.attributes.ID_MP < lastIdMp) {
                    // If the current id_mp is less than the last one, start a new path
                    if (currentPath.length > 0) {
                        paths.push(currentPath);
                    }
                    currentPath = [];
                }
                
                        currentPath.push([feature.attributes.LONGITUDE, feature.attributes.LATITUDE]);
                        lastIdMp = feature.attributes.ID_MP;
                    
               
                console.log(feature.attributes)
                currentPath.push([feature.attributes.LONGITUDE, feature.attributes.LATITUDE]);
                lastIdMp = feature.attributes.ID_MP;
                console.log(lastIdMp)
                
            });

            // Add the last path
            if (currentPath.length > 0) {
               
                paths.push(currentPath);
            }
            var allPolylines = [];
            
            paths.forEach(function (path) {
                var polyline = new Polyline({
                    paths: [path],
                    spatialReference: { wkid: 4326 }
                });

                var polylineGraphic = new Graphic({
                    geometry: polyline,
                    symbol: lineSymbol
                });

                view.graphics.add(polylineGraphic);
                allPolylines.push(polyline);
            });

            if (allPolylines.length > 0) {
                // Zoom to the extent of all polylines
                var totalExtent = allPolylines[0].extent.clone();
                allPolylines.forEach(function (polyline) {
                    totalExtent = totalExtent.union(polyline.extent);
                });

                view.goTo({
                    target: totalExtent,
                    zoom: 14     // Adjust zoom level as needed
                }).catch(function (error) {
                    if (error.name != "AbortError") {
                        console.error(error);
                    }
                });
            }
        }).catch(function (error) {
            console.error("Query failed: ", error);
        });
    };






    window.highlightRoute2 = function () {
        var check=0;
        var rampCounty = document.getElementById('ramp-county').value;
        var rampPrefix = document.getElementById('ramp-prefix').value;
        var rampRouteNumber = document.getElementById('ramp-route-number').value;
        var rampExitNumber=document.getElementById('ramp-exit-number').value;
        var rampNumber = document.getElementById('ramp-number').value;
       //COUNTY=16 and ID_PREFIX='RP' and ID_RTE_NO = 95 and AGOL_POPUP like '%11%' and RAMP_NUMBER = 1 and MP_DIRECTION = 'N'
       
        var queryWhere = "COUNTY=" + rampCounty + " and ID_PREFIX='" + rampPrefix + "' and ID_RTE_NO = " + rampRouteNumber + " and MP_DIRECTION='N' and AGOL_POPUP like '%"+rampExitNumber+"%' and RAMP_NUMBER="+ rampNumber;
       
        console.log(queryWhere)
        var query = milePointsLayer.createQuery();
        query.where = queryWhere;
        query.outFields = "*";
        query.returnGeometry = true;

        milePointsLayer.queryFeatures(query).then(function (results) {
            view.graphics.removeAll();
            var features = results.features;


            var paths = [];
            var currentPath = [];
            var lastIdMp = null;
            
            features.forEach(function (feature, index) {
                if (lastIdMp !== null && feature.attributes.ID_MP < lastIdMp) {
                    // If the current id_mp is less than the last one, start a new path
                    if (currentPath.length > 0) {
                        paths.push(currentPath);
                    }
                    currentPath = [];
                }
                if(check==1){
                    if(feature.attributes.MP_SUFFIX==null){
                        currentPath.push([feature.attributes.LONGITUDE, feature.attributes.LATITUDE]);
                        lastIdMp = feature.attributes.ID_MP;
                    }
                }
                else{
                console.log(feature.attributes)
                currentPath.push([feature.attributes.LONGITUDE, feature.attributes.LATITUDE]);
                lastIdMp = feature.attributes.ID_MP;
                console.log(lastIdMp)
                }
            });

            // Add the last path
            if (currentPath.length > 0) {
               
                paths.push(currentPath);
            }
            var allPolylines = [];
            
            paths.forEach(function (path) {
                var polyline = new Polyline({
                    paths: [path],
                    spatialReference: { wkid: 4326 }
                });

                var polylineGraphic = new Graphic({
                    geometry: polyline,
                    symbol: lineSymbol
                });

                view.graphics.add(polylineGraphic);
                allPolylines.push(polyline);
            });

            if (allPolylines.length > 0) {
                // Zoom to the extent of all polylines
                var totalExtent = allPolylines[0].extent.clone();
                allPolylines.forEach(function (polyline) {
                    totalExtent = totalExtent.union(polyline.extent);
                });

                view.goTo({
                    target: totalExtent,
                    zoom: 14     // Adjust zoom level as needed
                }).catch(function (error) {
                    if (error.name != "AbortError") {
                        console.error(error);
                    }
                });
            }
        }).catch(function (error) {
            console.error("Query failed: ", error);
        });
    };




    window.highlightRoute3 = function() {
        var intersecCounty = document.getElementById('intersection-county').value;
        var intersecPrefix = document.getElementById('intersection-prefix').value;
        var intersecRouteNumber = document.getElementById('intersection-route-number').value;
        var intersecSuffix = document.getElementById('intersection-suffix').value;
        var intersecMilePoint = document.getElementById('intersecting-milepoint').value;
    
        var queryWhere = intersecSuffix === '' ?
          "COUNTY=" + intersecCounty + " and ID_PREFIX='" + intersecPrefix + "' and ID_RTE_NO = " + intersecRouteNumber + " and MP_DIRECTION='N' and id_mp = " + intersecMilePoint + " and MP_SUFFIX is null" :
          "COUNTY=" + intersecCounty + " and ID_PREFIX='" + intersecPrefix + "' and ID_RTE_NO = " + intersecRouteNumber + " and MP_DIRECTION='N' and id_mp =" + intersecMilePoint + " and MP_SUFFIX='" + intersecSuffix + "'";
    
        console.log(queryWhere);
        var query = milePointsLayer.createQuery();
        query.where = queryWhere;
        query.outFields = "*";
        query.returnGeometry = true;
    
        milePointsLayer.queryFeatures(query).then(function(results) {
          view.graphics.removeAll();
          var features = results.features;
    
          if (features.length > 0) {
            var firstFeature = features[0];
            var point = new Point({
              longitude: firstFeature.attributes.LONGITUDE,
              latitude: firstFeature.attributes.LATITUDE
            });
    
            var circle = new Circle({
              center: point,
              radius: 100 // radius in meters, adjust as needed\width: 
             
            });
    
            var circleGraphic = new Graphic({
              geometry: circle,
              symbol: new SimpleLineSymbol({
                color: [227, 139, 79, 0.8],
                width: 4, // RGBA
                color: [0, 0, 0],
                outline: new SimpleLineSymbol({
                  color: [0, 0, 0],
                  width: 4
                })
              })
            });
    
            view.graphics.add(circleGraphic);
    
            view.goTo({
              target: circle.extent,
              zoom: 14 // Adjust zoom level as needed
            }).catch(function(error) {
              if (error.name != "AbortError") {
                console.error(error);
              }
            });
          }
        }).catch(function(error) {
          console.error("Query failed: ", error);
        });
      };
    
    
    
});


document.getElementById('saveProjectButton').addEventListener('click', function() {
    var formData = {}; // Object to hold form data

    // Collect all input data
    document.querySelectorAll('#inputForm input,#inputForm input[type="date"], #inputForm select').forEach(function(input) {
        formData[input.name] = input.value;
    });

    // Save the form data to localStorage
    localStorage.setItem('formData', JSON.stringify(formData));

    // Redirect to the crash collection page
    window.location.href = 'crashCollection.html';
});
document.getElementById('checkbox').addEventListener('click', function() {
    var formData = {}; // Object to hold form data

    // Collect all input data
    document.querySelectorAll('#inputForm input,#inputForm input[type="date"], #inputForm select').forEach(function(input) {
        formData[input.name] = input.value;
    });

    // Save the form data to localStorage
    localStorage.setItem('formData', JSON.stringify(formData));

    // Redirect to the crash collection page
    window.location.href = 'crashCollection.html';
});
