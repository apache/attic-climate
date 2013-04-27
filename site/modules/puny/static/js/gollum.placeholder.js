/*
 * Licensed to the Apache Software Foundation (ASF) under one or more
 * contributor license agreements.  See the NOTICE file distributed with
 * this work for additional information regarding copyright ownership.
 * The ASF licenses this file to You under the Apache License, Version 2.0
 * (the "License"); you may not use this file except in compliance with
 * the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

(function($) {

  var Placeholder = {
   
     _PLACEHOLDERS : [],
   
    _p : function( $field ) {
    
       this.fieldObject = $field; 
       this.placeholderText = $field.val();
       var placeholderText = $field.val();
     
       $field.addClass('ph');
     
       $field.blur(function() {
         if ( $(this).val() == '' ) {
           $(this).val( placeholderText );
           $(this).addClass('ph');
         }
       });
     
       $field.focus(function() {
         $(this).removeClass('ph');
         if ( $(this).val() == placeholderText ) {
           $(this).val('');
         } else {
           $(this)[0].select();
         }
       });
     
     },
   
     add : function( $field ) {
       Placeholder._PLACEHOLDERS.push( new Placeholder._p( $field ) );
     },
   
     clearAll: function() {
       for ( var i=0; i < Placeholder._PLACEHOLDERS.length; i++ ) {
         if ( Placeholder._PLACEHOLDERS[i].fieldObject.val() == 
              Placeholder._PLACEHOLDERS[i].placeholderText ) {
           Placeholder._PLACEHOLDERS[i].fieldObject.val('');
         }
       }
     },
   
     exists : function() {
       return ( _PLACEHOLDERS.length );
     }
   
 };
 
 $.GollumPlaceholder = Placeholder;
 
})(jQuery);