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
  ], function($,
              bdajax
              ){
  'use strict';

  $(document).ready(function(){

    // XXX this mus be wrapped in a document ready
    bdajax.spinner.hide();
    $(document).bdajax();
    // /XXX

  });

});
