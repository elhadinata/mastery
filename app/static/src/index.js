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

    $('#register-form').on('submit', function(e) {
      e.preventDefault();
      var name = $('#uname-register').val().trim();
      var password = $('#pass-register').val().trim();
      console.log(name);
      console.log(password);
      
      $.ajax({
          url : '/register',
          type: 'POST',
          contentType: 'application/json',
          data: {
              "name": name,
              "password": password
          },
          success: function (data) {
              console.log(name + " registered!")
              $('#success-register').removeClass('hidden');
              // $('#register-btn').addClass('hidden');
              // login();
              // sessionStorage.setItem('api-token', data.token);
          },
          error: function (jXHR, textStatus, errorThrown) {
              // console.log(errorThrown);
              console.log("ERROR REGISTER")
              console.log(textStatus);
              // console.log(jXHR);
              
              $('#fail-register').removeClass('hidden');
          }
      });
  });

    $('#search-form').on('submit', function(e) {
      e.preventDefault();
      // console.log(e);
      let location = e.target[1].value.toString();
      let area= e.target[2].value.toString();
      let type_room = e.target[3].value.toString();
      let start_date = e.target[4].value.toString();
      let end_date = e.target[5].value.toString();
      let guest = e.target[6].value.toString();
      let price_1 = e.target[7].value.toString();
      let price_2 = e.target[8].value.toString();
      let token = sessionStorage.getItem('api-token');
      console.log(location);
      console.log(area);
      console.log(type_room);
      console.log(start_date);
      console.log(end_date);
      console.log(guest);
      console.log(price_1);
      console.log(price_2);
      
      console.log(token)
      $.ajax({
        url : '/search_json',
        type: 'POST',
        cache: false,
        data: {
          "token": token,
          "location": location,
          "area": area,
          "type_room": type_room,
          "start_date": start_date,
          "end_date": end_date,
          "guest": guest,
          "price_1": price_1,
          "price_2": price_2
        },
        success: function (data) {
            console.log(data);
            console.log("YASS");
        },
        error: function (jXHR, textStatus, errorThrown) {
            // console.log(errorThrown);
            console.log(textStatus);
            // console.log(jXHR);
        }
    });
    })
});