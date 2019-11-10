$(document).ready(()=>{
    console.log("ready");
    $('#login-btn').click(()=>{
        $('#login').modal('show');
    });
    
    $('#register-btn').click(()=>{
        $('#register').modal('show');
    });


    $('#login-form').form({
        fields: {
          name: {
            identifier: 'name',
            rules: [
              {
                type   : 'empty',
                prompt : 'Please enter your username'
              }
            ]
          },
          password: {
            identifier: 'password',
            rules: [
              {
                type   : 'empty',
                prompt : 'Please enter a password'
              }
            ]
          },
        }
    });

    $('#register-form').form({
        fields: {
          name: {
            identifier: 'name',
            rules: [
              {
                type   : 'empty',
                prompt : 'Please enter your username'
              }
            ]
          },
          password: {
            identifier: 'password',
            rules: [
              {
                type   : 'empty',
                prompt : 'Please enter a password'
              }
            ]
          },
        }
    });


    $('#login-form').on('submit', function(e) {
        e.preventDefault();
        var i = $('#uname-login').val().trim().toString();
        var j = $('#pass-login').val().trim().toString();
        console.log(i);
        console.log(j);
        
        $.ajax({
            url : '/login',
            type: 'POST',
            contentType: 'application/json',
            data: {
                "name": $('#uname-login').val().trim(),
                "password": $('#pass-login').val().trim(),
            },
            success: function (data) {
                console.log(data);
                $("#success-login").html(data);
                $('#success-login').removeClass('hidden');
            },
            error: function (jXHR, textStatus, errorThrown) {
                console.log(errorThrown);
                console.log(textStatus);
                console.log(jXHR);
                
                $('#fail-login').removeClass('hidden');
            }
        });
    });
});