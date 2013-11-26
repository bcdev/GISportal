/**
 * Custom JavaScript functionality
 * @namespace
 */
opec.utils = {};

/**
 * An extremely handy PHP function ported to JS, works well for templating
 * 
 * @param {(string|Array)} search - A list of things to search for
 * @param {(string|Array)} replace - A list of things to replace the searches with
 * @param {string} subject - The string to search
 * @return {string} The resulting string
 */  
opec.utils.replace = function(search, replace, subject, count) {
   var i = 0, j = 0, temp = '', repl = '', sl = 0, fl = 0,
      f = [].concat(search),
      r = [].concat(replace),
      s = subject,
      ra = r instanceof Array, sa = s instanceof Array;
   s = [].concat(s);
   
   if(count) {
      this.window[count] = 0;
   }

   for(i = 0, sl = s.length; i < sl; i++) {      
      if(s[i] === '') {
         continue;
      }
      
      for (j = 0, fl = f.length; j < fl; j++) {     
             
         temp = s[i] + '';
         repl = ra ? (r[j] !== undefined ? r[j] : '') : r[0];
         s[i] = (temp).split(f[j]).join(repl);
         
         if(count && s[i] !== temp) {
            this.window[count] += (temp.length-s[i].length) / f[j].length;
         }       
      }
   }
   
   return sa ? s : s[0];  
};

/**
 * Extension to JavaScript Arrays to de-duplicate them
 */ 
opec.utils.arrayDeDupe = function(array) {
   var i,
      len = array.length,
      outArray = [],
      obj = {};
      
   for (i = 0; i < len; i++) { obj[array[i]] = 0; }
   for (i in obj) { outArray.push(i); }
   return outArray;
};

/** 
 * Array Remove - By John Resig (MIT Licensed)
 */
opec.utils.arrayRemove = function(array, from, to) {
   var rest = array.slice((to || from) + 1 || array.length);
   array.length = from < 0 ? array.length + from : from;
   return array.push.apply(array, rest);
};

/**
 * Helper function which returns the nearest value in an array to a given value
 *
 * @param {number|Array}   arr   The array of integers to search within
 * @param {number}         goal  The value for which to find the nearest
 *
 * @return {number} Returns the value of the nearest number in the array
 */
getNearestInArray = function(arr, goal) {
   var closest = null;
   $.each(arr, function(i, e) {
      if (closest === null || Math.abs(e - goal) < Math.abs(closest - goal)) {
         closest = e;
      }
   });
   return closest;
};

/**
 * Turn JavaScript date, d into ISO8601 date part (no time)
 */ 
opec.utils.ISODateString = function(d) {
   function pad(n){
      return n<10 ? '0'+n : n;
   }
   // Add 1 to month as its zero based.
   var datestring = d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate());
   return datestring;
};

/**
 * Returns true if first date is smaller than second
 */ 
opec.utils.compareDates = function(firstDate, secondDate) { 
   var firstDate = opec.utils.ISODateString(firstDate);
   var secondDate = opec.utils.ISODateString(secondDate);
   if (firstDate < secondDate) return true;
   return false;
};
   

/**
 * Format date string so it can be displayed
 */ 
opec.utils.displayDateString = function(date) {
   var year = date.substring(0, 4);
   var month = date.substring(5, 7);
   var day = date.substring(8, 10);
   return day + '-' + month + '-' + year;
};

function getObjectKey(obj, value) {
   for(var key in obj) {
      // TEST
      if(obj[key] == value) {
         return key;
      }
   }
   return null;
}

opec.utils.sortDates = function(a, b) {
   return a[0] - b[0];
};

opec.utils.ceil1places = function(num) {
   return Math.ceil(num * 10) / 10;
};

opec.utils.ceil3places = function(num) {
   return Math.ceil(num * 1000) / 1000;
};

opec.utils.clamp = function (num, min, max) {
   return Math.min(Math.max(num, min), max);
};

opec.utils.getURLParameter = function(name) {
   return decodeURIComponent((new RegExp('[?|&]' + name + '=' + '([^&;]+?)(&|#|;|$)').exec(location.search)||[,""])[1].replace(/\+/g, '%20'))||null;
};

// A function for getting unique identifier, generic function so that it can easily be changed throughout the codebase
opec.utils.uniqueID = function()  {
   return new Date().getTime();
};

opec.utils.isNullorUndefined = function(object) {
   if(object === null || typeof object === "undefined") {
      return true;
   }
   
   return false;
};

/* Taken from:
 *    https://code.google.com/p/step2/source/browse/code/java/trunk/example-consumer/src/main/webapp/popuplib.js 
 *    Apache 2.0 License
 * 
 * Computes the size of the window contents. Returns a pair of
 * coordinates [width, height] which can be [0, 0] if it was not possible
 * to compute the values.
 */
opec.utils.getWindowInnerSize = function() {
  var width = 0;
  var height = 0;
  var elem = null;
  if ('innerWidth' in window) {
    // For non-IE
    width = window.innerWidth;
    height = window.innerHeight;
  } else {
    // For IE,
    if (('BackCompat' === window.document.compatMode)
        && ('body' in window.document)) {
        elem = window.document.body;
    } else if ('documentElement' in window.document) {
      elem = window.document.documentElement;
    }
    if (elem !== null) {
      width = elem.offsetWidth;
      height = elem.offsetHeight;
    }
  }
  return [width, height];
};

/* Taken from:
 *    https://code.google.com/p/step2/source/browse/code/java/trunk/example-consumer/src/main/webapp/popuplib.js 
 *    Apache 2.0 License
 * 
 * Computes the coordinates of the parent window.
 * Gets the coordinates of the parent frame.
 */
opec.utils.getParentCoords = function() {
  var width = 0;
  var height = 0;
  if ('screenLeft' in window) {
    // IE-compatible variants
    width = window.screenLeft;
    height = window.screenTop;
  } else if ('screenX' in window) {
    // Firefox-compatible
    width = window.screenX;
    height = window.screenY;
  }
  return [width, height];
};

/* Taken from:
 *    https://code.google.com/p/step2/source/browse/code/java/trunk/example-consumer/src/main/webapp/popuplib.js 
 *    Apache 2.0 License
 * 
 * Computes the coordinates of the new window, so as to center it
 * over the parent frame.
 */
opec.utils.getCenteredCoords = function(width, height) {
   var parentSize = opec.utils.getWindowInnerSize();
   var parentPos = opec.utils.getParentCoords();
   var xPos = parentPos[0] +
       Math.max(0, Math.floor((parentSize[0] - width) / 2));
   var yPos = parentPos[1] +
       Math.max(0, Math.floor((parentSize[1] - height) / 2));
   return [xPos, yPos];
};

opec.utils.openPopup = function(width, height, url, onOpenHandler, checkforCloseHandler) {
   if(onOpenHandler !== null) {
      onOpenHandler();
   }
   
   var coordinates = opec.utils.getCenteredCoords(width, height);
   var popupWindow = window.open(url, "", 
      "width=" + width + 
      ", height=" + height + 
      ", status = 1, location = 1, resizable = yes" + 
      ", left=" + coordinates[0] + 
      ", top=" + coordinates[1]
   );
   var interval = window.setInterval(checkforCloseHandler, 80);
   return {'popupWindow':popupWindow, 'interval': interval};
};
