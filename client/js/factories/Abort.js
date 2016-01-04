/**
 * Created by qitian on 15-12-16.
 */
UserApp.factory('AbortPublish', function(Restangular) {
    var service;
    service = {
        stop: function(){
            return Restangular
                .one('abort')
                .customGET();
        }
    };

    return service;
});

