var module = angular.module('navCtrls', []);

module.controller('NavigationCtrl', ['$scope', '$location', 
                                     function ($scope, $location) 
{
  $scope.navClass = function (page) {
    var currentRoute = $location.path().substring(1) || 'home';
    return page === currentRoute ? 'active' : '';
  };
}]);
