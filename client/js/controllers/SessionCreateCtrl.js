var SessionCreateCtrl  = angular.module('SessionCreateCtrl', []);
SessionCreateCtrl.controller('SessionCreateCtrl', ['$scope', '$location', 'Session', 'AuthService', 'Restangular', 'toaster',
    function($scope, $location, Session, AuthService, Restangular, toaster) {
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
            toaster.pop('error', '登录失败', '登录名或者密码错误');
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