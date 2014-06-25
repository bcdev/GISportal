/**
 * Openid
 * @namespace 
 */
gisportal.openid = {};

gisportal.openid.setup = function(containerID) {
   gisportal.openid.loginBox = containerID;
   gisportal.openid.$loginBox = $('#' + containerID);
   gisportal.openid.darkCoverID = 'darkCover';
  
   gisportal.openid.logoutLocation = '/service/logout'; 
   gisportal.openid.popupWindow = null;
   
   gisportal.openid.loginForm = 'gisportal-openid-form'; // Set id for login form
   gisportal.openid.$loginForm = $('#' + gisportal.openid.loginForm);

   gisportal.openid.saveButton = 'gisportal-openid-getlink';
   gisportal.openid.$saveButton = $('#' + gisportal.openid.saveButton);
 
   gisportal.openid.logoutButton = 'gisportal-openid-logout';
   gisportal.openid.$logoutButton = $('#' + gisportal.openid.logoutButton);

   gisportal.openid.content = 'gisportal-openid-content';
   gisportal.openid.$content = $('#' + gisportal.openid.content);

   gisportal.openid.onOpenHandler = function() {
      gisportal.openid.darkscreen(gisportal.openid.darkCoverID);
   };

   gisportal.openid.onCloseHandler = function () {
       gisportal.openid.set_userinfo_to_html();
       gisportal.refreshOpLayers();
       if (gisportal.openid.is_logged_in()) {
           gisportal.openid.hideLogin();
       } else {
           gisportal.openid.showLogin();
       }
   };
   
   gisportal.openid.darkCoverStyle = [
      'position: absolute;',
      'top: 0px;',
      'left: 0px;',
      'padding-right: 0px;',
      'padding-bottom: 0px;',
      'background-color:#000000;',
      'opacity: 0.5;',
      '-moz-opacity: 0.5;',
      'filter: alpha(opacity = 0.5);',
      'z-index: 10000;',
      'width: 100%;',
      'height: 100%;'
   ].join(' ');
   gisportal.openid.interval = null;
   
   
   var data = {
      id: gisportal.openid.loginForm,
      providers: gisportal.openid.providers,
      provider: function() {
         return function(text, render) {
            return render(gisportal.templates.providerBox({
               name: this.name, 
               title: this.title, 
               url: this.url, 
               imagePath: this.imagePath, 
               x: this.x, 
               y: this.y,
               width: this.width,
               height: this.height
            }));
         };
      }
   };
   
   gisportal.openid.$loginBox.append(gisportal.templates.loginBox(data)); 
 
   $('#' + gisportal.openid.loginForm + ' .gisportal-login-with-google').click(function() {
      var $this = $(this);     
      gisportal.openid.openPopup($this.attr('data-url'));  
   });
   
   $('#' + gisportal.openid.loginForm + ' .gisportal-login-with-yahoo').click(function() {
      var $this = $(this);     
      gisportal.openid.openPopup($this.attr('data-url'));
   });

   $('#' + gisportal.openid.loginForm + ' .gisportal-login-with-bc').click(function() {
      var $this = $(this);
      gisportal.openid.openPopup($this.attr('data-url'));
   });
   

   gisportal.openid.$saveButton.click(function() {
      gisportal.openid.getLink();
   });

   gisportal.openid.$logoutButton.click(function()  {
      gisportal.openid.logout();
   });

};

gisportal.openid.set_userinfo_to_html = function() {
    // todo -- do this only when allowed to
    var on_success = function (data, opts) {
        $('#user_name').html(data.username);
        $('#user_full_name').html(data.fullname);
        $('#user_openid').html(data.openid);
        $('#user_mail').html(data.email);
        $('#user_groups').html(data.usergroups);
    };
    var on_error = function (request, errorType, exception) {
        $('#user_name').html(null);
        $('#user_full_name').html(null);
        $('#user_openid').html(null);
        $('#user_mail').html(null);
        $('#user_groups').html(null);
        console.log('Error: Failed to retrieved username. Ajax failed!');
    };
    gisportal.genericSync('POST', gisportal.middlewarePath + "/get_user", null, on_success, on_error, 'json', {});
};

// getLink to state
gisportal.openid.getLink = function()  {
   gisportal.genericAsync('POST', gisportal.stateLocation, { state: JSON.stringify(gisportal.getState())}, function(data, opts) { 
      if (data['output']['url']) {
         console.log(data['output']);
         $('#gisportal-openid-shareurl').val(location.origin + location.pathname + '?state=' + data['output']['url']);
      }
   }, 
   function(request, errorType, exception) {
      console.log(request, errorType, exception);
      if (exception === 'UNAUTHORIZED') gisportal.openid.showLogin();
   }, 'json', {});
};

gisportal.openid.logout = function() { gisportal.genericAsync('GET', gisportal.openid.logoutLocation, null, function(data, opts) {
      console.log(data); 
      if (data == '200')  {
         gisportal.openid.set_userinfo_to_html();
         gisportal.openid.showLogin();
      }
   }, 
   function(request, errorType, exception) {
      console.log(request, errorType, exception);
      if (exception === 'UNAUTHORIZED') gisportal.openid.showLogin();
   }, 'json', {});
};

gisportal.openid.is_logged_in = function() {
    var userName = $('#user_name').text();
    return userName != "" && userName != 'null' && userName != undefined;
};

gisportal.openid.openPopup = function(urlToOpen) {
   var windowWidth = '870px';
   var windowHeight = '600px';
      
   var dataObject = gisportal.utils.openPopup(windowWidth, windowHeight, urlToOpen, gisportal.openid.onOpenHandler, gisportal.openid.waitForPopupClose);  
   gisportal.openid.popupWindow = dataObject.popupWindow;
   gisportal.openid.interval = dataObject.interval;
};

gisportal.openid.showLogin = function() {
   $('#' + gisportal.openid.loginForm).show();
   gisportal.openid.$content.hide();
   gisportal.logout();
};

gisportal.openid.hideLogin = function() {
   $('#' + gisportal.openid.loginForm).hide();
   gisportal.openid.$content.show();
   gisportal.login();
};

//======== POPUP MANAGEMENT ========//
/* Taken from:
 *    https://code.google.com/p/step2/source/browse/code/java/trunk/example-consumer/src/main/webapp/popuplib.js 
 *    Apache 2.0 License
 */

gisportal.openid.darkscreen = function(darkCover) {
   var darkCoverDiv = $('#' + darkCover);
   if(darkCoverDiv.length === 0) {
      darkCoverDiv = $('<div></div>')
         .attr('style', gisportal.openid.darkCoverStyle)
         .attr('id', darkCover);
      $(document.body).append(darkCoverDiv);
      
   }
   darkCoverDiv.show();
};

// Check to perform at each execution of the timed loop. It also triggers
// the action that follows the closing of the popup
gisportal.openid.waitForPopupClose = function() {
   if (gisportal.openid.isPopupClosed()) {
      gisportal.openid.popupWindow = null;
      var darkCover = $('#' + gisportal.openid.darkCoverID);
      if (darkCover.length !== 0) {
         darkCover.hide();
      }
      if (gisportal.openid.onCloseHandler !== null) {
         gisportal.openid.onCloseHandler();
      }
      if (gisportal.openid.interval !== null) {
         window.clearInterval(gisportal.openid.interval);
         gisportal.openid.interval = null;
      }
      
   }
};

// Tests that the popup window has closed
gisportal.openid.isPopupClosed = function() {
   return (!gisportal.openid.popupWindow || gisportal.openid.popupWindow.closed);
};

//======== ENDOF POPUP MANAGEMENT ========//

gisportal.openid.providers = [
   {name: 'bc', title:'Login at Brockmann Consult', url:'/service/login', imagePath:'img/bc_signin_btn.png', x:'0', y:'0', width:'161px', height:'22px'}
];
