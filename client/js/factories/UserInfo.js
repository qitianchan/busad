/**
 * Created by qitian on 15-12-16.
 */
UserApp.factory('UserInfo', function(Restangular) {
    var service = Restangular.service('userinfo');
    service.validateData = function(student) {
        // validate student data
    };

    return service;
});