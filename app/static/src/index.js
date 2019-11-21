$(document).ready(() => {
  console.log("ready");

  function login() {
    $('#search').removeClass('hidden');
    $('#result').removeClass('hidden');
    $('#logout-btn').removeClass('hidden');
    $('#login-btn').addClass('hidden');
    $('#register-btn').addClass('hidden');
    $('html, body').animate({ scrollTop: $('#search').offset().top }, 500);

  }

  function logout() {
    $('#logout-btn').addClass('hidden');
    $('#search').addClass('hidden');
    $('#result').addClass('hidden');
    $('#login-btn').removeClass('hidden');
    $('#register-btn').removeClass('hidden');
    sessionStorage.removeItem('api-token');
  }

  if (sessionStorage.getItem('api-token')) {
    console.log("already logged in");
    // $('#logout-btn').removeClass('hidden');
    // $('#login-btn').addClass('hidden');
    // $('#register-btn').addClass('hidden');
    login();

  }
  $('#login-btn').click(() => {
    $('#login').modal('show');
  });

  $('#register-btn').click(() => {
    $('#register').modal('show');
  });

  $('#logout-btn').click(() => {
    logout();
  });

  $('#login-form').form({
    fields: {
      name: {
        identifier: 'name',
        rules: [
          {
            type: 'empty',
            prompt: 'Please enter your username'
          }
        ]
      },
      password: {
        identifier: 'password',
        rules: [
          {
            type: 'empty',
            prompt: 'Please enter a password'
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
            type: 'empty',
            prompt: 'Please enter your username'
          }
        ]
      },
      password: {
        identifier: 'password',
        rules: [
          {
            type: 'empty',
            prompt: 'Please enter a password'
          }
        ]
      },
    }
  });


  $('#login-form').on('submit', function (e) {
    e.preventDefault();
    var username = $('#uname-login').val().trim().toString();
    var password = $('#pass-login').val().trim().toString();
    console.log(username);
    console.log(password);

    $.ajax({
      url: '/login',
      type: 'POST',
      contentType: 'application/json',
      beforeSend: function (xhr) {
        xhr.setRequestHeader("Authorization", "Basic " + btoa(username + ":" + password));
      },
      data: {
        "name": $('#uname-login').val().trim(),
        "password": $('#pass-login').val().trim(),
      },
      success: function (data) {
        $('#success-login').removeClass('hidden');
        login();
        sessionStorage.setItem('api-token', data.token);
      },
      error: function (jXHR, textStatus, errorThrown) {
        console.log(textStatus);

        $('#fail-login').removeClass('hidden');
      }
    });
  });

   $('#register-form').on('submit', function (e) {
    e.preventDefault();
    var name = $('#uname-register').val().trim().toString();
    var password = $('#pass-register').val().trim().toString();

    var json = {
        "name": name,
        "password": password
      };
    json = JSON.stringify(json);

    $.ajax({
      url: '/register',
      type: 'POST',
      contentType: 'application/json',
      data: json,
      dataType: 'json',
      success: function (data) {
        $('#success-register').removeClass('hidden');
      },
      error: function (jXHR, textStatus, errorThrown) {
        console.log(textStatus);
        $('#fail-register').removeClass('hidden');
      }
    });
  });


  // ------------------------- Search -------------------------------------//
  $('#search-form')
    .form({
      fields: {
        location: {
          identifier: 'location',
          rules: [
            {
              type: 'empty',
              prompt: 'Please enter the location'
            }
          ]
        },
        area: {
          identifier: 'area',
          rules: [
            {
              type: 'empty',
              prompt: 'Please select at least two skills'
            }
          ]
        },
        type_room: {
          identifier: 'type_room',
          rules: [
            {
              type: 'empty',
              prompt: 'Please select a room type'
            }
          ]
        },
        start_date: {
          identifier: 'start_date',
          rules: [
            {
              type: 'empty',
              prompt: 'Please enter a Start Date'
            }
          ]
        },
        end_date: {
          identifier: 'end_date',
          rules: [
            {
              type: 'empty',
              prompt: 'Please enter an End Date'
            }
          ]
        },
        guest: {
          identifier: 'guest',
          rules: [
            {
              type: 'empty',
              prompt: 'Please specify number of guest'
            }
          ]
        },
        price_1: {
          identifier: 'price_1',
          rules: [
            {
              type: 'empty',
              prompt: 'Please enter the price range'
            }
          ]
        },
        price_2: {
          identifier: 'price_2',
          rules: [
            {
              type: 'empty',
              prompt: 'Please enter the price range'
            }
          ]
        },
      }
    });

  $('#search-form').on('submit', function (e) {
    e.preventDefault();
    if ($('#search-form').form('is valid')) {
      $('html, body').animate({ scrollTop: $('#result').offset().top }, 500);
    }

    $('#result').animate({ scrollTop: 0 }, 0);
    let location = e.target[1].value.toString();
    let area = e.target[2].value.toString();
    let type_room = e.target[3].value.toString();
    let start_date = e.target[4].value.toString();
    let end_date = e.target[5].value.toString();
    let guest = e.target[6].value.toString();
    let price_1 = e.target[7].value.toString();
    let price_2 = e.target[8].value.toString();
    let token = sessionStorage.getItem('api-token');
    var json = {
      "token": token,
      "location": location,
      "area": area,
      "type_room": type_room,
      "start_date": start_date,
      "end_date": end_date,
      "guest": guest,
      "price_1": price_1,
      "price_2": price_2
    };
    
    $.ajax({
      url: '/search_json',
      type: 'POST',
      cache: false,
      data: json,
      success: function (data) {
        console.log(data);
        console.log(data[0]["name"]);
        for (let i = 0; i < data.length; i++) {
          let element = data[i];
          let doc = $('result');
          doc
        }
      },
      error: function (jXHR, textStatus, errorThrown) {
        // console.log(errorThrown);
        console.log(textStatus);
        // console.log(jXHR);
      }
    });
  })
});
