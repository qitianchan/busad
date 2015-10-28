UserApp.controller('SessionDestroyCtrl', function($scope, $location, AuthService) {
    AuthService.logout();
    $location.path('/sessions/create');
})