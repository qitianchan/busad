
/**
 * Created by qitian on 2015/10/29.
 */
(function() {
    UserApp.factory('Bus', function(Restangular) {

        var service = Restangular.service('buses');
        service.validateData = function(student) {
            // validate student data
        };

        return service;

    });

}());
