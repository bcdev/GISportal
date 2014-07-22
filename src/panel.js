/**
 * Left Panel
 * @namespace
 */
gisportal.leftPanel = {};

gisportal.leftPanel.open = function() {
   $(".lPanel").show("fast");
   $(".triggerL").addClass("active");
};

gisportal.leftPanel.toggle = function() {
   $(".lPanel").toggle("fast");
   $(".triggerL").toggleClass("active");
};

gisportal.leftPanel.setup = function() {
   //$('#refLayers').multiOpenAccordion({
   //   active: 0
   //});

   // Makes each of the accordions sortable
   $('#gisportal-lPanel-operational').sortable({
      axis: 'y',
      distance: 10,
      handle: 'h3',
      update: function() {
         gisportal.leftPanel.updateGroupOrder($(this));
      }
   })
   .disableSelection();
   //.bind('sortstart', function(e, ui) {
   //   $(this).addClass('sort-start');
   //});

   // Makes each of the reference layers sortable
   $("#gisportal-lPanel-reference").sortable({
      axis: 'y',
      distance: 10,
      update: function() {
         gisportal.leftPanel.updateGroupOrder($(this));
         //var order = $("#gisportal-lPanel-reference").sortable('toArray');
         //$.each(order, function(index, value) {
            //var layer = gisportal.getLayerByID(value);
            //map.setLayerIndex(layer[0], map.numBaseLayers + order.length - index - 1);
         //});
      }
   });

   // Add dummy help layer
   //gisportal.leftPanel.addDummyHelpLayer();

   // Add first Group
   gisportal.leftPanel.addNextGroupToPanel($('#gisportal-lPanel-operational'));

   //Hook up the other events for the general UI
   // Left slide panel show-hide functionality
   $(".triggerL").click(function(e) {
		gisportal.leftPanel.toggle();
   });

   // Left slide panel buttons
   $('#triggerL-buttonset').buttonset();

   // Add group on click
   $('#triggerL-add-accordion')
      .button({ label: 'Add a new group', icons: { primary: 'ui-icon-circle-plus'}, text: false })
      .click(function(e) {
         var $panel = $('.lPanel .gisportal-tab-content:visible');
         gisportal.leftPanel.addNextGroupToPanel($panel);
      });
   //$('#triggerL-remove-accordion').button({ icons: { primary: 'ui-icon-circle-minus'}, text: false });

   $('#triggerL-add-group').button();

   $('.lPanel .gisportal-tab-group').buttonset();
   $('#gisportal-lpanel-tab-operational').button();
   $('#gisportal-lpanel-tab-reference').button();
   $('#gisportal-lpanel-tab-options').button();

   $('.lPanel .gisportal-tab-group input').click(function(e) {
      var tabToShow = $(this).attr('href');
      $('#gisportal-lPanel-content .gisportal-tab-content').filter(function(i) {
         return $(this).attr('id') != tabToShow.slice(1);
      }).hide('fast');
      $(tabToShow).show('fast');
   });

   // Populate the base layers drop down menu
   $.each(map.layers, function(index, value) {
       var layer = value;
       // Add map base layers to the baseLayer drop-down list from the map
       if(layer.isBaseLayer) {
           $('#baseLayer').append('<option value="' + layer.name + '">' + layer.name + '</option>');
       }
   });

   // Change of base layer event handler
   $('#baseLayer').change(function(e) {
       map.setBaseLayer(gisportal.baseLayers[$('#baseLayer').val()]);
   });

   // Create quick region buttons
   $('.lPanel .gisportal-quickRegion-reset').button({ label: 'Reset' }).click(function() {
      var id = $('.lPanel .gisportal-quickRegion-select').val();

      $('.lPanel .gisportal-quickRegion-name').val(gisportal.quickRegion[id][0]);
      $('.lPanel .gisportal-quickRegion-left').val(gisportal.quickRegion[id][1]);
      $('.lPanel .gisportal-quickRegion-bottom').val(gisportal.quickRegion[id][2]);
      $('.lPanel .gisportal-quickRegion-right').val(gisportal.quickRegion[id][3]);
      $('.lPanel .gisportal-quickRegion-top').val(gisportal.quickRegion[id][4]);
   });

   $('.lPanel .gisportal-quickRegion-save').button({ label: 'Save'}).click(function() {
      var select = $('.lPanel .gisportal-quickRegion-select'),
         id = select.val();

      gisportal.quickRegion[id][0] = $('.lPanel .gisportal-quickRegion-name').val();
      gisportal.quickRegion[id][1] = $('.lPanel .gisportal-quickRegion-left').val();
      gisportal.quickRegion[id][2] = $('.lPanel .gisportal-quickRegion-bottom').val();
      gisportal.quickRegion[id][3] = $('.lPanel .gisportal-quickRegion-right').val();
      gisportal.quickRegion[id][4] = $('.lPanel .gisportal-quickRegion-top').val();

      $(".gisportal-quickRegion-select").each(function() {
         $(this).find('option').eq(id).html(gisportal.quickRegion[id][0]);
      });
   });

   $('.lPanel .gisportal-quickRegion-add').button({ label: 'Add as new region' }).click(function() {
      gisportal.addQuickRegion($('.lPanel .gisportal-quickRegion-name').val(), {
         left: $('.lPanel .gisportal-quickRegion-left').val(),
         bottom: $('.lPanel .gisportal-quickRegion-bottom').val(),
         right: $('.lPanel .gisportal-quickRegion-right').val(),
         top: $('.lPanel .gisportal-quickRegion-top').val()
      });
   });

   $('.lPanel .gisportal-quickRegion-remove').button({ label: 'Remove selected region' }).click(function() {
      var select = $('.lPanel .gisportal-quickRegion-select'),
         id = select.val();

      gisportal.removeQuickRegion(id);
   });

   $('.lPanel .gisportal-quickRegion-addCurrent').button({ label: 'Add current view' }).click(gisportal.addCurrentView);
};

/**
 * Adds a group to the layers panel.
 *
 * @param {number} id - The id to use for the panel.
 * @param {string} displayName - The panel name to show.
 * @param {Object} $panelName - jQuery object representing the panel.
 */
gisportal.leftPanel.addGroupToPanel = function(id, displayName, $panelName) {
   // Add the accordion
   $panelName.prepend(
      '<div>' +
         '<h3><span class="ui-accordion-header-title">' + displayName + '</span></h3>' +
         '<div id="' + id + '" class="sensor-accordion"></div>' +
      '</div>'
   );

   // Creates the accordion
   $('#' + id).parent('div').multiOpenAccordion({
      active: 0,
      $panel: $panelName,
      showClose: function($panelName) {
         if($panelName.is("#gisportal-lPanel-reference") && $panelName.children().length <= 1)
            return false;
         else
            return true;
      },
      showDropdown: true,
      events: {
         close: function(id) {
            gisportal.leftPanel.removeGroupFromPanel(id);
         },
         dropdown: function($group) {
            $group.find('.ui-accordion-header-dropdown').first().contextMenu();
         }
      }
   });

   //if ($panelName.attr('id') == 'gisportal-lPanel-operational') {
      // Makes each of the operational layers sortable
      $('#' + id).sortable({
         connectWith: ".sensor-accordion",
         appendTo:".sensor-accordion",
         helper:"clone",
         update: function() {
            gisportal.leftPanel.updateLayerOrder($(this));
         }
      }).disableSelection();
   //}
};

/**
 * Remove a group from the layers panel.
 *
 * @param {string} id - The id of the panel to remove.
 */
gisportal.leftPanel.removeGroupFromPanel = function(id) {
   var $id = $('#' + id);
   if($id.length) {
      // Check if the accordion is empty
      $id.children('li').each(function() {
         var layer = gisportal.getLayerByID($(this).attr('id'));
         if(typeof layer !== 'undefined') {
            gisportal.removeLayer(layer);
            // Deselect layer on layer selector
            gisportal.layerSelector.toggleSelectionFromLayer(layer);
         }

      });

      // Remove the accordion we were asked to remove
      $id.parent('div').multiOpenAccordion('destroy');
      $id.parent('div').remove();
   }

   // Do a search for any others that need to be removed
   //$.each($('.sensor-accordion'), function(index, value) {
      //if($(this).children('li').length == 0)
         //$(this).parent('div').remove();
   //});
};

/**
 * Returns the first group from the panel. If there is no first group, it
 * creates one.
 *
 * @param {Object} $panelName - jQuery object representing the panel.
 *
 * @return {Object} Returns the first group.
 */
gisportal.leftPanel.getFirstGroupFromPanel = function($panelName) {
   var $firstGroup = $panelName.find('.sensor-accordion')
      .filter(function(i) {
         return !$(this).hasClass('gisportal-help');
      })
      .first();

   if($firstGroup.length > 0) {
      return $firstGroup;
   } else {
      gisportal.leftPanel.addNextGroupToPanel($panelName);
      return gisportal.leftPanel.getFirstGroupFromPanel($panelName);
   }
};

/**
 * Adds an empty group to the panel.
 *
 * @param {Object} $panelName - jQuery object representing the panel.
 */
gisportal.leftPanel.addNextGroupToPanel = function($panelName) {
   var number = ($panelName.find('.sensor-accordion')
      .filter(function(i) {
         return !$(this).hasClass('gisportal-help');
      })
      .length + 1);

   while($('#group' + number).length !== 0) {
      number++;
   }

   gisportal.leftPanel.addGroupToPanel('group' + number, 'Group ' + number, $panelName);
};

/**
 * Add a layer to a group on the layers panel.
 */
gisportal.leftPanel.addLayerToGroup = function(layer, $group) {
   // if not already on list, populate the layers panel (left slide panel)
   if(!$('#' + layer.id).length) {
      // jQuery selector for the layer controlID
      //var selID = layer.controlID == 'opLayers' ? '#' + layer.displaySensorName : '#' + layer.controlID;

      var data = {
         name: layer.id,
         visibility: layer.visibility,
         displayTitle: layer.displayTitle,
         type: layer.controlID
      };

      // Add the html to the document using a template
      $group.prepend(
         gisportal.templates.layer(data)
      );

      layer.$layer = $('#' + layer.id);
      gisportal.updateLayerData(layer.id);
      gisportal.rightPanel.updateCoverageList();
		$('#' + data.name + ' .gisportal-layer-dropdown').click(function(e)  { $(this).contextMenu({ x: e.clientX, y: e.clientY});  });
		// Remove the dummy layer
      //removeDummyHelpLayer()
   }
};

/**
 * Remove a layer from its group on the layers panel.
 */
gisportal.leftPanel.removeLayerFromGroup = function(layer) {
   if($('#' + layer.id).length)
      $('#' + layer.id).remove();
};

/**
 * Updates all the layer indexes in all the layer accordions.
 */
gisportal.leftPanel.updateGroupOrder = function($panel) {
   $.each($panel.find('.sensor-accordion'), function(index, value) {
      //if($(this).children('li').length == 0)
         //gisportal.leftPanel.removeGroupFromPanel($(this).attr('id'));
      //else
         gisportal.leftPanel.updateLayerOrder($(this));
   });
};

/**
 * Updates the position of layers based on their new
 * position on the stack.
 */
gisportal.leftPanel.updateLayerOrder = function(accordion) {
   var layersBelowOffset = 0;
   $.each(accordion.parent('div').nextAll('div').children('.sensor-accordion'), function(index, value) {
      //layersBelowOffset += $(this).children('li').length;
      $(this).children('li').each(function() {
         if($(this).hasClass('gisportal-layer')) {
            layersBelowOffset += gisportal.layers[$(this).attr('id')].order.length;
         }
      });
   });

   var layerGroupOrder = accordion.sortable('toArray');
   if(layerGroupOrder.length > 0) {
      $.each(layerGroupOrder, function(index, value) {
         var layer = gisportal.getLayerByID(value);
         if(typeof layer !== 'undefined') {
            var positionOffset = layer.controlID == 'opLayers' ? map.numBaseLayers : (map.numBaseLayers + map.numOpLayers);

            for(var i = 0, len = layer.order.length; i < len; i++) {
               map.setLayerIndex(layer.openlayers[layer.order[i]], positionOffset + layersBelowOffset + (layerGroupOrder.length - index - 1) + i);
            }
         }
      });
   }
   else
      ;//gisportal.leftPanel.removeGroupFromPanel(accordion.attr('id'));
};

/**
 * Adds a dummy layer to help the user.

gisportal.leftPanel.addDummyHelpLayer = function() {
   gisportal.leftPanel.addGroupToPanel("Need-Help", "Need Help?", $('#gisportal-lPanel-operational'));
*/
/* 
   $('#Need-Help')
      .addClass('gisportal-help')
      .prepend(
      '<li id="Help" class="notSelectable">' +
         'You Need to add some layers! Use the ' +
         '<a id="dmhLayerSelection" href="#">Layer Selection</a>' +
         ' panel.' +
      '</li>');

   // Open the layer panel on click
   $('#dmhLayerSelection').click(function(e) {
      if($('#gisportal-layerSelection').extendedDialog('isOpen')) {
         $('#gisportal-layerSelection').parent('div').fadeTo('slow', 0.3, function() { $(this).fadeTo('slow', 1); });
      }
      else {
         $('#layerPreloader').fadeTo('slow', 0.3, function() {
            $(this).fadeTo('slow', 1).fadeTo('slow', 0.3, function() {
               $(this).fadeTo('slow', 1);
            });
         });
      }

      return false;
   });
};
*/
/**
 * Saves the state of the left panel
 */
gisportal.leftPanel.saveState = function(state) {
   state.leftPanel = {};

   // Panel Open?
   if($('.triggerL').hasClass('active')) {
      state.leftPanel.isOpen = true;
   } else {
      state.leftPanel.isOpen = false;
   }

   // What tab is on display?
   // Foreach tab:
   //    What accordions exist and in what order?
   //    What layers are in each accordions and in what order?

   // What base layer is selected
   state.leftPanel.baseLayer = $('#baseLayer option:selected').val();


   return state;
};

/**
 * Loads the state given
 */
gisportal.leftPanel.loadState = function(state) {
   var map = state.map;
   var state = state.leftPanel;

   if(state.isOpen) {
      gisportal.leftPanel.open();
   }

   if (state.baseLayer)  {
      $('#baseLayer option[value="'+state.baseLayer+'"]').prop('selected', true);
      $('#baseLayer').change();
   }
};

/**
 * Right Panel
 * @namespace
 */
gisportal.rightPanel = {};

gisportal.current_area = 0;

gisportal.rightPanel.open = function() {
   $(".rPanel").show("fast");
   $(".triggerR").addClass("active");
	$('#advanced-inputs-header').click();
}

gisportal.rightPanel.toggle = function() {
	$('#advanced-inputs-header').click();
	$(".rPanel").toggle("fast");
   $(".triggerR").toggleClass("active");
}

// coverageStateSelected is a boolean that is set when a state has
// selected a coverage. This is so that the select box can be
// modified without always returning to the same state.
gisportal.rightPanel.coverageStateSelected = false;

gisportal.rightPanel.updateCoverageList = function()  {
	var selectedLayer = $('#graphcreator-coverage option:selected');
	$('#graphcreator-coverage option').remove();
	var keys = Object.keys(gisportal.layers);
	for (var i = 0; i < keys.length; i++)  {
		// TODO Nicer way of select, make sure to clean up
 		var layer = gisportal.layers[keys[i]];
		var tickedLayers = $('#gisportal-lPanel-operational input:checked');
		var selected = '';
      // Potentially change to using selectedLayers, I haven't done so since sometimes the array has more entries than it should
		if (layer === selectedLayer.value || (tickedLayers.length === 1 && layer === tickedLayers[0].value) || i === keys.length - 1) selected = 'selected';
		$('#graphcreator-coverage').prepend('<option ' + selected + ' value="' + keys[i] + '">' + (layer.displayTitle.length > 1 ? layer.displayTitle : keys[i]) + '</option>');
	}
	$('#graphcreator-coverage').prepend('<option value="" disabled="">Name of the Layer</option>');

   var state = gisportal.cache.state;
   if (state && state.rightPanel.selectedCoverage)  {
      $('#graphcreator-coverage option[value="' + state.rightPanel.selectedCoverage + '"]').prop("selected", true);
      gisportal.rightPanel.coverageStateSelected = true;
   }

   $('#graphcreator-coverage').change();
}

gisportal.rightPanel.setup = function() {

   // Right slide panel show-hide functionality
   $(".triggerR").click(function(e) {
      gisportal.rightPanel.toggle();
   });

   // Custom-made jQuery interface elements: multi-accordion sections (<h3>)
   // for data layers (in left panel) and data analysis (in right panel)
   $("#gisportal-rPanel-content").children('div').multiOpenAccordion({
      active: [0, 1]
   });

   // Regions of interest drawing control buttons - with custom styling
   $('#ROIButtonSet').buttonset();
   $('#point').button({ icons: { primary: 'ui-icon-drawpoint' }});
   $('#box').button({ icons: { primary: 'ui-icon-drawbox'} });
   $('#circle').button({ icons: { primary: 'ui-icon-drawcircle'} });
   $('#polygon').button({ icons: { primary: 'ui-icon-drawpoly'} });
   $('#shapefile_button').button({ icons: { primary: 'ui-icon-uploadshapefile'} });

    var updateShapenameDropdown = function () {
        var selectedValue = $('#shapename_chooser').val();
        var shapefile = $('#shapefile_chooser').val();
        gisportal.drawShape(shapefile, selectedValue);
    };

    var shapefileDropdownHandler = function () {
        var selectedValue = $('#shapefile_chooser').val();
        if (selectedValue == 'none') {
            var vectorLayer = map.getLayersBy('controlID', 'poiLayer')[0];
            vectorLayer.removeAllFeatures();
            $('#dispROI').html('No Selection');
        }
        gisportal.updateShapes();
        updateShapenameDropdown();
    };
   $('#shapefile_chooser').change(shapefileDropdownHandler);
   $('#shapename_chooser').change(updateShapenameDropdown);
   $('#shapefile_upload_button').change(gisportal.submit_shapefile_upload_form);
   $('#uploadshapefile').attr('action', gisportal.middlewarePath + '/shapefile_upload');

   $('input[name="roi_button_group"]').change(function() {
       if ($('input[name="roi_button_group"]:checked').val() === 'shapefile') {
           $('#shape_chooser').find('select').prop('disabled', false);
       } else {
           $('#shape_chooser').find('select').prop('disabled', 'disabled');
       }
       gisportal.updateShapefiles();
       gisportal.updateShapes();
       gisportal.geometryType = $('#ROIButtonSet').find('input[name=roi_button_group]:checked').val();
   });

   // Data Analysis panel tabs and accordions
   $("#gisportal-tab-analyses").multiOpenAccordion({ collapsible: true, heightStyle: 'content', active: [-1, -1, -1, -1] });
   $("#spatial").multiOpenAccordion({ collapsible: true, heightStyle: 'content', active: [-1, -1] });
   $("#temporal").multiOpenAccordion({ collapsible: true, heightStyle: 'content', active: [-1, -1] });

   $('.rPanel .gisportal-tab-group').buttonset();
   $('#gisportal-button-selection').button();
   $('#gisportal-button-analyses').button();
   $('#gisportal-button-export').button();

   $('.rPanel .gisportal-tab-group input').click(function(e) {
      var tabToShow = $(this).attr('href');
      $('#gisportal-rPanel-content .gisportal-tab-content').filter(function(i) {
         return $(this).attr('id') != tabToShow.slice(1);
      }).hide('fast');
      $(tabToShow).show('fast');
   });

   $('#gisportal-button-analyses').click(); // show analyses first
   $('#gisportal-tab-analyses > h3').click(); // show graphing first

   gisportal.rightPanel.setupDrawingControls();
   gisportal.rightPanel.setupGraphingTools();
   gisportal.rightPanel.setupDataExport();

};

gisportal.switchBackToPan = function() {
    $('label[for="pan"], #pan').click();
};
/**
 * Sets up the drawing controls to allow for the selection
 * of ROI's.
 */
gisportal.rightPanel.setupDrawingControls = function() {
   // Add the Vector drawing layer for POI drawing
   var vectorLayer = new OpenLayers.Layer.Vector('POI Layer', {
      style : {
         strokeColor : 'white',
         fillColor : 'green',
         strokeWidth : 2,
         fillOpacity : 0.3,
         pointRadius: 5
      },
      onFeatureInsert : function(feature) {
         ROIAdded(feature);
      },
      rendererOptions: { zIndexing: true }
   });

   vectorLayer.controlID = "poiLayer";
   vectorLayer.displayInLayerSwitcher=false;
   map.addLayer(vectorLayer);


   // Function called once a ROI has been drawn on the map
   function ROIAdded(feature) {
      gisportal.switchBackToPan();

      // Get the geometry of the drawn feature
      var geom = feature.geometry;

      // Special HTML character for the degree symbol
      var d = '&deg;';

      // Get bounds of the feature's geometry
      var bounds = new OpenLayers.Bounds();
      bounds = geom.getBounds();

      // Some metrics for the ROI
      var area_deg, area_km, height_deg, width_deg, height_km, width_km, radius_deg, ctrLat, ctrLon = 0;

      // Get some values for non-point ROIs
      if(map.ROI_Type !== '' && map.ROI_Type != 'point' && map.ROI_Type != 'shapefile') {
         $('#graphcreator-bbox').val(new OpenLayers.Format.WKT().extractGeometry(geom));
         area_deg = geom.getArea();
         area_km = (geom.getGeodesicArea()*1e-6);
         height_deg = bounds.getHeight();
         width_deg = bounds.getWidth();
         // Note - to get values in true ellipsoidal distances, we need to use Vincenty functions for measuring ellipsoidal
         // distances instead of planar distances (http://www.movable-type.co.uk/scripts/latlong-vincenty.html)
         ctrLon = geom.getCentroid().x;
         ctrLat = geom.getCentroid().y;
         height_km = OpenLayers.Util.distVincenty(new OpenLayers.LonLat(ctrLon,bounds.top),new OpenLayers.LonLat(ctrLon,bounds.bottom));
         width_km = OpenLayers.Util.distVincenty(new OpenLayers.LonLat(bounds.left,ctrLat),new OpenLayers.LonLat(bounds.right,ctrLat));
         radius_deg = ((bounds.getWidth() + bounds.getHeight())/4);
      }

      switch(map.ROI_Type) {
         case 'point':
            $('#dispROI').html('<h3>Point ROI</h3>');
            $('#dispROI').append('<img src="./img/pointROI.png" title ="Point Region Of Interest" alt="Map Point" />');
            $('#dispROI').append('<p>Lon, Lat: ' + geom.x.toPrecision(4) + d + ', ' + geom.y.toPrecision(4) + d + '</p>');
            break;
         case 'box':
            $('#dispROI').html('<h3>Rectangular ROI</h4>');
            // Setup the JavaScript canvas object and draw our ROI on it
            $('#dispROI').append('<canvas id="ROIC" width="100" height="100"></canvas>');
            var c = document.getElementById('ROIC');
            var ctx = c.getContext('2d');
            ctx.lineWidth = 4;
            ctx.fillStyle = '#CCCCCC';
            var scale = (width_deg > height_deg) ? 90/width_deg : 90/height_deg;
            ctx.fillRect(5,5,width_deg*scale,height_deg*scale);
            ctx.strokeRect(5,5,width_deg*scale,height_deg*scale);
            //
            $('#dispROI').append('<p>Width: ' + width_deg.toPrecision(4) + d + ' (' + width_km.toPrecision(4) + ' km)</p>');
            $('#dispROI').append('<p>Height: ' + height_deg.toPrecision(4) + d + ' (' + height_km.toPrecision(4) + ' km)</p>');
            $('#dispROI').append('<p>Projected Area: ' + area_km.toPrecision(4) + ' km<sup>2</sup></p>');
            break;
         case 'circle':
            $('#dispROI').html('<h3>Circular ROI</h4>');
            $('#dispROI').append('<img src="./img/circleROI.png" title ="Circular Region Of Interest" alt="Map Point" />');
            $('#dispROI').append('<p>Radius: ' + radius_deg.toPrecision(4) + d + '</p>');
            $('#dispROI').append('<p>Centre lat, lon: ' + ctrLat.toPrecision(4) + ', ' + ctrLon.toPrecision(4) + '</p>');
            $('#dispROI').append('<p>Width: ' + width_deg.toPrecision(4) + d + ' (' + width_km.toPrecision(4) + ' km)</p>');
            $('#dispROI').append('<p>Height: ' + height_deg.toPrecision(4) + d + ' (' + height_km.toPrecision(4) + ' km)</p>');
            $('#dispROI').append('<p>Projected Area: ' + area_km.toPrecision(4) + ' km<sup>2</sup></p>');
            break;
         case 'polygon':
            // Get the polygon vertices
            var vertices = geom.getVertices();
            $('#dispROI').html('<h3>Custom Polygon ROI</h4>');
            // Setup the JavaScript canvas object and draw our ROI on it
            $('#dispROI').append('<canvas id="ROIC" width="100" height="100"></canvas>');
            var c = document.getElementById('ROIC');
            var ctx = c.getContext('2d');
            ctx.lineWidth = 4;
            ctx.fillStyle = '#CCCCCC';
            var scale = (width_deg > height_deg) ? 90/width_deg : 90/height_deg;
            ctx.beginPath();
            var x0 = 5 + (vertices[0].x-bounds.left)*scale;
            var y0 = 5 + (bounds.top-vertices[0].y)*scale;
            ctx.moveTo(x0,y0);
            for(var i=1,j=vertices.length; i<j; i++){
               var x = 5 + (vertices[i].x-bounds.left) * scale;
               var y = 5 + (bounds.top-vertices[i].y) * scale;
               ctx.lineTo(x, y);
            }
            ctx.lineTo(x0,y0);
            ctx.stroke();
            ctx.fill();
            ctx.closePath();
            //
            $('#dispROI').append('<p>Centroid Lat, Lon:' + ctrLat.toPrecision(4) + d + ', ' + ctrLon.toPrecision(4) + d + '</p>');
            $('#dispROI').append('<p>Projected Area: ' + area_km.toPrecision(4) + ' km<sup>2</p>');
            break;
         case 'shapefile':
//             Handled in gisportal.js#fillROIDisplay()
            break;
      }
   }

   gisportal.mapControls.box = new OpenLayers.Control.DrawFeature(vectorLayer, OpenLayers.Handler.RegularPolygon, {handlerOptions:{sides: 4, irregular: true, persist: false }});
   gisportal.mapControls.circle = new OpenLayers.Control.DrawFeature(vectorLayer, OpenLayers.Handler.RegularPolygon, {handlerOptions:{sides: 50}, persist: false});
   gisportal.mapControls.polygon = new OpenLayers.Control.DrawFeature(vectorLayer, OpenLayers.Handler.Polygon);

   map.addControls([gisportal.mapControls.box, gisportal.mapControls.circle, gisportal.mapControls.polygon]);
   // Function which can toggle OpenLayers drawing controls based on the value of the clicked control
   function toggleDrawingControl(element, removePanControl) {
      if (removePanControl) {
          gisportal.toggleControl(element);
      }
      vectorLayer.removeAllFeatures();
      map.ROI_Type = element.value;
   }

   // Manually Handle drawing control radio buttons click event - each button has a class of "iconBtn"
   $('#ROIButtonSet').find('input:radio').click(function(e) {
      var removePanControl = true;
      if (this['id'].indexOf('shapefile') !== -1) {
          gisportal.switchBackToPan();
          removePanControl = false;
      }
      toggleDrawingControl(this, removePanControl);
   });

   // So that changing the input box changes the visual selection box on map
   $('#gisportal-graphing').on('change', '#graphcreator-bbox', function() {
//      var values = $('#graphcreator-bbox').val().split(',');
//      values[0] = gisportal.utils.clamp(values[0], -180, 180); // Long
//      values[2] = gisportal.utils.clamp(values[2], -180, 180); // Long
//      values[1] = gisportal.utils.clamp(values[1], -90, 90); // Lat
//      values[3] = gisportal.utils.clamp(values[3], -90, 90); // Lat
//      $('#graphcreator-bbox').val(values[0] + ',' + values[1] + ',' + values[2] + ',' + values[3]);
//      var feature = new OpenLayers.Feature.Vector(new OpenLayers.Bounds(values[0], values[1], values[2], values[3]).toGeometry());
//      feature.layer = map.layers[map.layers.length -1];
//      var features = map.layers[map.layers.length -1].features;
//      if (features[0]) map.layers[map.layers.length -1].features[0].destroy();
//      map.layers[map.layers.length -1].features[0] = feature;
//      map.layers[map.layers.length -1].redraw();
   });

   // TRAC Ticket #58: Fixes flaky non-selection of jQuery UI buttons (http://bugs.jqueryui.com/ticket/7665)
   $('#panZoom label.ui-button, #ROIButtonSet label.ui-button').unbind('mousedown').unbind('mouseup').unbind('mouseover').unbind('mouseout').unbind('click',
      function(e) { h.disabled && ( e.preventDefault(), e.stopImmediatePropagation() ); }
   ).bind('mousedown', function() {
      $(this).addClass('gisportal_click');
   }).bind('mouseup', function() {
      if ($(this).hasClass('gisportal_click')) {
         $(this).click();
      }
      $(this).removeClass('gisportal_click');
   });

};


gisportal.rightPanel.updateRanges = function(label)  {
   // Populate range from rangebars
   $('#graphcreator-range option').remove();
   $('#graphcreator-range').append('<option>Select a Range</option>');
   for(var i = 0; i < gisportal.timeline.rangebars.length; i++) {
      $('#graphcreator-range').append('<option value="' + gisportal.timeline.rangebars[i].name + '">' + gisportal.timeline.rangebars[i].label + '</option>');
   }
   if (label)  {
      var d = gisportal.timeline.rangebars.filter(function(element, index, array) { return element.label == label; });
      if (d.length > 0) $("#graphcreator-range option[value='" + (d[0].name || d.name) + "']").attr('selected', 'selected');
   }
};

gisportal.rightPanel.getDateRange = function()  {
   var dateRange = $('#graphcreator-time').val();
   if ($('#graphcreator-time2').val() !== "") {
      dateRange += ("/" + $('#graphcreator-time2').val());
   }
   return dateRange;
}

/**
* Sets up the graphing tools.
*/
gisportal.rightPanel.setupGraphingTools = function() {
//var graphCreator = $('#graphCreator');
// If there is an open version, close it
//if(graphCreator.length)
    //graphCreator.extendedDialog('close');

    var data = {
        advanced: true
    };

    // Add the html to the document using a template
    $('#gisportal-graphing').append(gisportal.templates.graphCreatorWindow(data));
    //$(document.body).append(gisportal.templates.graphCreatorWindow(data));

    var graphCreator = $('#graphCreator');
    var graphCreatorGenerate = graphCreator.find('#graphcreator-generate').first();

    /*
     // Turn it into a dialog box
     graphCreator.extendedDialog({
     position: ['center', 'center'],
     width:340,
     resizable: false,
     autoOpen: false,
     close: function() {
     // Remove on close
     $('#graphCreator').remove();
     },
     showHelp: true,
     showMinimise: true,
     dblclick: "collapse",
     help : function(e, dlg) {
     gisportal.gritter.showNotification ('graphCreatorTutorial', null);
     }
     }); */

    // Add the jQuery UI datepickers to the dialog
    $('#graphcreator-time').datepicker({
                                           showButtonPanel: true,
                                           dateFormat: 'yy-mm-dd',
                                           changeMonth: true,
                                           changeYear: true,
                                           yearRange: "1970:2020"
                                       });

    $('#graphcreator-time2').datepicker({
                                            showButtonPanel: true,
                                            dateFormat: 'yy-mm-dd',
                                            changeMonth: true,
                                            changeYear: true,
                                            yearRange: "1970:2020"
                                        });
    // Set the datepicker controls to the current view date if set
    var viewDate = $('#viewDate').datepicker('getDate');
    if (viewDate !== "") {
        $('#graphcreator-time').datepicker('setDate', viewDate);
        $('#graphcreator-time2').datepicker('setDate', viewDate);
    }

    $('#graphcreator-range').change(function () {
        var d = gisportal.timeline.rangebars.filter(function (element, index, array) {
            return element.name == $('#graphcreator-range option:selected').val();
        });
        if (d !== '' && d[0] !== undefined && d.selectedStart !== '' && d.selectedEnd !== '') {
            d = d[0]; // Take the first match
            $('#graphcreator-time').datepicker('setDate', d.selectedStart);
            $('#graphcreator-time2').datepicker('setDate', d.selectedEnd);
        }
        else {
            $('#graphcreator-time').datepicker('setDate', null);
            $('#graphcreator-time2').datepicker('setDate', null);
        }
    });

    $(gisportal).on('rangeUpdate.gisportal', function (e, d) {
        if ($('#graphcreator-range option:selected').val() == d.name) {
            $('#graphcreator-time').datepicker('setDate', d.selectedStart);
            $('#graphcreator-time2').datepicker('setDate', d.selectedEnd);
        }
    });

    $('.js-newRange').on('click', function () {
        //var name = prompt("Please give a label for this range bar.");
        if (!gisportal.timeline.rangeCounter) gisportal.timeline.rangeCounter = 1;
        var name = "Time Range " + gisportal.timeline.rangeCounter;
        gisportal.timeline.rangeCounter++;
        gisportal.timeline.addRangeBar(name);
        gisportal.rightPanel.updateRanges(name);
    });

    $('.js-hideRange').on('click', function () {
        var option = $('#graphcreator-range option:selected');
        if (option.data('hidden') == true) {
            gisportal.timeline.showRange(option.val());
            option.data('hidden', false);
            $('.js-hideRange').html("Hide Range");
        }
        else {
            gisportal.timeline.hideRange(option.val());
            option.data('hidden', true);
            $('.js-hideRange').html("Show Range");
        }
    });

    $('.js-deleteRange').on('click', function () {
        gisportal.timeline.removeTimeBarByName($('#graphcreator-range option:selected').val());
        $('#graphcreator-range option:selected').remove();
    });

    $('.js-renameRange').on('click', function () {
        var name = prompt("Please give a label for this range bar.");
        gisportal.timeline.rename($('#graphcreator-range option:selected').val(), name);
        gisportal.rightPanel.updateRanges(name);
    });

    $('#gisportal-graphing').on('change', '.hasDatepicker', function () {
        if ($('#graphcreator-range option:selected').val() !== 'Select a Range') {
            var selectedStart = $('#graphcreator-time').datepicker('getDate');
            var selectedEnd = $('#graphcreator-time2').datepicker('getDate');
            gisportal.timeline.rangebars.filter(function (element, index, array) {
                if (element.name == $('#graphcreator-range option:selected').val()) {
                    element.selectedStart = selectedStart;
                    element.selectedEnd = selectedEnd;
                }
            });
            gisportal.timeline.redraw();
        }
    });

    var layerID = $('.selectedLayer:visible').attr('id');

    // We need to check if a layer is selected
    if (typeof layerID !== 'undefined') {
        // Get the currently selected layer
        var layer = gisportal.getLayerByID(layerID);
        $('#graphcreator-baseurl').val(layer.wcsURL);
        $('#graphcreator-coverage option[val=' + layer.origName + ']').selected = true;
    }

    $('#graphcreator-coverage').on('change', function () {
        var layerID = $('option:selected', this).val();
        var layer = gisportal.getLayerByID(layerID);
        if (layer) {
            if (layer.wcsURL) {
                $('#graphcreator-baseurl').val(layer.wcsURL);

                if (layer.controlID === 'refLayers') {
                    $('#advanced-inputs-header').parent().hide();
                    $('.js-reference').show();

                    // TEMP CODE
                    $('#graphcreator-reference-variable option:selected').attr('value', 'TEMP-CPHLPS01').html('TEMP-CPHLPS01');
                }
                else {
                    $('#advanced-inputs-header').parent().show();
                    $('.js-reference').hide();
                }
                if (gisportal.selection.bbox)
                    $(gisportal.selection).trigger('selection_updated', {bbox: true});
            }
        }
    });

    // Check for changes to the selected layer
    $('.lPanel').on('change', '.selectedLayer', function (e) {
        var layerID = $('.selectedLayer:visible').attr('id');
        gisportal.updateLayerData(layerID);
    });

    graphCreatorGenerate.find('img[src="img/ajax-loader.gif"]').hide();

    // When selecting the bounding box text field, request user to draw the box to populate values
    $('#graphcreator-bbox').click(function () {
        gisportal.gritter.showNotification('bbox', null);
    });

    // Event to open and close the panels when clicked
    $('.ui-control-header').click(function () {
        $(this)
            .toggleClass("ui-control-header-active")
            .find("> .ui-icon").toggleClass("ui-icon-triangle-1-e ui-icon-triangle-1-s").end()
            .next().toggleClass("ui-control-content-active").slideToggle();
        return false;
    });

    graphCreator.unbind('.loadGraph').bind('ajaxStart.loadGraph', function () {
        $(this).find('img[src="img/ajax-loader.gif"]').show();
    }).bind('ajaxStop.loadGraph', function () {
        $(this).find('img[src="img/ajax-loader.gif"]').hide();
    });

    $('#graphcreator-barwidth-button').click(function () {
        return false;
    });

    $('#graphcreator-gallery').buttonset();
    $('#timeseries').button({ icons: { primary: 'gallery_timeseries'}, text: false });
    $('#hovmollerLat').button({ icons: { primary: 'gallery_hov_lat'}, text: false });
    $('#hovmollerLon').button({ icons: { primary: 'gallery_hov_long'}, text: false });
    $('#histogram').button({ icons: { primary: 'gallery_histogram'}, text: false });

    $('#graphcreator-gallery').change(function () {
        if (!$('#graphcreator-gallery input[value="histogram"]').prop("checked")) {
            $('#histogram-inputs').parent().hide();
        }
        else {
            $('#histogram-inputs').parent().show();
        }

        if (!$('#graphcreator-gallery input[value="hovmollerLat"]').prop("checked")
            && !$('#graphcreator-gallery input[value="hovmollerLon"]').prop("checked")) {
            $('#graph-settings').parent().hide();
        }
        else {
            $('#graph-settings').parent().show();
        }

    });

    $('#graphcreator-gallery').change(); // Initialise states

    // Close histogram, advanced and format panels
    $('#histogram-inputs-header').trigger('click');
    $('#advanced-inputs-header').trigger('click');
    $('#graph-format-header').trigger('click');

    var createAndDisplayGraph = function () {
        // Extract the date-time value from the datepickers either as single date-time or date-time range

        var dateRange = gisportal.rightPanel.getDateRange();
        var graphXAxis = null;
        var graphYAxis = null;

        const graphcreatorGalleryElement = $('#graphcreator-gallery');
        if (graphcreatorGalleryElement.find('input[value="hovmollerLon"]').prop("checked")) {
            graphXAxis = 'Lon';
            graphYAxis = 'Time';
        } else if (graphcreatorGalleryElement.find('input[value="hovmollerLat"]').prop("checked")) {
            graphXAxis = 'Time';
            graphYAxis = 'Lat';
        }

        // Some providers change direction of depth,
        // so this makes it match direction
        var depthDirection = function () {
            var layerID = $('#graphcreator-coverage').find('option:selected').val();
            var layer = gisportal.layers[layerID];
            var elevation = layer.selectedElevation;
            var direction = gisportal.microLayers[layerID].positive;

            // Take direction === up as default
            if (direction === "down") elevation = -elevation;
            return elevation;
        };

        const graphcreatorCoverageElement = $('#graphcreator-coverage');
        var graphParams = {
            baseurl: $('#graphcreator-baseurl').val(),
            coverage: gisportal.layers[graphcreatorCoverageElement.find('option:selected').val()].origName ||
                      graphcreatorCoverageElement.find('option:selected').val(),
            graphType: graphcreatorGalleryElement.find('input[name="gallery"]:checked').val(),
            bins: $('#graphcreator-bins').val(),
            time: dateRange,
            depth: depthDirection(),
            graphXAxis: graphXAxis,
            graphYAxis: graphYAxis,
            graphZAxis: gisportal.layers[graphcreatorCoverageElement.find('option:checked').val()].origName
        };

        if (graphParams.baseurl && graphParams.coverage) {
            var title = $('#graphcreator-title').html() || graphParams.type + " of " +
                                                           gisportal.layers[graphcreatorCoverageElement.find('option:checked').val()].displayTitle;
            var graphObject = {};
            graphObject.graphData = graphParams;
            //graphObject.description = prompt("Please enter a description");
            graphObject.description = title;
            graphObject.title = title;

            var success = function (data, opts) {
                console.log('POSTED graph!');
            };
            // Async post the state
            var error = function (request, errorType, exception) {
                console.log('Failed to retrieve stored graph from user');
            };

            var options = {};
            options.title = title;
            options.provider = gisportal.layers[graphcreatorCoverageElement.find('option:selected').val()].providerTag;
            options.labelCount = $('#graph-settings-labels').val();
            gisportal.graphs.data(graphParams, $('#graphcreator-bbox').val(), options);
        } else {
            gisportal.gritter.showNotification('dataNotSelected', null);
        }
    };

    // Create and display the graph
    graphCreatorGenerate.on('click', ':button', createAndDisplayGraph);
};

gisportal.rightPanel.setupDataExport = function() {

   var dataExport = $('#dataTools');
   var selectedLayer = $('.js-export-layer');
   var selectedBbox = $('.js-export-bbox');
   var selectedTime = $('.js-export-time');
   var dataDownloadURL = $('.js-export-url');

   var url = null;
   var urlParams = {
      service: 'WCS',
      version: '1.0.0',
      request: 'GetCoverage',
      crs: 'OGC:CRS84',
      format: 'NetCDF3'
   };

   var layerID = $('.selectedLayer:visible').attr('id');

   // We need to check if a layer is selected
   if(typeof layerID !== 'undefined') {
      // Get the currently selected layer
      var layer = gisportal.getLayerByID(layerID);
      selectedLayer.html('<b>Selected Layer: </b>' + layer.displayTitle);

      // Not using dot notation, so Closure doesn't change it.
      urlParams['coverage'] = layer.urlName;
      url = layer.wcsURL;
      updateURL();
   }

 	// Check for changes to the selected layer
   $('.lPanel').bind('selectedLayer', function(e) {
      var layer = gisportal.getLayerByID($('.selectedLayer:visible').attr('id'));
      selectedLayer.html('<b>Selected Layer: </b>' + layer.displayTitle);

      // Not using dot notation, so Closure doesn't change it.
      urlParams['coverage'] = layer.urlName;
      url = layer.wcsURL;
      updateURL();
   });

	// TODO: IMPROVE
   $(gisportal.selection).bind('selection_updated', function(event, params) {
      if(typeof params.bbox !== 'undefinded' && params.bbox) {
         var layer = gisportal.layers[$('#graphcreator-coverage').val()];
         var bbox = gisportal.selection.bbox.split(',');
         updateUrlTime();
         selectedLayer.html('<b>Selected Layer: </b>' + layer.displayTitle);
         selectedBbox.html('<b>Selected Bbox: </b>' + bbox[0] + ', ' + bbox[1] + ', ' + bbox[2] + ', ' + bbox[3]);
         urlParams['bbox'] = gisportal.selection.bbox;
         urlParams['coverage'] = layer.urlName;
         url = layer.wcsURL;
         updateURL();
      }

		$('#gisportal-graphing').on('change', '.hasDatepicker', updateUrlTime);
		$(gisportal).on('rangeUpdate.gisportal', updateUrlTime);

		function updateUrlTime() {
         var layer = gisportal.layers[$('#graphcreator-coverage').val()];
         gisportal.selection.time = urlParams['time'] = gisportal.rightPanel.getDateRange();
         if (gisportal.selection.time !== '')  {
            selectedTime.html('<b>Selected Time: </b>' + gisportal.selection.time);
            url = layer.wcsURL;
            updateURL();
         }
         else {
            selectedTime.html('');
         }
		}

	});

   function updateURL() {
      var request = $.param( urlParams );
      dataDownloadURL.attr('href', url + request);
   }

   dataDownloadURL.click(function() {
      // Check if there is data to download and catch spam clicks.
      if($(this).attr('href') == '#' && $(this).text() != 'No Data To Download') {
         dataDownloadURL.text('No Data To Download');
         setTimeout(function() {
            dataDownloadURL.text('Download Data');
         }, 1000);

         return false;
      }
      // If the text is hasn't changed then download the data.
      else if($(this).text() == 'Download Data') {
         // TODO: We could use this to keep track of what data the user has
         // downloaded. They might need to see what they have or have not
         // downloaded.
      }
      // Top check will fail if the user spam clicks, but we still need to 'return false'.
      else {
         return false;
      }
   });
};

/**
 * Saves the state of the right panel
 */
gisportal.rightPanel.saveState = function(state) {
   state.rightPanel = {};

   // Panel Open?
   if($('.triggerR').hasClass('active')) {
      state.rightPanel.isOpen = true;
   } else {
      state.rightPanel.isOpen = false;
   }

   state.rightPanel.selectedCoverage = $('#graphcreator-coverage option:selected').val();
   state.rightPanel.selectedRange = $('#graphcreator-range option:selected').val();

   state.rightPanel.gallery = $('#graphcreator-gallery input:checked').val();

   state.rightPanel.fromDate = $('#graphcreator-time').datepicker("getDate");
   state.rightPanel.toDate = $('#graphcreator-time2').datepicker("getDate");

   state.rightPanel.bbox = $('#graphcreator-bbox').val();

   return state;
};

/**
 * Loads the state given
 */
gisportal.rightPanel.loadState = function(state) {
   var map = state.map;
   var state = state.rightPanel;

   if(state.isOpen) {
      gisportal.rightPanel.open();
   }

   if(state.gallery)  {
      $('#graphcreator-gallery input[value="' + state.gallery + '"]').prop("checked", true);
      $('#' + state.gallery).button("refresh");
   }

   if (state.fromDate)$('#graphcreator-time').datepicker("setDate",  new Date(state.fromDate));

   if (state.toDate) $('#graphcreator-time2').datepicker("setDate", new Date(state.toDate));

   if (state.bbox) $('#graphcreator-bbox').val(state.bbox);

   if (state.selectedRange) $('#graphcreator-range option[value="' + state.selectedRange + '"]').prop("selected", true);

};


/**
 * Top bar
 * @namespace
 */
gisportal.topbar = {};

gisportal.topbar.setup = function() {

   // Add jQuery UI datepicker
   $('#viewDate').datepicker({
      showButtonPanel: true,
      dateFormat: 'dd-mm-yy',
      changeMonth: true,
      changeYear: true,
      beforeShowDay: function(date) { return gisportal.allowedDays(date); },
      onSelect: function(dateText, inst) {
         var thedate = new Date(inst.selectedYear, inst.selectedMonth, inst.selectedDay);
         // Synchronise date with the timeline
         gisportal.timeline.setDate(thedate);
         // Filter the layer data to the selected date
         //gisportal.filterLayersByDate(thedate);
      },
      yearRange: "1970:2020"
   });

   //--------------------------------------------------------------------------

   // Pan and zoom control buttons
   $('#panZoom').buttonset();
   $('#pan').button({ icons: { primary: 'ui-icon-arrow-4-diag'} });
   $('#zoomIn').button({ icons: { primary: 'ui-icon-circle-plus'} });
   $('#zoomOut').button({ icons: { primary: 'ui-icon-circle-minus'} });

   // Function which can toggle OpenLayers controls based on the clicked control
   // The value of the value of the underlying radio button is used to match
   // against the key value in the mapControls array so the right control is toggled
   gisportal.toggleControl = function(element) {
      for(var key in gisportal.mapControls) {
         var control = gisportal.mapControls[key];
         if($(element).val() == key) {
            $('#'+key).attr('checked', true);
            control.activate();

            if(key == 'pan') {
               gisportal.mapControls.selector.activate();
            }
         }
         else {
            if(key != 'selector') {
               if(key == 'pan') {
                  gisportal.mapControls.selector.deactivate();
               }

               $('#' + key).attr('checked', false);
               control.deactivate();
            }
         }
      }
      $('#panZoom input:radio').button('refresh');
   };

   // Making sure the correct controls are active
   gisportal.toggleControl($('#panZoom input:radio'));

   // Manually Handle jQuery UI icon button click event - each button has a class of "iconBtn"
   $('#panZoom input:radio').click(function(e) {
      gisportal.toggleControl(this);
   });

   //--------------------------------------------------------------------------

   // Create buttons
   $('#gisportal-toolbar-actions').buttonset();
   $('#mapInfoToggleBtn').button({ label: '', disabled: 'true', icons: { primary: 'ui-icon-gisportal-globe-info'} });
   $('#shareMapToggleBtn').button({ label: '', icons: { primary: 'ui-icon-gisportal-globe-link'} });
   $('#layerPreloader').button({ label: '', icons: { primary: 'ui-icon-gisportal-layers'} })
   $('#gisportal-button-3d').button({ label: '', icons: { primary: 'ui-icon-gisportal-globe'}, disabled: 'true' })
      .click(function(e) {
         if(map.globe.is3D) {
            map.show2D();
         }
         else {
            map.show3D();
            gisportal.gritter.showNotification('3DTutorial', null);
         }
      });
   $('#infoToggleBtn').button({ label: '', icons: { primary: 'ui-icon-gisportal-info'} });
   $('#userInfoToggleBtn').button({ label: '', icons: { primary: 'ui-icon-gisportal-user-info'} });

   // Add toggle functionality for dialogs
   $('#shareMapToggleBtn').click(function() {
      $('#shareOptions').toggle();
   });
   addDialogClickHandler('mapInfoToggleBtn', $('#gisportal-historyWindow'));
   addDialogClickHandler('layerPreloader', $('#gisportal-layerSelection'));
   addDialogClickHandler('infoToggleBtn', $('#walkthrough-menu'));
   addDialogClickHandler('userInfoToggleBtn', $('#user-info-balloon'));

     function addDialogClickHandler(idOne, idTwo) {
      $("label[for=" + idOne + "]").click(function(e) {
         if ($(idTwo).extendedDialog("isOpen")) {
             $(idTwo).extendedDialog("close");
         } else {
             $(idTwo).extendedDialog("open");
         }
      });
   }

   $('#topToolbar .togglePanel')
      .button({ label:'Toggle Panel', icons: { primary: 'ui-icon-triangle-1-n'}, 'text': false})
      .click(function() {
         if ($(this).parent().css('top') != "0px") {
            $(this).parent().animate({top:'0px'});
            console.log(this);
            $(this).button( "option", "icons", { primary: 'ui-icon-triangle-1-n'} );
         }
         else {
            $(this).parent().animate({top:'-50px'});
            $(this).button( "option", "icons", { primary: 'ui-icon-triangle-1-s'} );
         }
      });
};
