angular.module('securitySrv', ['commonSrvs'])
  .service('SecuritySrv', ['$rootScope', '$http', 'MessageSrv',
                           function ($rootScope, $http, MessageSrv){

    var currentUser = null;

    var srv = {};

    srv.getUser = function(force){
      
      if (!currentUser || force) {
        $http.get("/api/current_user")
          .success(function(data){
            currentUser = data;
            // set the CSRF token here
            $http.defaults.headers.post['X-CSRFToken'] = data.csrf_token;
            $http.defaults.headers.put['X-CSRFToken'] = data.csrf_token;
            // Curious group sees everything
            if ($.inArray( 'curious', currentUser.groups) >= 0){
              currentUser.admin = true;
            }
          })
          .error(function(messages){
            MessageSrv.setMessages(messages, "error");
          });
      }
      return currentUser;
    };

    srv.inGroup = function(group){
      if (!currentUser){
        return false;
      }
      return $.inArray( group, currentUser.groups) >= 0
      // Admin sees everything
        || currentUser.admin 
      // Curious group sees everything
        || $.inArray( 'curious', currentUser.groups) >= 0;
    };

    srv.login = function(username, password){
      var loginData = {"username": username, "password": password};
      $http.post("api/login/", loginData)
        .success(function(data){
          srv.getUser(true);
        })
        .error(function(messages){
          MessageSrv.setMessages(messages, "error");
        });
    };

    srv.logout = function(){
      $http.post("api/logout/", {})
        .success(function(data){
          srv.getUser(true);
        })
        .error(function(messages){
          MessageSrv.setMessages(messages, "error");
        });
    };

    srv.register = function(register){
      // var registerData = {"register": register,
      //                     "recaptcha": vcRecaptchaService.data()};

      $http.post("api/register/", register)
        .success(function(data){
          MessageSrv.setMessages("You've registered as " + register.username 
                                 + ". Please, login.", "success");
        })
        .error(function(messages){
          MessageSrv.setMessages(messages, "error");
          // In case of a failed validation you need to reload the
          // captcha because each challenge can be checked just once
          // vcRecaptchaService.reload();
        });
    };
    
    srv.getUser(true);
    return srv;
  }]);

