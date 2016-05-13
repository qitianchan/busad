/**
 * Created by qitian on 2015/10/29.
 */
UserApp.factory('District', function(Restangular) {
    var service = Restangular.service('districts');
    service.validateData = function() {

    };

    return service;
});