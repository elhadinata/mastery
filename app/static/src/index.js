$(document).ready(()=>{
    console.log("ready");

    function login() {
      $('#search').removeClass('hidden');
      $('#logout-btn').removeClass('hidden');
      $('#login-btn').addClass('hidden');
      $('#register-btn').addClass('hidden');
    }

    if(sessionStorage.getItem('api-token')) {
      console.log("already logged in");
      // $('#logout-btn').removeClass('hidden');
      // $('#login-btn').addClass('hidden');
      // $('#register-btn').addClass('hidden');
      login();
      
    }
    $('#login-btn').click(()=>{
        $('#login').modal('show');
    });
    
    $('#register-btn').click(()=>{
        $('#register').modal('show');
    });

    $('#logout-btn').click(()=>{
      $('#logout-btn').addClass('hidden');
      $('#search').addClass('hidden');
      $('#login-btn').removeClass('hidden');
      $('#register-btn').removeClass('hidden');
      sessionStorage.removeItem('api-token');
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
        var username = $('#uname-login').val().trim().toString();
        var password = $('#pass-login').val().trim().toString();
        console.log(username);
        console.log(password);
        
        $.ajax({
            url : '/login',
            type: 'POST',
            contentType: 'application/json',
            beforeSend: function (xhr) {
              xhr.setRequestHeader ("Authorization", "Basic " + btoa(username + ":" + password));
            },
            data: {
                "name": $('#uname-login').val().trim(),
                "password": $('#pass-login').val().trim(),
            },
            success: function (data) {
                // console.log(data.token);
                $('#success-login').removeClass('hidden');
                // $('#logout-btn').removeClass('hidden');
                // $('#login-btn').addClass('hidden');
                // $('#register-btn').addClass('hidden');
                login();
                sessionStorage.setItem('api-token', data.token);
            },
            error: function (jXHR, textStatus, errorThrown) {
                // console.log(errorThrown);
                console.log(textStatus);
                // console.log(jXHR);
                
                $('#fail-login').removeClass('hidden');
            }
        });
    });
});