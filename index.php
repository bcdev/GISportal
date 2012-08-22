<!DOCTYPE HTML>
<html>
<!-- http://spyrestudios.com/demos/sliding-panel-left/ -->
<head>
<meta charset="utf-8">
<title>OpEc GIS Portal (jQuery + jQuery UI)</title>
<!-- Now for the styling -->
<!-- jQuery UI theming CSS -->
<link rel="stylesheet" type="text/css" href="js-libs/jquery-ui/css/black-tie/jquery-ui-1.8.23.custom.css" />
<!-- Default OpenLayers styling -->
<link rel="stylesheet" type="text/css" href="js-libs/OpenLayers/theme/default/style.css" />
<!-- Context Menu styling -->
<Link rel="stylesheet" type="text/css" href="js-libs/jquery-contextMenu/css/jquery-contextMenu.css" />
<!-- Gritter styling -->
<Link rel="stylesheet" type="text/css" href="js-libs/jquery-gritter/css/jquery.gritter.css" />
<!-- Multiselect styling -->
<Link rel="stylesheet" type="text/css" href="js-libs/jquery-multiselect/css/jquery.multiselect.css" />
<!--<link rel="stylesheet" type="text/css" href="js-libs/OpenLayers/theme/default/google.css">-->
<!-- Default styling for web app plus overrides of OpenLayers and jQuery UI styles -->
<link rel="stylesheet" type="text/css" href="css/main.css" />
<!-- JavaScript libraries -->
<!-- Custom functions and extensions to exisiting JavaScript objects -->
<script type="text/javascript" src="custom.js"></script>
<!-- Latest jQuery from jQuery.com -->
<script type="text/javascript" src="js-libs/jquery/jquery-1.7.2.min.js"></script>
<!-- The latest jQuery UI from jqueryui.com -->
<script type="text/javascript" src="js-libs/OpenLayers/OpenLayers.js"></script>
<!--<script src="http://maps.google.com/maps/api/js?v=3.6&amp;sensor=false"></script>-->
<script type="text/javascript" src="js-libs/jquery-ui/js/jquery-ui-1.8.23.custom.min.js"></script>
<!-- http://forum.jquery.com/topic/expand-all-zones-for-an-accordion#14737000002919405 -->
<!-- <script type="text/javascript" src="js-libs/multiAccordion.js"></script> -->
<!-- http://code.google.com/p/jquery-multi-open-accordion -->
<script type="text/javascript" src="js-libs/jquery.multi-open-accordion-1.5.2.js"></script>
<!-- Custom library of extensions and functions for OpenLayers Map and Layer objects -->
<script type="text/javascript" src="maplayers.js"></script>
<!-- http://medialize.github.com/jQuery-contextMenu/ -->
<script type="text/javascript" src="js-libs/jquery-contextMenu/js/jquery-contextMenu.js"></script>
<!-- https://github.com/jboesch/Gritter -->
<script type="text/javascript" src="js-libs/jquery-gritter/js/jquery.gritter.min.js"></script>
<!-- https://github.com/michael/multiselect -->
<script type="text/javascript" src="js-libs/jquery-multiselect/js/jquery.multiselect.js"></script>
<!-- Custom JavaScript -->
<!-- OpenLayers Map Code-->
<script type="text/javascript" src="opecportal.js"></script>
<script type="text/javascript" src="gritter.js"></script>
<script type="text/javascript" src="contextMenu.js"></script>

<!-- Use custom PHP class to create cache the getCapabilities call and create some
   date caches for the required data layers.
   See wms-capabilities.php for details. -->

<?php
//--------PHP-DEBUG-SETTINGS--------
   // Log file location
   //define("LOG_FILE", "/errors.log");

   ini_set('error_reporting', E_ALL);
   ini_set('display_errors', '1');
   //ini_set("log_errors", "1");
   //ini_set('error_log', LOG_FILE)

   // Setup firebug php  
   require_once('FirePHPCore/fb.php');
   ob_start();
//----------------------------------

   require('wms-capabilities.php');

   // Generate cache files
   updateCache();
?>

</head>
<body>
   <!-- CSS check and info for screen readers -->
   <div id="nocss-info">
      <h1>Opec Visualisation</h1>
      <span>Operational Ecology Marine Ecosystem Forecasting</span>
      <div class="css-check">
         This website requires css to work. Please enable it in your browser.
      </div>
   </div>
   <!-- JavaScript check -->
   <noscript>
      <div id="noscript-warning">
         This website requires JavaScript to work. Please enable it in your browser.
      </div>
   </noscript>

   <!-- The Map -->
   <div id="map"></div>
   <!-- The Top Toolbar -->
   <div id="topToolbar" class="toolbar">
      <ul>
         <li id="panZoom">
            <input type="radio" id="pan" name="radio" value="pan" checked="checked" />
               <label class="iconBtn" for="pan" title="Pan the Map: Keep the mouse button pressed and drag the map around."></label>
            <input type="radio" id="zoomIn" name="radio" value="zoomIn"/>
               <label class="iconBtn" for="zoomIn" title="Zoom In: Click in the map to zoom in or drag a rectangle to zoom into that selection."></label>
            <input type="radio" id="zoomOut" name="radio" value="zoomOut" />
               <label class="iconBtn" for="zoomOut" title="Zoom Out: Click in the map to zoom out or drag a rectangle to zoom the map out into that selection."></label>
         </li>
         <li class="divider"></li>
         <li>
            <fieldset>
               <legend>View Date</legend>
               <input size="10" type="text" name="viewDate" id="viewDate" />
            </fieldset>
         </li>
         <li class="divider"></li>
         <!-- Placeholder ROI radio buttons -->
         <li id="ROIButtonSet">
            <input type="radio" id="point" name="radio" value="point" />
               <label class="iconBtn" for="point" title="Draw Point: Click in the map to draw a point as a region of interest centred on the click point."></label>
            <input type="radio" id="box" name="radio" value="box"/>
               <label class="iconBtn" for="box" title="Draw Box: Click and drag on the map to draw a rectangle as a region of interest with the click point at its top-left."></label>
            <input type="radio" id="circle" name="radio" value="circle" />
               <label class="iconBtn" for="circle" title="Draw Circle: Click and drag on the map to draw a circle as a region of interest with the click point at its centre."></label>
            <input type="radio" id="polygon" name="radio" value="polygon" />
               <label class="iconBtn" for="polygon" title="Draw Polygon: Click repeatedly on the map to draw a polygon as a region of interest. Double-click to finish drawing the polygon"></label>
         </li>
         <li class="divider"></li>
         <li>
            <a href="#" id="mapInfoToggleBtn"><img src="img/info32.png" alt="Toggle Map Information Window"></a>        
         </li>
         <li>
            <a href="#" id="shareMapToggleBtn"><img src="img/mapLink.png" alt="Toggle Share Map Window"></a>
         </li>
      </ul>
   </div>
   <!-- The Left Panels -->
   <a class="trigger triggerL" href="#">Layers</a>
   <div class="panel lPanel">
      <h3 id="layerLbl">Data Layers</h3>
      <div id="layerAccordion">
         <h3><a href="#">Operational Layers</a></h3>
         <div id="opLayers"></div>
         <h3><a href="#">Reference Layers</a></h3>
         <div id="refLayers"></div> 
      </div>
      <div style="clear: both;"> </div>
   </div>
   <!-- The Right Panels -->
   <a class="trigger triggerR" href="#">Data</a>
   <div class="panel rPanel">
      <h3 id="dataLbl">Data Analysis</h3>
      <div id="dataAccordion">
         <h3><a href="#">Current R.O.I.</a></h3>
         <div id="dispROI"></div>
         <h3><a href="#">Data Tools</a></h3>
         <div id="dataTools">
            <div id="dataTabs">
               <ul>
                  <li><a href="#tabs-1">Analyses</a></li>
                  <li><a href="#tabs-2">Export<br></a></li>
               </ul>
               <div id="tabs-1">
                  <div id="analyses">
                     <h3><a href="#">Basic Statistics</a></h3>
                        <table id="bStats">
                           <tr>
                              <td>Mean Value:</td>
                              <td>Two</td>
                           </tr>
                           <tr>
                              <td>Max Value:</td>
                              <td>Two</td>
                           </tr>
                           <tr>
                              <td>Min Value:</td>
                              <td>Two</td>
                           </tr>
                           <tr>
                              <td>Std.Dev.:</td>
                              <td>Two</td>
                           </tr>
                        </table>
                     <h3><a href="#">Spatial Analysis</a></h3>
                     <div id="spatial">
                        <h3><a href="#">Thresholding</a></h3>
                        <div id="threshold"></div>
                        <h3><a href="#">Data Correlation</a></h3>
                        <div id="dCorr"></div> 
                     </div> 
                     <h3><a href="#">Temporal Analysis</a></h3>
                     <div id="temporal">
                        <h3><a href="#">Time Series</a></h3>
                        <div id="tSeries"></div>
                        <h3><a href="#">Interannual Variability</a></h3>
                        <div id="IAVar"></div>
                     </div> 
                     <h3><a href="#">Risk Analysis</a></h3>
                     <div id="risk"></div> 
                  </div>
               </div>
               <div id="tabs-2">
                  <p>Mauris eleifend est et turpis. Duis id erat. Suspendisse potenti. Aliquam vulputate, pede vel vehicula accumsan, mi neque rutrum erat, eu congue orci lorem eget lorem. Vestibulum non ante. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Fusce sodales. Quisque eu urna vel enim commodo pellentesque. Praesent eu risus hendrerit ligula tempus pretium. Curabitur lorem enim, pretium nec, feugiat nec, luctus a, lacus.</p>
               </div>
            </div>      
         </div>
      </div>
      <div style="clear: both;"> </div>
   </div>
   <div id="bottomToolbar" class="toolbar">
      <ul>
         <li>
            <fieldset>
               <legend>Base Layer</legend>
               <select id="baseLayer" name="Base Layer">
               </select>
            </fieldset>
         </li>
         <li class="divider"></li>
         <li>
            <fieldset>
               <legend>Quick Region</legend>
               <select id="quickRegion" name="Quick Region">
               </select>
            </fieldset>
         </li>
         <li class="divider"></li>
         <li>
            <a href="#" id="mapOptionsBtn"><img src="img/map-icon.png" alt="Click for Map Options"></a>
         </li>
         <li class="divider"></li>
         <li>
            <a href="#" id="infoToggleBtn"><img src="img/info32.png" alt="Toggle Information Window"></a>
         </li>   
      </ul>
   </div>
   <div class="toolbar" id="mapOptions">
   	<h2>Some header text</h2>
      <p>Some stuff can go here in the future...</p>
   </div>
   <div class="toolbar" id="shareOptions">
   	<h3>Share</h3>
      <div>
         <input type="text" name="shareLink" value="link" id="shareLink" />
         <label class="iconBtn" for="shareLink" />
      </div> 
   </div>
   <div id="info" title="Information">
      <a href="http://www.marineopec.eu" target="_new" name="OpEc Main Web Site" rel="external"> <img src="img/OpEc_small.png" alt="OpEc (Operational Ecology) Logo" /></a>
      <a href="http://cordis.europa.eu/fp7/home_en.html" target="_new" name="European Union Seventh Framework Programme" rel="external"> <img src="img/fp7_small.png" alt="European Union FP7 Logo" /></a>
      <p>&copy;2012 PML Applications Ltd<br />
      EU Project supported within DG SPACE for the 7th Framework Programme for Cooperation.</p>
      <div style="clear: both;"> </div>
   </div>
   <div id="mapInfo" title="MapInfo">
      <div>
         <span id="latlng"></span>
      </div>
   </div>
   <div id="layerSelection" class="layer-selection" title="Layer Selection">
      <span>Please select which layers you would like to use with the map. You can change these layers at any time.</span>
      <div id="layers">
         <select name="countries[]" multiple="multiple" class="multiselect" id="countries" style="display: none;">
            <option selected="selected" value="AUT">Austria</option>
            <option selected="selected" value="DEU">Germany</option>
            <option selected="selected" value="NLD">Netherlands</option>
            <option selected="selected" value="USA">United States</option>
            <option value="AFG">Afghanistan</option>
            <option value="ALB">Albania</option>
            <option value="DZA">Algeria</option>

            <option value="AND">Andorra</option>
            <option value="ARG">Argentina</option>
            <option value="ARM">Armenia</option>
            <option value="ABW">Aruba</option>
            <option value="AUS">Australia</option>


            <option value="AZE">Azerbaijan</option>
            <option value="BGD">Bangladesh</option>
            <option value="BLR">Belarus</option>
            <option value="BEL">Belgium</option>
            <option value="BIH">Bosnia and Herzegovina</option>
            <option value="BRA">Brazil</option>
            <option value="BRN">Brunei</option>
            <option value="BGR">Bulgaria</option>
            <option value="CAN">Canada</option>

            <option value="CHN">China</option>
            <option value="COL">Colombia</option>
            <option value="HRV">Croatia</option>
            <option value="CYP">Cyprus</option>
            <option value="CZE">Czech Republic</option>
            <option value="DNK">Denmark</option>
            <option value="EGY">Egypt</option>
            <option value="EST">Estonia</option>
            <option value="FIN">Finland</option>

            <option value="FRA">France</option>
            <option value="GEO">Georgia</option>

            <option value="GRC">Greece</option>
            <option value="HKG">Hong Kong</option>
            <option value="HUN">Hungary</option>
            <option value="ISL">Iceland</option>
            <option value="IND">India</option>
            <option value="IDN">Indonesia</option>

            <option value="IRN">Iran</option>
            <option value="IRL">Ireland</option>
            <option value="ISR">Israel</option>
            <option value="ITA">Italy</option>
            <option value="JPN">Japan</option>
            <option value="JOR">Jordan</option>
            <option value="KAZ">Kazakhstan</option>
            <option value="KWT">Kuwait</option>
            <option value="KGZ">Kyrgyzstan</option>

            <option value="LVA">Latvia</option>
            <option value="LBN">Lebanon</option>
            <option value="LIE">Liechtenstein</option>
            <option value="LTU">Lithuania</option>
            <option value="LUX">Luxembourg</option>
            <option value="MAC">Macau</option>
            <option value="MKD">Macedonia</option>
            <option value="MYS">Malaysia</option>
            <option value="MLT">Malta</option>

            <option value="MEX">Mexico</option>
            <option value="MDA">Moldova</option>
            <option value="MNG">Mongolia</option>

            <option value="NZL">New Zealand</option>
            <option value="NGA">Nigeria</option>
            <option value="NOR">Norway</option>
            <option value="PER">Peru</option>
            <option value="PHL">Philippines</option>

            <option value="POL">Poland</option>
            <option value="PRT">Portugal</option>
            <option value="QAT">Qatar</option>
            <option value="ROU">Romania</option>
            <option value="RUS">Russia</option>
            <option value="SMR">San Marino</option>
            <option value="SAU">Saudi Arabia</option>
            <option value="CSG">Serbia and Montenegro</option>
            <option value="SGP">Singapore</option>

            <option value="SVK">Slovakia</option>
            <option value="SVN">Slovenia</option>
            <option value="ZAF">South Africa</option>
            <option value="KOR">South Korea</option>
            <option value="ESP">Spain</option>
            <option value="LKA">Sri Lanka</option>
            <option value="SWE">Sweden</option>
            <option value="CHE">Switzerland</option>
            <option value="SYR">Syria</option>

            <option value="TWN">Taiwan</option>
            <option value="TJK">Tajikistan</option>
            <option value="THA">Thailand</option>
            <option value="TUR">Turkey</option>
            <option value="TKM">Turkmenistan</option>
            <option value="UKR">Ukraine</option>
            <option value="ARE">United Arab Emirates</option>
            <option value="GBR">United Kingdom</option>


            <option value="UZB">Uzbekistan</option>
            <option value="VAT">Vatican City</option>
            <option value="VNM">Vietnam</option>
            </select>
         </div>
      
      <!--<div class="ui-widget-content">
         <ul id="selectedLayers" class="layer-list">
         </ul>
      </div>
      <div class="ui-widget-content">         
         <ul id="availableLayers" class="layer-list">
         </ul>
      </div>
      <div>
         <button id="addAccordion" alt="Add Accordion">Add Accordion</button>
         <button id="removeAccordion" alt="Remove Accordion">Remove Accordion</button>
         <button id="addLayer" alt="Add Layer">Add Layer</button>
         <button id="removeLayer" alt="Remove Layer">Remove Layer</button>
      </div> -->
   </div>
</body>
</html>
