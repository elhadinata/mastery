$(document).ready(() => {
  console.log("ready");

  function formatDate(date) {
    var d = new Date(date),
        month = '' + (d.getMonth() + 1),
        day = '' + d.getDate(),
        year = d.getFullYear();

    if (month.length < 2) 
        month = '0' + month;
    if (day.length < 2) 
        day = '0' + day;

    return [year, month, day].join('-');
  }
  if (sessionStorage.getItem('api-token')) {
    console.log("already logged in");

  }

  $('#login-form').on('submit', function (e) {
    e.preventDefault();
    var username = $('#uname-login').val().trim().toString();
    var password = $('#pass-login').val().trim().toString();
    console.log(username);
    console.log(password);
    var data = {
      "username": username,
      "password": password
    };
    $.ajax({
      url: 'http://127.0.0.1:5000/token',
      type: 'GET',
      contentType: 'application/x-www-form-urlencoded',
      // beforeSend: function (xhr) {
      //   xhr.setRequestHeader("Authorization", "Basic " + btoa(username + ":" + password));
      // },
      data: data,
      success: function (data) {      
        sessionStorage.setItem('api-token', data.token);
        console.log("logged in")
        console.log("TOKEN " +data.token)
      },
      error: function (jXHR, textStatus, errorThrown) {
        console.log(textStatus);
      }
    });
  });

   $('#register-form').on('submit', function (e) {
    e.preventDefault();
    var name = $('#uname-register').val().trim().toString();
    var password = $('#pass-register').val().trim().toString();

    var data = {
        "username": name,
        "password": password
      };
    json = JSON.stringify(data);
    $.ajax({
      url: "http://127.0.0.1:5000/user_register",
      type: 'POST',
      contentType: 'application/json',
      data: json,
      
      // dataType: 'json',
      success: function (data) {
        console.log("succesfully registered");
      },
      error: function (jXHR, textStatus, errorThrown) {
        console.log(textStatus);
        console.log(jXHR);
        console.log(errorThrown);
      }
    });
  });

  function makeBooking(id, json) {
    $.ajax({
      url: 'http://127.0.0.1:5000/book/'+id,
      type: 'POST',
      contentType: 'application/json',
      beforeSend: function (xhr) {
        xhr.setRequestHeader("api-token", sessionStorage.getItem('api-token'));
      },
      data: json,
      success: function (data) {
        console.log("booking created!!");

      },
      error: function (jXHR, textStatus, errorThrown) {
        console.log(errorThrown);
        console.log(textStatus);
        console.log(jXHR);
      }
    });   
  }

  function updateDetails(data) {
    $('#search-result-details').empty();
    var div = document.createElement('div');
    var ul = document.createElement('ul');
    for(var o in data.record) {
      var li = document.createElement('li');
      li.innerText=o+' : '+data.record[o];
      ul.append(li);
    }
    div.appendChild(ul)

    $('#search-result-details').append(div);
  }

  function pay(data) {
    // console.log(data.record);
    const url = 'http://127.0.0.1:5000/makepay/'+data.record.id;
    var json = {
      'name': data.record.name,
      'neighbourhood_group': data.record.neighbourhood_group,
      'neighbourhood': data.record.neighbourhood,
      'room_type': data.record.room_type,
      'price': data.record.price,
      'id': data.record.id
    };

    let redirect = function(url, method) {
      let form = document.createElement('form');
      form.method = method;
      form.action = url;

      for (let name in json) {
        console.log(name+' '+json[name]);
        let input = document.createElement('input');
        input.type = 'hidden';
        input.name = name;
        input.value = json[name];
        form.appendChild(input);
        console.log(input);
      }
      document.body.appendChild(form);
      form.submit();
      document.body.removeChild(form);
    };
  
    redirect('http://127.0.0.1:5000/makepay/'+data.record.id, 'post');
  }

  function setupBooking(data) {
    
    var btn = document.createElement('button');
    btn.setAttribute('type', 'button');
    btn.setAttribute('id', 'book-btn');
    btn.innerHTML = "Book the room";
    $('#search-result-details').append(btn);
    
    
    $('#book-btn').click(()=> {
        console.log(data.record);
        var start = $('#start_date').val().trim().toString();
        var end = $('#end_date').val().trim().toString();
        
        var json = {
          'start_date': formatDate(start),
          'end_date': formatDate(end),
          
        };
        json = JSON.stringify(json);
        makeBooking(data.record.id, json);
      });
  }
  function setupPayment(data) {
    var btn1 = document.createElement('button');
    btn1.setAttribute('type', 'submit');
    btn1.setAttribute('id', 'pay-btn');
    btn1.innerHTML = "Pay for the room";
    $('#search-result-details').append(btn1);
    
    $('#pay-btn').click(()=> {
        pay(data);
    });
  }
  
  function setupRecommendation(data) {
    
    $('#search-result-rec').empty();
    var ul1 =document.createElement('ul');
                    
    console.log(data.recommendation);
    for(let o in data.recommendation) {
      
      var text = document.createElement('h3');
      text.innerText = data.recommendation[o].name;
      var li1 = document.createElement('li');
      li1.setAttribute('id', data.recommendation[o].id);
      // Header
      li1.appendChild(text);
      // if click on it then display details
      const index = o;
      li1.onclick = function(e) {
        e.preventDefault();
        $.ajax({
          url: 'http://127.0.0.1:5000/accommodation/'+data.recommendation[index].id+'/details',
          type: 'GET',
          contentType: 'application/json',
          beforeSend: function (xhr) {
            xhr.setRequestHeader("api-token", sessionStorage.getItem('api-token'));
          },
          success: function (data) {

            console.log(data);
            // ============================== UPDATE ================================ //
            updateDetails(data);
            // ============================== BOOKING =============================== //                
            setupBooking(data);
            // ============================== PAYMENT =============================== //
            setupPayment(data);
                    
            $.ajax({
              url: 'http://127.0.0.1:5000/accommodation/'+data.record.id,
              type: 'GET',
              contentType: 'application/json',
              beforeSend: function (xhr) {
                xhr.setRequestHeader("api-token", sessionStorage.getItem('api-token'));
              },
              success: function (data) {        
                setupRecommendation(data);
                  
                }
              })
              
            }
          })
        }


      ul1.append(li1);
    }
    $('#search-result-rec').append(ul1);
    console.log(data);
  }

  $('#search-form').on('submit', function (e) {
    e.preventDefault();
  
    let location = e.target[0].value.toString();
    let area = e.target[1].value.toString();
    let type_room = e.target[2].value.toString();
    let start_date = e.target[3].value.toString();
    let end_date = e.target[4].value.toString();
    let guest = e.target[5].value.toString();
    let price_1 = e.target[6].value.toString();
    let price_2 = e.target[7].value.toString();
    let station = e.target[8].value.toString();
    let token = sessionStorage.getItem('api-token');
    var data = {
      'location': location,
      'area': area,
      'type_room': type_room,
      'start_date': formatDate(start_date),
      'end_date': formatDate(end_date),
      'guest': guest,
      'price_1': price_1,
      'price_2': price_2,
      'station': station,
    };
    console.log(data);
    data = JSON.stringify(data);  
    $.ajax({
      url: 'http://127.0.0.1:5000/search',
      type: 'POST',
      
      contentType: 'application/json',
      data: data,
      beforeSend: function (xhr) {
        xhr.setRequestHeader("api-token", sessionStorage.getItem('api-token'));
      },
      success: function (data) {
        console.log(data);
        $('#search-result').empty();
        for (let o in data) {
          var li = document.createElement('li');
          li.setAttribute('id', data[o].id);
          
          var a = document.createElement('a');
          a.innerText = data[o].name+' '+data[o].price+' '+data[o].number_of_reviews;
          li.appendChild(a);

          var id = data[o].id;
          $('#search-result').append(li);
          $('#'+data[o].id).click(()=> {
            $.ajax({
              url: 'http://127.0.0.1:5000/accommodation/'+data[o].id+'/details',
              type: 'GET',
              contentType: 'application/json',
              beforeSend: function (xhr) {
                xhr.setRequestHeader("api-token", sessionStorage.getItem('api-token'));
              },
              success: function (data) {

                console.log(data);
                updateDetails(data);
                
                // ==================== book =============================//
                setupBooking(data);
                // ============================== PAYMENT =============================== //
                setupPayment(data);
                // ============================== RECOMMENDATION ================================ //
                $('#search-result-rec').empty();
                $.ajax({
                  url: 'http://127.0.0.1:5000/accommodation/'+id,
                  type: 'GET',
                  contentType: 'application/json',
                  beforeSend: function (xhr) {
                    xhr.setRequestHeader("api-token", sessionStorage.getItem('api-token'));
                  },
                  success: function (data) {
                    setupRecommendation(data);
                    
                  },
                  error: function (jXHR, textStatus, errorThrown) {
                    console.log(errorThrown);
                    console.log(textStatus);
                    console.log(jXHR);
                  }
                });
                    
                },
                error: function (jXHR, textStatus, errorThrown) {
                  console.log(errorThrown);
                  console.log(textStatus);
                  console.log(jXHR);
                }
              });
              
          })
        }
        
      },
      error: function (jXHR, textStatus, errorThrown) {
        console.log(errorThrown);
        console.log(textStatus);
        console.log(jXHR);
      }
    })
  })


  $('#update-booking').click(()=>{
    $.ajax({
      url: 'http://127.0.0.1:5000/book',
      type: 'GET',
      contentType: 'application/json',
      beforeSend: function (xhr) {
        xhr.setRequestHeader("api-token", sessionStorage.getItem('api-token'));
      },
      success: function (data) {
        $('#bookings').empty();
        console.log(data.booking);
        for(var o in data.booking) {
          var li = document.createElement('li');
          li.innerText = 'listing: '+data.booking[o].listing_id+' | owner : '+data.booking[o].owner_id+' | renter: '+data.booking[o].renter_id;
          
          var btn = document.createElement('button');
          btn.innerText = 'Delete booking';
          btn.onclick = function() {
            $.ajax({
              url: 'http://127.0.0.1:5000/book/'+data.booking[o].listing_id,
              type: 'DELETE',
              contentType: 'application/json',
              beforeSend: function (xhr) {
                xhr.setRequestHeader("api-token", sessionStorage.getItem('api-token'));
              },
              success: function (data) {
                console.log("Deleted booking")
              },
              error: function (jXHR, textStatus, errorThrown) {
                console.log(errorThrown);
                console.log(textStatus);
                console.log(jXHR);
              }
            });
          }
          li.append(btn);
          $('#bookings').append(li);
        }
      },
      error: function (jXHR, textStatus, errorThrown) {
        console.log(errorThrown);
        console.log(textStatus);
        console.log(jXHR);
      }
    });
  })

  $('#acc-form').on('submit', function (e) {
    e.preventDefault();

    console.log(e.target)
    let name = e.target[0].value.toString();
    let neighbourhood_group = e.target[1].value.toString();
    let neighbourhood = e.target[2].value.toString();
    let latitude = e.target[3].value.toString();
    let longitude = e.target[4].value.toString();
    let room_type = e.target[5].value.toString();
    let minimum_nights = e.target[6].value.toString();
    let number_of_reviews = e.target[7].value.toString();
    let last_review = e.target[8].value.toString();
    let reviews_per_month = e.target[9].value.toString();
    let calculated_host_listings_count = e.target[10].value.toString();
    let availability_365 = e.target[11].value.toString();
    let price = e.target[12].value.toString();
    
    var data = {
      'name': name,
      'neighbourhood_group': neighbourhood_group,
      'neighbourhood': neighbourhood,
      'latitude': latitude,
      'longitude': longitude,
      'room_type': room_type,
      'minimum_nights': minimum_nights,
      'number_of_reviews': number_of_reviews,
      'last_review': last_review,
      'reviews_per_month': reviews_per_month,
      'calculated_host_listings_count': calculated_host_listings_count,
      'availability_365': availability_365,
      'price': price
    };
    // console.log(data);
    data = JSON.stringify(data);  
    const data_json = data;
    $.ajax({
      url: 'http://127.0.0.1:5000/accommodation',
      type: 'POST',
      contentType: 'application/json',
      beforeSend: function (xhr) {
        xhr.setRequestHeader("api-token", sessionStorage.getItem('api-token'));
      },
      data: data,
      success: function (data) {      
        // console.log(data);
      },
      error: function (jXHR, textStatus, errorThrown) {
        console.log(textStatus);
      }
    });
  });


  $('#price-form').on('submit', function (e) {
    e.preventDefault();
    let name = e.target[0].value.toString();
    let neighbourhood_group = e.target[1].value.toString();
    let neighbourhood = e.target[2].value.toString();
    let latitude = e.target[3].value.toString();
    let longitude = e.target[4].value.toString();
    let room_type = e.target[5].value.toString();
    let minimum_nights = e.target[6].value.toString();
    let availability_365 = e.target[7].value.toString();

    var data = {
      'name': name,
      'neighbourhood_group': neighbourhood_group,
      'neighbourhood': neighbourhood,
      'latitude': latitude,
      'longitude': longitude,
      'room_type': room_type,
      'minimum_nights': minimum_nights,
      'availability_365': availability_365
    };
    // console.log(data);
    data = JSON.stringify(data);  
    data_json = data;

    $.ajax({
      url: 'http://127.0.0.1:5000/priceadvice',
      type: 'PUT',
      contentType: 'application/json',
      beforeSend: function (xhr) {
        xhr.setRequestHeader("api-token", sessionStorage.getItem('api-token'));
      },
      data: data_json,
      success: function (data) {  
          // console.log(data);

        $('#price-rec').empty();
        var text = document.createElement('h4');
        text.innerText = "suggested range from "+data.price_range_lower+" to "+data.price_range_upper;    
        $('#price-rec').append(text);
      },
      error: function (jXHR, textStatus, errorThrown) {
        console.log(textStatus);
      }
    })
  })


  $('#acc-edit-form').on('submit', function (e) {
    e.preventDefault();

    // console.log(e.target)
    let id = e.target[0].value.toString();
    let name = e.target[1].value.toString();
    let neighbourhood_group = e.target[2].value.toString();
    let neighbourhood = e.target[3].value.toString();
    let latitude = e.target[4].value.toString();
    let longitude = e.target[5].value.toString();
    let room_type = e.target[6].value.toString();
    let minimum_nights = e.target[7].value.toString();
    let number_of_reviews = e.target[8].value.toString();
    let last_review = e.target[9].value.toString();
    let reviews_per_month = e.target[10].value.toString();
    let calculated_host_listings_count = e.target[11].value.toString();
    let availability_365 = e.target[12].value.toString();
    let price = e.target[13].value.toString();
    
    var data = {
      'name': name,
      'neighbourhood_group': neighbourhood_group,
      'neighbourhood': neighbourhood,
      'latitude': latitude,
      'longitude': longitude,
      'room_type': room_type,
      'minimum_nights': minimum_nights,
      'number_of_reviews': number_of_reviews,
      'last_review': last_review,
      'reviews_per_month': reviews_per_month,
      'calculated_host_listings_count': calculated_host_listings_count,
      'availability_365': availability_365,
      'price': price
    };
    // console.log(data);
    data = JSON.stringify(data);  
    data_json = data;
    $.ajax({
      url: 'http://127.0.0.1:5000/accommodation/'+id,
      type: 'PUT',
      contentType: 'application/json',
      beforeSend: function (xhr) {
        xhr.setRequestHeader("api-token", sessionStorage.getItem('api-token'));
      },
      data: data,
      success: function (data) {      
        console.log(data);
        // If success get price recommendation
        $.ajax({
          url: 'http://127.0.0.1:5000/priceadvice',
          type: 'PUT',
          contentType: 'application/json',
          beforeSend: function (xhr) {
            xhr.setRequestHeader("api-token", sessionStorage.getItem('api-token'));
          },
          data: data_json,
          success: function (data) {  
            // console.log(data);

            $('#price-rec').empty();
            var text = document.createElement('h4');
            text.innerText = "suggested range from "+data.price_range_lower+" to "+data.price_range_upper;    
            $('#price-rec').append(text);
          },
          error: function (jXHR, textStatus, errorThrown) {
            console.log(textStatus);
          }
        })
      },
      error: function (jXHR, textStatus, errorThrown) {
        console.log(textStatus);
      }
    });
  });

  $('#btn-owner').click(()=>{
    $('#owner-bookings').empty()
    $.ajax({
      url: 'http://127.0.0.1:5000/owner/bookings',
      type: 'GET',
      contentType: 'application/json',
      beforeSend: function (xhr) {
        xhr.setRequestHeader("api-token", sessionStorage.getItem('api-token'));
      },
      success: function (data) {      
        console.log(data.booking);
        if(data.message == 'No bookings found') {
          var text = document.createElement('li');
          text.innerText = 'No bookings found';
          $('#owner-bookings').append(text);
        } else {
          for(var o in data.booking) {
            var li = document.createElement('li');
            li.innerText = 'listing: '+data.booking[o].listing_id+' | owner : '+data.booking[o].owner_id+' | renter: '+data.booking[o].renter_id;
            
            var btn = document.createElement('button');
            btn.innerText = 'Delete booking';
            btn.onclick = function() {
              $.ajax({
                url: 'http://127.0.0.1:5000/owner/bookings/'+data.booking[o].listing_id,
                type: 'DELETE',
                contentType: 'application/json',
                beforeSend: function (xhr) {
                  xhr.setRequestHeader("api-token", sessionStorage.getItem('api-token'));
                },
                success: function (data) {
                  console.log("Deleted booking")
                },
                error: function (jXHR, textStatus, errorThrown) {
                  console.log(errorThrown);
                  console.log(textStatus);
                  console.log(jXHR);
                }
              });
            }
            li.append(btn);
            $('#owner-bookings').append(li);
          }
        }
      },
      error: function (jXHR, textStatus, errorThrown) {
        console.log(textStatus);
      }
    });
  });

  $('#subs-form').on('submit', function (e) {
    e.preventDefault();

    console.log(e.target)
    let id = e.target[0].value.toString();

    var data = {
      'public_id': id,
    };
    console.log(data);
    data = JSON.stringify(data);

    $.ajax({
      url: 'http://127.0.0.1:5000/subscribe/'+id,
      type: 'GET',
      contentType: 'application/json',
      beforeSend: function (xhr) {
        xhr.setRequestHeader("api-token", sessionStorage.getItem('api-token'));
      },
      data: data,
      success: function (data) {
        console.log(data);
      },
      error: function (jXHR, textStatus, errorThrown) {
        console.log(textStatus);
      }
    });
  });

  $('#unsubs-form').on('submit', function (e) {
    e.preventDefault();

    console.log(e.target)
    let id = e.target[0].value.toString();

    var data = {
      'public_id': id,
    };
    console.log(data);
    data = JSON.stringify(data);

    $.ajax({
      url: 'http://127.0.0.1:5000/unsubscribe/'+id,
      type: 'GET',
      contentType: 'application/json',
      beforeSend: function (xhr) {
        xhr.setRequestHeader("api-token", sessionStorage.getItem('api-token'));
      },
      data: data,
      success: function (data) {
        console.log(data);
      },
      error: function (jXHR, textStatus, errorThrown) {
        console.log(textStatus);
      }
    });
  });

  $('#btn-users').click(()=>{
    $.ajax({
      url: 'http://127.0.0.1:5000/userlist',
      type: 'GET',
      contentType: 'application/json',
      beforeSend: function (xhr) {
        xhr.setRequestHeader("api-token", sessionStorage.getItem('api-token'));
      },
      success: function (data) {
        $('#users-list').empty();
        console.log(data);
        for(var o in data.users) {
          var li = document.createElement('li');
          li.innerText = data.users[o].name;
          $('#users-list').append(li);
        }
      },
      error: function (jXHR, textStatus, errorThrown) {
        console.log(errorThrown);
        console.log(textStatus);
        console.log(jXHR);
      }
    });
  })

  $('#btn-stats').click(()=>{
    $.ajax({
      url: 'http://127.0.0.1:5000/statistics',
      type: 'GET',
      contentType: 'application/json',
      beforeSend: function (xhr) {
        xhr.setRequestHeader("api-token", sessionStorage.getItem('api-token'));
      },
      success: function (data) {
        $('#statistics').empty();
        console.log(data);
        for(var o in data.users) {
          var li = document.createElement('li');
          li.innerText = 'area: '+data.users[o].area+'\n'+
              'end_date : '+data.users[o].end_date+'\n'+
              'guest: '+data.users[o].guest+'\n'+
              'location: '+data.users[o].location+'\n'+
              'price_1: '+data.users[o].price_1+'\n'+
              'price_2: '+data.users[o].price_2+'\n'+
              'start_date: '+data.users[o].start_date+'\n'+
              'time: '+data.users[o].time+'\n'+
              'type_room: '+data.users[o].type_room+'\n'+
              'user_id: '+data.users[o].user_id;
          $('#statistics').append(li);
        }
      },
      error: function (jXHR, textStatus, errorThrown) {
        console.log(errorThrown);
        console.log(textStatus);
        console.log(jXHR);
      }
    });
  })

});