/*jslint browser: true*/
/*global $, jQuery, define*/

/* global require */

if(window.jQuery){
  define('jquery', function(){
    return window.jQuery;
  });
}

require([
  'jquery',
  'bdajax',
  // 'bdajax-overlay',
  ], function($,
              bdajax
              ){
  'use strict';

  $(document).ready(function(){
    bdajax.spinner.hide();
    $(document).bdajax();
  });

});
