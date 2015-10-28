var SessionCreateCtrl  = angular.module('SessionCreateCtrl', []);
SessionCreateCtrl.controller('SessionCreateCtrl', ['$scope', '$location', 'Session', 'AuthService', 'Restangular',
    function($scope, $location, Session, AuthService, Restangular) {
    $scope.loginSubmit = function() {
        $scope.submitted = true;
        //$scope.authenticationForm.$setDirty();

        //if (!isValid) {
        //    return;
        //}
        //$scope.credentials = {
        //    'username': $scope.username,
        //    'password': $scope.password
        //}

        AuthService.login($scope.credentials).then(function(user) {
            $location.path('/')
        }, function(response) {
            $scope.failedLoginAttempt = true;
        });
    };
    //$scope.users = function(){
    //    var User = Restangular.all('users');
    //    User.getList().then(function(users){
    //        $scope.myusers = users;
    //    });
    //    var hello = 'hello'
    //
    //};
}]);