/**
 * Opens a jQuery UI dialog which display a scalebar image fetched from the 
 * server and adds a jQuery UI slider along with two input boxes.
 */
gisportal.window.createScalebar = function($trigger) {
   // Get the selected layer
   var layer;
   if (typeof $trigger === 'object')  {
      layer = gisportal.getLayerByID($trigger.attr('id'));
   }
   else  {
      layer = gisportal.getLayerByID($trigger);
   }   
   var scalebarDetails = getScalebarDetails(layer);

   // If there is an open version, close it
   if($('#scalebar-' + layer.id).length)
      $('#scalebar-' + layer.id).extendedDialog('close');
      
   var data = {
      name: layer.id,
      displayTitle: layer.displayTitle,
      url: scalebarDetails.url
   };

   // Add the html to the document using a template
   $(document.body).append(gisportal.templates.scalebarWindow(data));
   
   if(typeof layer.minScaleVal !== 'undefined' && typeof layer.maxScaleVal !== 'undefined') {
      $('#' + layer.id + '-max').val(layer.maxScaleVal);
      $('#' + layer.id + '-min').val(layer.minScaleVal);
   }
   else {
      $('#' + layer.id + '-max').val = '';
      $('#' + layer.id + '-min').val = '';  
   }

   // Show the scalebar for a selected layer
   $('#scalebar-' + layer.id).extendedDialog({
      position: ['right-10 bottom-50'],
      width: 310,
      resizable: false,
      autoOpen: false,
      showHelp: true,
      showMinimise: true,
      dblclick: "collapse",
      close: function() {
         // Remove on close
         $('#scalebar-' + layer.id).remove(); 
      },
      restore: function(e, dlg) {
         // Used to resize content on the dialog.
         $(this).trigger("resize");
      },
      help : function(e, dlg) {
         gisportal.gritter.showNotification('scalebarTutorial', null);
      }
   });
   
   // Event to change the scale to and from log if the checkbox is changed
   $('#' + layer.id + '-log').on('click', ':checkbox', function(e) {          
      // Check to see if the value was changed
      if(layer.log && $(this).is(':checked'))
         return;
      else if(layer.log === false && !$(this).is(':checked'))
         return;
         
      validateScale(layer, null , null);
   });
   
   // Event to reset the scale if the "Reset Scale" button is pressed
   $('#' + layer.id + '-reset').on('click', '[type="button"]', function(e) {                              
      validateScale(layer, layer.origMinScaleVal , layer.origMaxScaleVal, true);
   });
   
   // Event to automatically set the scale if the "Auto Scale" button is pressed
   $('#' + layer.id + '-auto').on('click', '[type="button"]', function(e) {
      var l = gisportal.layers[layer.id];     
   	gisportal.genericAsync('GET', OpenLayers.ProxyHost + encodeURIComponent(l.wmsURL + 'item=minmax&layers=' + l.id + '&bbox=-180,-90,180,90&elevation=' + (l.selectedElevation || -1) + '&time='+ new Date(l.selectedDateTime).toISOString() + '&crs=' + gisportal.lonlat.projCode + '&srs=' + gisportal.lonlat.projCode + '&width=50&height=50&request=GetMetadata') , null, function(d) {
   		validateScale(layer, d.min, d.max, true);
   	}, null, 'json', {});                          
      
   });
   
   // Event to recalculate the scale if the "Recalculate Scale" button is pressed
   $('#' + layer.id + '-scale').on('click', '[type="button"]', function(e) {                              
      var scaleRange = getScaleRange(layer.minScaleVal, layer.maxScaleVal);
      validateScale(layer, layer.minScaleVal , layer.maxScaleVal);
   });
   
   // Event for unclicking the max box
   $('#' + layer.id + '-max').focusout(function(e) {          
      // Check to see if the value was changed
      var max = parseFloat($(this).val());
      
      if(max == layer.maxScaleVal)
         return;
         
      validateScale(layer, null , max);
   });
   
   // Event for unclicking the min box
   $('#' + layer.id + '-min').focusout(function(e) {          
      // Check to see if the value was changed
      var min = parseFloat($(this).val());
      
      if(min == layer.minScaleVal)
         return;
         
      validateScale(layer, min , null);
   });
   
   // Open the dialog box
   $('#scalebar-' + layer.id).extendedDialog('open');
};

/**
 * Update the scale bar after changes have occurred.
 * 
 * @param {Object} layer - The layer who's scalebar needs to be updated.
 */
function updateScalebar(layer) {
   // Check we have something to update
   if($('#scalebar-' + layer.id).length)
   {
      var scalebarDetails = getScalebarDetails(layer);
      $('#scalebar-' + layer.id + '> img').attr('src', scalebarDetails.url);
   }
   
   var params = {
      colorscalerange: layer.minScaleVal + ',' + layer.maxScaleVal,
      logscale: layer.log
   };
   
   layer.mergeNewParams(params);
}

function getScalebarDetails(layer) {
   // Setup defaults
   var url = null;
   var width = 110;
   var height = 256;
   
   // Iter over styles
   $.each(layer.styles, function(index, value)
   {
      // If the style names match grab its info
      if(value.Name == layer.style && url === null) {
         url = value.LegendURL + createGetLegendURL(layer, true);
         width = parseInt(value.Width, 10);
         height = parseInt(value.Height, 10);
         return false; // Break loop
      }
   });
   
   // If the url is still null then there were no matches, so use a generic url
   if(url === null)
      url = createGetLegendURL(layer, false);
      
   return {
      url: url,
      width: width,
      height: height
   };
}

/**
 * Calculates a scale range based on the provided values.
 * @param {number} min - The lower end of the scale.
 * @param {number} max - The higher end of the scale.
 * @return {Object} Returns two values min and max in an object.
 */
function getScaleRange(min, max) {
   return {
      max: max + Math.abs((max / 100) * 25),
      min: min - Math.abs((max / 100) * 25)
   };
}

/**
 * Validates the entries for the scale bar
 * @param {Object} layer - The layer who's scalebar you wish to validate
 * @param {number} newMin - The new minimum value to be used for the scale
 * @param {number} newMax - The new maximum value to be used for the scale
 * @param {boolean} reset - Resets the scale if true
 */ 
function validateScale(layer, newMin, newMax, reset) {  
   if(newMin === null || typeof newMin === 'undefined')
      newMin = layer.minScaleVal;
      
   if(newMax === null || typeof newMax === 'undefined')
      newMax = layer.maxScaleVal;
      
   if(reset === null || typeof reset === 'undefined')
      reset = false;
   
   var min = parseFloat(newMin);
   var max = parseFloat(newMax);
   
   if (isNaN(min)) {
      console.log('Scale limits must be set to valid numbers -- reset to the old value');
      $('#' + layer.id + '-min').val(layer.minScaleVal);
   }
   else if (isNaN(max)) {
      console.log('Scale limits must be set to valid numbers -- reset to the old value');
      $('#' + layer.id + '-max').val(layer.maxScaleVal);
   }
   else if (min > max) {
      console.log('Minimum scale value must be less than the maximum -- reset to the old value');
      $('#' + layer.id + '-min').val(layer.minScaleVal);
      $('#' + layer.id + '-max').val(layer.maxScaleVal);
   } 
   else if (min <= 0 && $('#' + layer.id + '-log').children('[type="checkbox"]').first().is(':checked')) {
      console.log('Cannot use a logarithmic scale with negative or zero values -- reset to the old value');
      $('#' + layer.id + '-log').children('[type="checkbox"]').attr('checked', false);
   }
   else { 
      $('#' + layer.id + '-min').val(min);
      $('#' + layer.id + '-max').val(max);
      
      layer.minScaleVal = min;
      layer.maxScaleVal = max;     
      layer.log = $('#' + layer.id + '-log').children('[type="checkbox"]').first().is(':checked') ? true : false;
      
      updateScalebar(layer);
   }
}

function createGetLegendURL(layer, hasBase) {
   if(hasBase)
      return '&COLORSCALERANGE=' + layer.minScaleVal + ',' + layer.maxScaleVal + '&logscale=' + layer.log;
   else
      return layer.wmsURL + 'REQUEST=GetLegendGraphic&LAYER=' + layer.urlName + '&COLORSCALERANGE=' + layer.minScaleVal + ',' + layer.maxScaleVal + '&logscale=' + layer.log;
}
