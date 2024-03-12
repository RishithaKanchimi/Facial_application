$(document).ready(function () {
      $('.sidebar .nav .userApprove').click(function() {
        $('#approve').hide();
        $('#userApprove').show();
         $('.faceverification').hide();
      })

        $('.sidebar .nav .Approve').click(function() {
        $('#approve').show();
        $('#userApprove').hide();
         $('.faceverification').hide();
      })
    
       $('.sidebar .nav .facialverification').click(function() {         
           $('.faceverification').show();
              $('#userApprove').hide();
               $('#approve').hide();
        })   
});

$(function () {
  $("#datepicker").datepicker({ 
        autoclose: true, 
        todayHighlight: true
  }).datepicker('update', new Date());;
});

$(document).ready( function () {
    $('#usertable').DataTable();
} );

$(function() {
      $( 'ul.nav li' ).on( 'click', function() {
            $( this ).parent().find( 'li.active' ).removeClass( 'active' );
            $( this ).addClass( 'active' );
      });
});

$(document).ready(function () {
      $('.sidebar .nav .clearregistration').click(function() {
        $('#registration').hide();
        $('.clear_registration').show();
      })

        $('.sidebar .nav .registration').click(function() {
        $('#registration').show();
        $('.clear_registration').hide();
      })
});
