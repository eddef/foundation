var module = angular.module('donationsCtrls', ['commonDirs', 'validationDirs', 
                                               'commonSrvs', 'donationsSrvs']);

module.controller('OrgCategoriesCtrl', ['$scope', '$routeParams', 'DonationsSrv', 
                                        function($scope, $routeParams, DonationsSrv)
{
  $scope.type = $routeParams.orgType ? $routeParams.orgType : 'validated';
  $scope.orderProp = 'name';

  DonationsSrv.getCategoryTree($scope.type, function(categories, org_count){
    $scope.categories_tree = categories;
    $scope.org_count = org_count;
  });
}]);

module.controller('OrgDetailCtrl', ['$rootScope', '$scope', '$routeParams', 'MessageSrv', 'DonationsSrv', 
                                    function($rootScope, $scope, $routeParams, MessageSrv, DonationsSrv)
{
  DonationsSrv.getOrganization($routeParams.orgId, function(org) {
    $scope.org = org;
    $rootScope.org = null;
  });

   $scope.validate = function() {

    var org = $scope.org;
    var callback = function(new_org) {
      $scope.org = new_org;
      var msg;
      if (org.validation_state == "validated"){
        msg = "The organization has been blocked.";
      } else if (org.validation_state == "blocked") {
        msg = "The organization is valid again.";
      } else if (org.validation_state == "candidate") {
        msg = "The organization has been validated.";
      } else {
        MessageSrv.error("Unkown validation state " + org.validation_state);
        return;
      }
      MessageSrv.success(msg);
    };
    DonationsSrv.validateOrganization(org, callback);
  };

}]);

module.controller('OrgEditCtrl', ['$rootScope', '$scope', '$routeParams', '$location', 
                                  'MessageSrv', 'DonationsSrv', 
                                  function($rootScope, $scope, $routeParams, $location, 
                                    MessageSrv, DonationsSrv)
{
  if ($routeParams.orgId) {
    // If there's an id we're editing
    $scope.is_edit = true;
    $scope.panel_tittle = "Edit Organization";
    $scope.panel_class = "warning";
    DonationsSrv.getOrganization($routeParams.orgId, function(org) {
      $scope.org = org;
    });
  } else {
    // Otherwise we're creating
    $scope.panel_tittle = "Register Organization";
    $scope.is_edit = false;
    $scope.panel_class = "success";
    $scope.org = {};
  }

  DonationsSrv.getCategories(function(categories) {
    $scope.categories = categories;
  });

  $scope.submit = function() {
    
    $scope.disableSubmit = true;

    var callback = function(org) {
      $rootScope.org = org;

      if ($routeParams.orgId) {
        MessageSrv.success({"Success: ": ["The organization has been updated."]});
      } else {
        MessageSrv.success({"Success: ": ["Organization created with id " + org.id]});
      }        
      $location.path( "/donations/detail/" + org.id );
    };

    var errorCallback = function(org) {
      $scope.disableSubmit = false;
    };

    if ($routeParams.orgId) {
      DonationsSrv.updateOrganization($scope.org, $routeParams.orgId, callback, errorCallback);
    } else {
      DonationsSrv.createOrganization($scope.org, callback, errorCallback);
    }
  };
}]);
