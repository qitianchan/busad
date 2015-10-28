UserApp.factory('User', function(Restangular) {
    var User;
    User = {
        create: function(user) {
            return Restangular
                .one('users')
                .customPOST(user);
        },

        get: function(user_id) {
            return Restangular
                .one('users')
                .customGET(user_id)
        }
    };
    return User;
});