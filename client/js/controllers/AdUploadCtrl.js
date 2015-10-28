UserApp.controller('AdUploadCtrl', function($scope, User) {
    User.get().then(function(users) {
        $scope.users = users;
    });
});