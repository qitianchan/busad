/**
 * Created by qitian on 15-12-16.
 */
UserApp.factory('AbortPublish', function(Restangular) {
    var service = Restangular.service('abort');

    return service;
});